import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Boxes, Database, Plus, Trash2 } from "lucide-react";
import { useCollections } from "@/hooks/useCollections";
import { useCreateCollection } from "@/hooks/useCreateCollection";
import { useIngest } from "@/hooks/useIngest";
import { useDeleteCollection } from "@/hooks/useCollectionActions";
import { formatDate, pluralize } from "@/lib/utils";
import { validateFiles } from "@/lib/fileValidation";
import CollectionCreateDialog from "@/components/collections/CollectionCreateDialog";
import ConfirmDialog from "@/components/common/ConfirmDialog";
import EmptyState from "@/components/common/EmptyState";
import ErrorState from "@/components/common/ErrorState";
import PageHeader from "@/components/common/PageHeader";
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { toast } from "sonner";

const CollectionsPage = () => {
  const { data, isLoading, isError, error, refetch } = useCollections();
  const [createVisible, setCreateVisible] = useState(false);
  const [pendingDelete, setPendingDelete] = useState<string | null>(null);
  const navigate = useNavigate();

  const createMutation = useCreateCollection();
  const ingestMutation = useIngest();
  const deleteMutation = useDeleteCollection();

  const handleCreated = async (payload: {
    name: string;
    size?: number;
    distance?: string;
    description?: string;
    files: File[];
  }) => {
    const { files, ...collectionPayload } = payload;
    try {
      const result = await createMutation.mutateAsync(collectionPayload);
      toast.success("Коллекция создана");

      if (files.length) {
        const { valid, invalid } = validateFiles(files);
        if (invalid.length > 0) {
          toast.warning(`${invalid.length} ${pluralize(invalid.length, "файл не подходит", "файла не подходят", "файлов не подходят")} для загрузки и будет пропущено`);
        }
        if (valid.length) {
        try {
          const ingestResult = await ingestMutation.mutateAsync({
            collectionId: result.id,
            files: valid,
          });
          toast.success(
            `${ingestResult.count} ${pluralize(ingestResult.count, "файл", "файла", "файлов")} отправлены на обработку`
          );
        } catch {
          toast.error("Коллекция создана, но загрузить документы не удалось.");
        }
        }
      }

      setCreateVisible(false);
      navigate(`/collections/${result.id}`);
    } catch (error) {
      const message =
        error && typeof error === "object" && "message" in error && typeof error.message === "string"
          ? error.message
          : "Не удалось создать коллекцию";
      toast.error(message);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <PageHeader eyebrow="Знания компании" title="Базы знаний" />
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[0, 1, 2, 3, 4, 5].map((i) => (
            <Skeleton key={i} className="h-40 rounded-2xl" />
          ))}
        </div>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="space-y-6">
        <PageHeader eyebrow="Знания компании" title="Базы знаний" />
        <ErrorState error={error} message="Не удалось загрузить коллекции" onRetry={() => refetch()} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <PageHeader
        eyebrow="Знания компании"
        title="Базы знаний"
        description={
          data && data.length > 0
            ? `${data.length} ${pluralize(data.length, "коллекция", "коллекции", "коллекций")}`
            : undefined
        }
        actions={
          <Button onClick={() => setCreateVisible(true)}>
            <Plus className="h-4 w-4" aria-hidden="true" />
            Создать коллекцию
          </Button>
        }
      />

      {!data || data.length === 0 ? (
        <EmptyState
          icon={Boxes}
          title="Коллекций пока нет"
          description="Создайте первую базу знаний: задайте название, при желании добавьте описание и сразу загрузите документы."
          action={
            <Button onClick={() => setCreateVisible(true)}>
              <Plus className="h-4 w-4" aria-hidden="true" />
              Создать первую коллекцию
            </Button>
          }
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {data.map((collection) => (
            <article
              key={collection.id}
              className="group relative flex flex-col gap-3 rounded-2xl border border-border bg-card p-5 shadow-[0_1px_12px_rgba(10,17,32,0.06)] transition-all duration-300 hover:-translate-y-0.5 hover:border-accent-200 hover:shadow-lg hover:shadow-slate-900/[0.06]"
            >
              <div className="flex items-start justify-between gap-3">
                <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent-50 text-accent-600 transition-colors group-hover:bg-accent-600 group-hover:text-white">
                  <Database className="h-5 w-5" aria-hidden="true" />
                </span>
                <Button
                  variant="ghost"
                  size="icon-sm"
                  className="relative z-20 text-slate-400 transition-opacity focus-visible:opacity-100 hover:text-red-600 md:opacity-0 md:group-hover:opacity-100"
                  onClick={() => setPendingDelete(collection.id)}
                  aria-label={`Удалить коллекцию ${collection.name}`}
                >
                  <Trash2 className="h-4 w-4" aria-hidden="true" />
                </Button>
              </div>

              <div className="min-w-0">
                <h3 className="truncate text-[15px] font-semibold text-slate-900 group-hover:text-accent-700">
                  {collection.name}
                </h3>
                <p className="mt-1 line-clamp-2 min-h-10 text-sm leading-relaxed text-muted-foreground">
                  {collection.description || "Описание не указано"}
                </p>
              </div>

              <div className="mt-auto flex flex-wrap items-center gap-1.5 border-t border-slate-100 pt-3">
                {collection.distance && (
                  <Badge variant="outline" className="text-[10px]">
                    {collection.distance}
                  </Badge>
                )}
                {collection.size && (
                  <Badge variant="outline" className="font-mono text-[10px]">
                    {collection.size} dim
                  </Badge>
                )}
                <span className="ml-auto text-[11px] text-slate-400">{formatDate(collection.created_at)}</span>
              </div>

              <Link
                to={`/collections/${collection.id}`}
                className="absolute inset-0 z-0 rounded-2xl"
                aria-label={`Открыть коллекцию ${collection.name}`}
              />
            </article>
          ))}
        </div>
      )}

      <CollectionCreateDialog
        open={createVisible}
        loading={createMutation.isPending || ingestMutation.isPending}
        onClose={() => setCreateVisible(false)}
        onSubmit={(payload) => void handleCreated(payload)}
      />

      <ConfirmDialog
        open={Boolean(pendingDelete)}
        title="Удалить коллекцию?"
        description="Коллекция, её документы, индексы и исходные файлы будут удалены безвозвратно."
        confirmLabel="Удалить"
        onCancel={() => setPendingDelete(null)}
        onConfirm={() => {
          if (!pendingDelete) return;
          const target = pendingDelete;
          deleteMutation.mutate(target, {
            onSuccess: () => {
              toast.success("Коллекция удалена");
              setPendingDelete(null);
            },
            onError: (mutationError) => {
              const message =
                mutationError && typeof mutationError === "object" && "message" in mutationError
                  ? String(mutationError.message)
                  : "Не удалось удалить коллекцию";
              toast.error(message);
              setPendingDelete(null);
            },
          });
        }}
        loading={deleteMutation.isPending}
      />
    </div>
  );
};

export default CollectionsPage;
