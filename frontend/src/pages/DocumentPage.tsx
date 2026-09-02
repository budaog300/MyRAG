import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useDocument } from "@/hooks/useDocument";
import ConfirmDialog from "@/components/common/ConfirmDialog";
import Spinner from "@/components/ui/Spinner";
import { formatDate } from "@/lib/utils";
import { toast } from "sonner";

const DocumentPage = () => {
  const { collectionId, documentId } = useParams<{
    collectionId: string;
    documentId: string;
  }>();
  const { query, deleteMutation } = useDocument(collectionId, documentId);
  const [pendingDelete, setPendingDelete] = useState<string | null>(null);
  const navigate = useNavigate();

  if (!collectionId || !documentId) {
    return null;
  }

  if (query.isLoading) {
    return (
      <div className="rounded-2xl border border-border bg-card p-6 shadow-xl">
        <Spinner />
      </div>
    );
  }

  if (query.isError) {
    return (
      <div className="rounded-2xl border border-border bg-card p-6 shadow-xl">
        <p className="text-sm text-muted-foreground">Не удалось загрузить документ.</p>
      </div>
    );
  }

  const document = query.data;
  if (!document) {
    return <p>Документ не найден.</p>;
  }

  return (
    <div className="space-y-6">
      <header className="rounded-2xl border border-border bg-card p-6 shadow-xl">
        <p className="text-xs uppercase tracking-[0.4em] text-accent">
          Информация о документе
        </p>

        <div className="mt-3">
          <h2 className="text-2xl font-semibold text-foreground">
            {document.filename || documentId}
          </h2>

          <p className="mt-1 text-xs text-muted-foreground">
            ID: {documentId}
          </p>
        </div>

        <div className="mt-5">
          <button
            type="button"
            className="rounded-full border border-border px-4 py-2 text-sm font-semibold text-destructive"
            onClick={() => setPendingDelete(documentId)}
            disabled={deleteMutation.isPending}
          >
            Удалить документ
          </button>
        </div>
      </header>
      <section className="rounded-2xl border border-border bg-card p-6 shadow-xl">
        <h3 className="text-sm font-semibold text-foreground">
          Свойства документа
        </h3>
        <div className="mt-4 space-y-3">
          <p className="text-sm text-muted-foreground">Статус: {document.status}</p>
          <p className="text-sm text-muted-foreground">MIME: {document.mime_type || "не указано"}</p>
          <p className="text-sm text-muted-foreground">Размер: {document.size_bytes} B</p>
          <p className="text-sm text-muted-foreground">Создан: {formatDate(document.created_at)}</p>
        </div>
        {document.error_message && (
          <p className="mt-3 text-sm text-rose-400">Ошибка: {document.error_message}</p>
        )}
      </section>

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Удалить документ?"
        description="Документ будет удалён из коллекции и все чанки также удалятся."
        onCancel={() => setPendingDelete(null)}
        onConfirm={() => {
          if (!pendingDelete) {
            return;
          }
          deleteMutation.mutate(
            { documentId: pendingDelete },
            {
              onSuccess: () => {
                toast.success("Документ удалён");
                navigate(`/collections/${collectionId}/documents`);
              },
              onError: () => {
                toast.error("Не удалось удалить документ");
                setPendingDelete(null);
              },
            },
          );
        }}
        loading={deleteMutation.isPending}
      />
    </div>
  );
};

export default DocumentPage;
