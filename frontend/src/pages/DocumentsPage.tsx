import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useDocuments } from "@/hooks/useDocuments";
import { useIngest } from "@/hooks/useIngest";
import { usePagination } from "@/hooks/usePagination";
import { formatDate } from "@/lib/utils";
import FilePicker from "@/components/documents/FilePicker";
import Pagination from "@/components/common/Pagination";
import ConfirmDialog from "@/components/common/ConfirmDialog";
import Spinner from "@/components/ui/Spinner";
import { toast } from "sonner";

const statusLabel = (status: string) => {
  const map: Record<string, string> = {
    pending: "text-amber-300",
    processing: "text-sky-300",
    ready: "text-emerald-400",
    failed: "text-rose-400",
    deleted: "text-muted-foreground",
  };
  return map[status] ?? "text-muted-foreground";
};

const DocumentsPage = () => {
  const { collectionId } = useParams<{ collectionId: string }>();
  const { pagination, setPage, setSize } = usePagination();
  const { page, size } = pagination;
  const { query, deleteMutation } = useDocuments({ collectionId: collectionId ?? "", page, size });
  const ingestMutation = useIngest();
  const [files, setFiles] = useState<File[]>([]);
  const [pendingDelete, setPendingDelete] = useState<string | null>(null);
  const navigate = useNavigate();

  if (!collectionId) {
    return null;
  }

  const handleUpload = async () => {
    if (!files.length) {
      return;
    }

    try {
      await ingestMutation.mutateAsync({
        collectionId,
        files,
      });
      toast.success(`${files.length} документов отправлены на обработку`);
      setFiles([]);
    } catch (error) {
      toast.error("Не удалось отправить документы");
    }
  };

  const items = query.data?.items ?? [];
  const total = query.data?.total ?? 0;

  return (
    <div className="space-y-6">
      <div className="rounded-2xl border border-border bg-card p-6 shadow-xl">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <h3 className="text-lg font-semibold">Documents</h3>
          <div className="flex items-center gap-2 text-sm text-muted-foreground">
            <span>Выбрано файлов: {files.length}</span>
            <button
              className="rounded-full border border-border px-3 py-1 text-xs font-semibold text-secondary"
              onClick={handleUpload}
              disabled={!files.length || ingestMutation.isPending}
            >
              {ingestMutation.isPending ? "Загрузка..." : "Загрузить"}
            </button>
          </div>
        </div>
        <FilePicker files={files} onFilesChange={setFiles} disabled={ingestMutation.isPending} />
      </div>

      <div className="rounded-2xl border border-border bg-card p-4 shadow-xl">
        {query.isLoading && (
          <div className="py-10 text-center">
            <Spinner />
          </div>
        )}
        {query.isError && (
          <div className="space-y-3 text-center text-sm text-muted-foreground">
            <p>Не удалось загрузить документы.</p>
            <button className="text-secondary" onClick={() => query.refetch()}>
              Повторить
            </button>
          </div>
        )}
        {!query.isLoading && !query.isError && items.length === 0 && (
          <p className="py-10 text-center text-sm text-muted-foreground">Документы не загружены.</p>
        )}

        {!query.isLoading && !query.isError && items.length > 0 && (
          <div className="overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead>
                <tr>
                  <th className="px-3 py-2 text-xs uppercase tracking-[0.3em] text-muted-foreground">Имя файла</th>
                  <th className="px-3 py-2 text-xs uppercase tracking-[0.3em] text-muted-foreground">Дата загрузки</th>
                  <th className="px-3 py-2 text-xs uppercase tracking-[0.3em] text-muted-foreground">Статус</th>
                  <th className="px-3 py-2 text-xs uppercase tracking-[0.3em] text-muted-foreground">Действия</th>
                </tr>
              </thead>
              <tbody>
                {items.map((document) => (
                  <tr
                    key={document.id}
                    className="border-t border-border transition hover:bg-muted/10"
                  >
                    <td
                      className="cursor-pointer px-3 py-3 text-foreground"
                      onClick={() => navigate(`/collections/${collectionId}/documents/${document.id}`)}
                    >
                      {document.filename || "Без имени"}
                    </td>
                    <td className="px-3 py-3 text-muted-foreground">
                      {formatDate(document.created_at)}
                    </td>
                    <td className={`px-3 py-3 text-sm font-semibold ${statusLabel(document.status)}`}>
                      {document.status}
                    </td>
                    <td className="px-3 py-3">
                      <button
                        type="button"
                        className="rounded-full border border-border px-3 py-1 text-[11px] font-semibold text-destructive"
                        onClick={() => setPendingDelete(document.id)}
                      >
                        Удалить
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <Pagination
          page={page}
          size={size}
          total={total}
          onPageChange={setPage}
          onSizeChange={setSize}
        />
      </div>

        <ConfirmDialog
          open={Boolean(pendingDelete)}
          title="Удалить документ?"
          description="Документ будет удалён из коллекции и все чанки также удалятся."
          onCancel={() => setPendingDelete(null)}
          onConfirm={() => {
            if (!collectionId || !pendingDelete) {
              return;
            }
            deleteMutation.mutate({ documentId: pendingDelete });
            setPendingDelete(null);
          }}
          loading={deleteMutation.isPending}
        />
    </div>
  );
};

export default DocumentsPage;
