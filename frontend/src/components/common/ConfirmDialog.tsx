import { useEffect, useRef } from "react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from "@/components/ui/alert-dialog";

interface ConfirmDialogProps {
  open: boolean;
  title: string;
  description: string;
  confirmLabel?: string;
  cancelLabel?: string;
  onConfirm: () => void;
  onCancel: () => void;
  loading?: boolean;
  destructive?: boolean;
}

const ConfirmDialog = ({
  open,
  title,
  description,
  confirmLabel = "Подтвердить",
  cancelLabel = "Отмена",
  onConfirm,
  onCancel,
  loading,
  destructive = true,
}: ConfirmDialogProps) => {
  const contentRef = useRef<HTMLDivElement | null>(null);

  // Radix AlertDialog не поддерживает закрытие по клику вне окна —
  // реализуем его вручную (во время loading клики игнорируются).
  useEffect(() => {
    if (!open) return;

    const handlePointerDown = (event: PointerEvent) => {
      if (loading) return;
      const content = contentRef.current;
      if (content && event.target instanceof Node && !content.contains(event.target)) {
        onCancel();
      }
    };

    document.addEventListener("pointerdown", handlePointerDown);
    return () => document.removeEventListener("pointerdown", handlePointerDown);
  }, [open, loading, onCancel]);

  return (
    <AlertDialog
      open={open}
      onOpenChange={(next) => {
        if (!next && !loading) {
          onCancel();
        }
      }}
    >
      <AlertDialogContent ref={contentRef}>
        <AlertDialogHeader>
          <AlertDialogTitle>{title}</AlertDialogTitle>
          <AlertDialogDescription>{description}</AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel disabled={loading}>{cancelLabel}</AlertDialogCancel>
          <AlertDialogAction
            disabled={loading}
            className={!destructive ? "bg-primary text-primary-foreground hover:bg-accent-700" : undefined}
            onClick={(event) => {
              event.preventDefault();
              onConfirm();
            }}
          >
            {loading ? "Выполняется…" : confirmLabel}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
};

export default ConfirmDialog;
