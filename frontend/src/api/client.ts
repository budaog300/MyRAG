import axios from "axios";
import type { ApiErrorPayload, ApiErrorResponse } from "@/types/api";

const baseURL = import.meta.env.VITE_API_URL ?? "http://localhost:8000/api/v1";

const client = axios.create({
  baseURL,
  timeout: 15_000,
});

export const normalizeError = (error: unknown): ApiErrorPayload => {
  if (axios.isAxiosError<ApiErrorResponse>(error)) {
    const status = error.response?.status ?? 500;
    const detail = error.response?.data?.detail;
    const extra = error.response?.data?.extra;
    const message = (() => {
      if (status === 422) {
        return detail ?? "Ошибка валидации данных";
      }
      if (status === 404) {
        return detail ?? "Не найден ресурс";
      }
      if (status === 400) {
        return detail ?? "Некорректный запрос";
      }
      if (status === 500) {
        return detail ?? "Внутренняя ошибка сервера";
      }
      return detail ?? "Неизвестная ошибка";
    })();

    return { status, message, detail, extra };
  }

  if (error instanceof Error) {
    return {
      status: 0,
      message: error.message,
    };
  }

  return {
    status: 0,
    message: "Неизвестная ошибка",
  };
};

client.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!axios.isAxiosError(error)) {
      return Promise.reject(error);
    }
    const payload = normalizeError(error);
    return Promise.reject(payload);
  }
);

export default client;
