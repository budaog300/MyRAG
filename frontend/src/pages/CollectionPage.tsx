import { useState } from "react";
import { NavLink, Outlet, useNavigate, useParams } from "react-router-dom";
import Spinner from "@/components/ui/Spinner";
import { toast } from "sonner";
import { useQueryClient } from "@tanstack/react-query";
import { useCollection } from "@/hooks/useCollection";
import { useDeleteCollection, useUpdateCollection, useClearCollection } from "@/hooks/useCollectionActions";
import ConfirmDialog from "@/components/common/ConfirmDialog";
import CollectionUpdateDialog from "@/components/collections/CollectionUpdateDialog";
import InfoTooltip from "@/components/ui/InfoTooltip";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";

const CollectionPage = () => {
  const client = useQueryClient();
  const [isDeleting, setIsDeleting] = useState(false);
  const { collectionId } = useParams<{ collectionId: string }>();
  const { query } = useCollection(isDeleting ? undefined : collectionId);
  const clearMutation = useClearCollection();
  const deleteMutation = useDeleteCollection();
  const updateMutation = useUpdateCollection();
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [isClearOpen, setIsClearOpen] = useState(false);
  const [isEditOpen, setIsEditOpen] = useState(false);
  const navigate = useNavigate();

  if (!collectionId) {
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
        <p className="text-sm text-muted-foreground">Не удалось загрузить данные коллекции.</p>
        <button
          className="mt-3 text-sm font-semibold text-secondary"
          onClick={() => query.refetch()}
        >
          Повторить
        </button>
      </div>
    );
  }

  const collection = query.data;
  if (!collection) {
    return null;
  }

  const handleUpdate = (payload: UpdateCollectionPayload) => {
    if (!collectionId) {
      return;
    }

    updateMutation.mutate(
      {
        collectionId,
        payload,
      },
      {
        onSuccess: () => {
          setIsEditOpen(false);
        },
      },
    );
  };

  const handleDelete = async () => {
    try {
      setIsDeleting(true);

      await deleteMutation.mutateAsync(collectionId);

      await client.invalidateQueries({
        queryKey: ["collections"],
        exact: true,
      });

      navigate("/collections", { replace: true });

      toast.success("Коллекция удалена");
    } catch {
      setIsDeleting(false);
      toast.error("Не удалось удалить коллекцию");
    }
  };

  const handleClear = () => {
    clearMutation.mutate(collectionId, {
      onSuccess: () => {
        toast.success("Коллекция очищена");
      },
      onError: () => {
        toast.error("Не удалось очистить коллекцию");
      },
    });
  };

  return (
    <section className="space-y-6">
      <header className="flex flex-col gap-3 border-b border-border pb-4 md:flex-row md:items-center md:justify-between">
        <div className="min-w-0">
          <p className="text-xs uppercase tracking-[0.4em] text-accent">Коллекция</p>
          <div className="mt-1 flex items-center gap-2">
            <h2 className="mt-1 text-3xl font-semibold text-foreground">{collection.name}</h2>
            <Popover>
              <PopoverTrigger asChild>
                <button
                  type="button"
                  className="inline-flex h-5 w-5 items-center justify-center rounded-full border border-border text-xs text-muted-foreground hover:text-foreground"
                >
                  ?
                </button>
              </PopoverTrigger>

              <PopoverContent className="w-100 bg-black text-sm leading-relaxed text-foreground text-justify">
                {collection.description || "Описание отсутствует"}
              </PopoverContent>
            </Popover>
          </div>
          <p className="mt-2 text-[10px] uppercase tracking-[0.5em] text-muted-foreground">ID: {collection.id}</p>
        </div>
        <div className="flex flex-wrap gap-3">
          <button
            className="rounded-full border border-border px-4 py-2 text-sm font-semibold text-muted-foreground hover:bg-muted"
            onClick={() => setIsEditOpen(true)}
          >
            Изменить
          </button>
          <button
            className="rounded-full border border-border px-4 py-2 text-sm font-semibold text-muted-foreground"
            onClick={() => setIsClearOpen(true)}
            disabled={clearMutation.isPending}
          >
            Очистить
          </button>
          <button
            className="rounded-full bg-destructive px-4 py-2 text-sm font-semibold text-destructive-foreground"
            onClick={() => setIsDeleteOpen(true)}
            disabled={deleteMutation.isPending}
          >
            Удалить коллекцию
          </button>
        </div>
      </header>

      <details className="rounded-2xl border border-border bg-card p-4 shadow-lg">
        <summary className="cursor-pointer text-sm font-semibold text-accent">
          <span className="inline-flex items-center gap-1.5">
            <span>Источники данных</span>
            <InfoTooltip text="Информация о хранилищах, которые используются для поиска документов в этой коллекции." />
          </span>
        </summary>
        <div className="mt-3 grid gap-4 md:grid-cols-2">
          <article className="space-y-1 rounded-2xl border border-border bg-muted/10 p-3">
            <h3 className="flex items-center gap-1 text-xs uppercase text-muted-foreground">
              <span className="tracking-[0.4em]">
                Векторное хранилище
              </span>
              <InfoTooltip text="Хранилище векторных представлений документов. Используется для поиска фрагментов по смысловой близости." />
            </h3>
            <p className="text-sm text-muted-foreground">Размер вектора: {collection.vector_repo_info.size}</p>
            <p className="text-sm text-muted-foreground">Метрика расстояния: {collection.vector_repo_info.distance}</p>
            <p className="text-sm text-muted-foreground">Количество фрагментов: {collection.vector_repo_info.points_count}</p>
          </article>
          <article className="space-y-1 rounded-2xl border border-border bg-muted/10 p-3">
            <h3 className="flex items-center gap-1 text-xs uppercase text-muted-foreground">
              <span className="tracking-[0.4em]">
                Текстовое хранилище
              </span>
              <InfoTooltip text="Хранилище текстовых данных. Используется для поиска фрагментов по совпадениям в тексте." />
            </h3>
            <p className="text-sm text-muted-foreground">Количество фрагментов: {collection.keyword_repo_info.points_count}</p>
          </article>
        </div>
      </details>

      <nav className="flex gap-2 border-b border-border pb-3">
        <NavLink
          to="."
          end
          className={({ isActive }) =>
            `rounded-full px-4 py-2 text-sm font-semibold ${isActive ? "bg-secondary text-secondary-foreground" : "text-muted-foreground"
            }`}
        >
          Чат
        </NavLink>
        <NavLink
          to="documents"
          className={({ isActive }) =>
            `rounded-full px-4 py-2 text-sm font-semibold ${isActive ? "bg-secondary text-secondary-foreground" : "text-muted-foreground"
            }`}
        >
          Документы
        </NavLink>
      </nav>

      <div className="rounded-3xl border border-border bg-card p-4 shadow-xl">
        <Outlet />
      </div>

      <ConfirmDialog
        open={isClearOpen}
        title="Очистить коллекцию?"
        description="Все исходные файлы будут удалены, но сама коллекция останется."
        onCancel={() => setIsClearOpen(false)}
        onConfirm={() => {
          setIsClearOpen(false);
          handleClear();
        }}
        loading={clearMutation.isPending}
      />
      <ConfirmDialog
        open={isDeleteOpen}
        title="Удалить коллекцию?"
        description="Коллекция, индексы, документы и исходные файлы будут удалены."
        onCancel={() => setIsDeleteOpen(false)}
        onConfirm={() => {
          setIsDeleteOpen(false);
          handleDelete();
        }}
        loading={deleteMutation.isPending}
      />
      <CollectionUpdateDialog
        open={isEditOpen}
        loading={updateMutation.isPending}
        collection={query.data!}
        onClose={() => setIsEditOpen(false)}
        onSubmit={handleUpdate}
      />
    </section>
  );
};

export default CollectionPage;
