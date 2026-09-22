import axios from "axios";
import type { ApiErrorPayload } from "@/types/api";

const baseURL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

const client = axios.create({
  baseURL,
  timeout: 15_000,
});

const FALLBACK_MESSAGES: Record<number, string> = {
  400: "Некорректный запрос",
  401: "Доступ запрещён. Требуется авторизация",
  403: "Недостаточно прав для выполнения операции",
  404: "Ресурс не найден",
  409: "Конфликт данных",
  415: "Неподдерживаемый формат данных",
  422: "Ошибка валидации данных",
  500: "Внутренняя ошибка сервера. Обратитесь к администратору",
  502: "Сервис недоступен. Попробуйте позже",
  503: "Сервис временно недоступен",
};

interface PydanticErrorItem {
  loc?: (string | number)[];
  msg?: string;
}

/** Извлекает человекочитаемое сообщение из ответа backend. */
const extractMessage = (
  status: number,
  detail: unknown,
): string | undefined => {
  // Backend возвращает {"detail": "текст"} для доменных ошибок.
  if (typeof detail === "string" && detail.trim()) {
    return detail;
  }

  // FastAPI возвращает {"detail": [{loc, msg}]} для ошибок валидации.
  if (Array.isArray(detail) && detail.length > 0) {
    const items = detail as PydanticErrorItem[];
    const parts = items
      .map((item) => {
        const field = item.loc
          ?.filter((part) => typeof part === "string" && part !== "body")
          .join(".");
        return field ? `${field}: ${item.msg ?? "некорректное значение"}` : (item.msg ?? undefined);
      })
      .filter((part): part is string => Boolean(part));
    if (parts.length > 0) {
      return parts.slice(0, 3).join("; ");
    }
  }

  return FALLBACK_MESSAGES[status];
};

export const normalizeError = (error: unknown): ApiErrorPayload => {
  if (axios.isAxiosError(error)) {
    if (axios.isCancel(error)) {
      return { status: 0, message: "Запрос отменён" };
    }

    const status = error.response?.status ?? 0;

    // Нет ответа от сервера: сеть, таймаут, DNS.
    if (!error.response) {
      const isTimeout = error.code === "ECONNABORTED";
      return {
        status: 0,
        message: isTimeout
          ? "Превышено время ожидания ответа сервера"
          : "Нет соединения с сервером. Проверьте подключение",
      };
    }

    const detail = error.response.data?.detail;
    return {
      status,
      message: extractMessage(status, detail) ?? "Неизвестная ошибка",
      detail: typeof detail === "string" ? detail : undefined,
      extra: error.response.data?.extra,
    };
  }

  if (error instanceof Error) {
    return { status: 0, message: error.message };
  }

  return { status: 0, message: "Неизвестная ошибка" };
};

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!axios.isAxiosError(error)) {
      return Promise.reject(error);
    }
    return Promise.reject(normalizeError(error));
  }
);

export default client;
