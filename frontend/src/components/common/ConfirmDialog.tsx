import { useEffect } from "react";

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  loading?: boolean;
}

const ConfirmDialog = ({
  open,
  title,
  description,
  confirmLabel = "Подтвердить",
  cancelLabel = "Отмена",
  onCancel,
  onConfirm,
  loading,
}: ConfirmDialogProps) => {
  useEffect(() => {
    if (!open) {
      document.body.style.overflow = "";
      return;
    }
    document.body.style.overflow = "hidden";
    return () => {
      document.body.style.overflow = "";
    };
  }, [open]);

  if (!open) {
    return null;
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
      onClick={onCancel}
    >
      <section
        className="w-full max-w-md space-y-4 rounded-2xl border border-border bg-black p-6 shadow-2xl"
        onClick={(event) => event.stopPropagation()}
      >
        <header>
          <h3 className="text-lg font-semibold text-foreground">{title}</h3>
          <p className="text-sm text-muted-foreground">{description}</p>
        </header>
        <div className="flex justify-end gap-3">
          <button
            className="rounded-full border border-border px-4 py-1 text-sm font-medium text-muted-foreground transition hover:border-primary"
            onClick={onCancel}
            disabled={loading}
          >
            {cancelLabel}
          </button>
          <button
            className="rounded-full bg-destructive px-4 py-1 text-sm font-semibold text-white transition hover:bg-destructive/90 disabled:opacity-50"
            onClick={onConfirm}
            disabled={loading}
          >
            {loading ? "Удаление..." : confirmLabel}
          </button>
        </div>
      </section>
    </div>
  );
};

export default ConfirmDialog;
