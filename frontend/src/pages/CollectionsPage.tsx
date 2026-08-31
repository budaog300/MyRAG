import { Link, useNavigate } from "react-router-dom";
import { useState } from "react";
import { pluralize } from "@/lib/utils";
import { useCollections } from "@/hooks/useCollections";
import { useCreateCollection } from "@/hooks/useCreateCollection";
import { useIngest } from "@/hooks/useIngest";
import { useDeleteCollection } from "@/hooks/useCollectionActions";
import ConfirmDialog from "@/components/common/ConfirmDialog";
import CollectionCreateDialog from "@/components/collections/CollectionCreateDialog";
import Spinner from "@/components/ui/Spinner";
import { toast } from "sonner";

const CollectionsPage = () => {
  const { data, isLoading, isError, refetch } = useCollections();
  const [createVisible, setCreateVisible] = useState(false);
  const navigate = useNavigate();

  const createMutation = useCreateCollection();
  const ingestMutation = useIngest();
  const deleteMutation = useDeleteCollection();
  const [pendingDelete, setPendingDelete] = useState<string | null>(null);

  const handleCreate = () => {
    setCreateVisible(true);
  };

  const handleCreated = async (payload: {
    name: string
    size?: number
    distance?: string
    description?: string
    files: File[]
  }) => {
    const { files, ...collectionPayload } = payload;
    try {
      const result = await createMutation.mutateAsync(collectionPayload);
      toast.success("Коллекция создана");

      if (files.length) {
        try {
          const ingestResult = await ingestMutation.mutateAsync({
            collectionId: result.id,
            files,
          });
          toast.success(
            `${ingestResult.count} ${pluralize(ingestResult.count, "файл", "файла", "файлов")} успешно отправлены на обработку`,
          );
        } catch (ingestError) {
          toast.error("Коллекция создана, но загрузить документы не удалось.");
        }
      }

      navigate(`/collections/${result.id}`);
    } catch (error) {
      toast.error("Не удалось создать коллекцию");
    }
  };

  if (isLoading) {
    return (
      <div className="rounded-2xl border border-border bg-card p-6 shadow-xl">
        <Spinner />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="rounded-2xl border border-border bg-card p-6 shadow-xl">
        <p className="text-sm text-muted-foreground">Не удалось загрузить коллекции.</p>
        <button className="mt-3 text-sm font-semibold text-secondary" onClick={() => refetch()}>
          Повторить
        </button>
      </div>
    );
  }

  if (!data || data.length === 0) {
    return (
      <div className="space-y-4 rounded-2xl border border-border bg-card p-6 text-center text-muted-foreground shadow-xl">
        <p>Коллекций пока нет.</p>
        <button className="rounded-full bg-secondary px-4 py-2 text-sm font-semibold text-secondary-foreground" onClick={handleCreate}>
          + Создать коллекцию
        </button>
      </div>
    );
  }

  return (
    <section className="space-y-6">
      <header className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold">Коллекции</h2>
        <button className="rounded-full border border-border px-4 py-2 text-sm font-semibold text-secondary" onClick={handleCreate}>
          + Создать коллекцию
        </button>
      </header>
      <div className="rounded-2xl border border-border bg-card p-4 shadow-xl">
        <table className="w-full text-left text-sm">
          <thead>
            <tr>
              <th className="px-3 py-2 font-semibold text-muted-foreground">Название</th>
              <th className="px-3 py-2 font-semibold text-muted-foreground">Действия</th>
            </tr>
          </thead>
          <tbody>
            {data.map((collection) => (
              <tr key={collection.id} className="border-t border-border">
                <td className="px-3 py-3 text-foreground">
                  <Link to={`/collections/${collection.id}`} className="text-secondary">
                    {collection.name}
                  </Link>
                </td>
                <td className="px-3 py-3 space-x-2">
                  <button
                    className="rounded-full border border-border px-3 py-1 text-xs font-semibold text-muted-foreground"
                    onClick={() => navigate(`/collections/${collection.id}`)}
                  >
                    Перейти
                  </button>
                  <button
                    className="rounded-full border border-border px-3 py-1 text-xs font-semibold text-destructive"
                    onClick={() => setPendingDelete(collection.id)}
                  >
                    Удалить
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
        <CollectionCreateDialog
          open={createVisible}
          loading={createMutation.isPending || ingestMutation.isPending}
          onClose={() => setCreateVisible(false)}
          onSubmit={(payload) => {
            setCreateVisible(false);
            handleCreated(payload);
          }}
        />
        <ConfirmDialog
          open={Boolean(pendingDelete)}
          title="Удалить коллекцию?"
          description="Все документы, чанки и связанные исходные файлы будут удалены."
          onCancel={() => setPendingDelete(null)}
          onConfirm={() => {
            if (!pendingDelete) {
              return;
            }
            deleteMutation.mutate(pendingDelete, {
              onSuccess: () => {
                toast.success("Коллекция удалена");
                setPendingDelete(null);
              },
              onError: () => {
                toast.error("Не удалось удалить коллекцию");
                setPendingDelete(null);
              },
            });
          }}
          loading={deleteMutation.isPending}
        />
    </section>
  );
};

export default CollectionsPage;
