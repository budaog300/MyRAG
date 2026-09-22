import type { Badge } from "@/components/ui/badge";
import type { DocumentRecord } from "@/types/document";

type BadgeVariant = React.ComponentProps<typeof Badge>["variant"];

export const DOCUMENT_STATUS_LABEL: Record<DocumentRecord["status"], string> = {
  pending: "В очереди",
  processing: "Обрабатывается",
  ready: "Готов",
  failed: "Ошибка",
  deleted: "Удалён",
  deleting: "Удаляется",
};

export const DOCUMENT_STATUS_VARIANT: Record<DocumentRecord["status"], BadgeVariant> = {
  pending: "warning",
  processing: "info",
  ready: "success",
  failed: "destructive",
  deleted: "secondary",
  deleting: "warning",
};

/** Показывает, что документ ещё обрабатывается (для пустых состояний/подсказок). */
export const isProcessingStatus = (status: DocumentRecord["status"]): boolean =>
  status === "pending" || status === "processing";
