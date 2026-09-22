import type { ReactNode } from "react";
import { AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import type { ApiErrorPayload } from "@/types/api";

interface ErrorStateProps {
  error?: ApiErrorPayload | Error | null;
  message?: string;
  onRetry?: () => void;
  children?: ReactNode;
}

const getErrorMessage = (error: ErrorStateProps["error"]): string | null => {
  if (!error) {
    return null;
  }
  if ("message" in error && typeof error.message === "string") {
    return error.message;
  }
  return null;
};

const ErrorState = ({ error, message, onRetry, children }: ErrorStateProps) => {
  const detail = getErrorMessage(error);
  const fallback = message ?? "Не удалось загрузить данные";

  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-2xl border border-red-200 bg-red-50/60 px-6 py-10 text-center">
      <span className="flex h-12 w-12 items-center justify-center rounded-xl bg-red-100 text-red-600">
        <AlertCircle className="h-5 w-5" aria-hidden="true" />
      </span>
      <div className="space-y-1">
        <p className="text-[15px] font-semibold text-red-800">{fallback}</p>
        {detail && (
          <p className="mx-auto max-w-md text-sm leading-relaxed text-red-700/90">{detail}</p>
        )}
      </div>
      {onRetry && (
        <Button variant="destructive-outline" size="sm" onClick={onRetry} className="mt-1">
          <RefreshCw className="h-3.5 w-3.5" aria-hidden="true" />
          Повторить
        </Button>
      )}
      {children}
    </div>
  );
};

export default ErrorState;
