import { useState } from "react";
import { NavLink, Outlet, useNavigate, useParams } from "react-router-dom";
import { useCollection } from "@/hooks/useCollection";
import ConfirmDialog from "@/components/common/ConfirmDialog";
import Spinner from "@/components/ui/Spinner";
import { toast } from "sonner";

const CollectionPage = () => {
  const { collectionId } = useParams<{ collectionId: string }>();
  const { query, deleteMutation, clearMutation } = useCollection(collectionId);
  const [isDeleteOpen, setIsDeleteOpen] = useState(false);
  const [isClearOpen, setIsClearOpen] = useState(false);
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

  const handleDelete = () => {
    deleteMutation.mutate(collectionId, {
      onSuccess: () => {
        toast.success("Коллекция удалена");
        navigate("/collections");
      },
      onError: () => {
        toast.error("Не удалось удалить коллекцию");
      },
    });
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
        <div>
          <p className="text-xs uppercase tracking-[0.4em] text-accent">Коллекция</p>
          <h2 className="text-3xl font-semibold text-foreground">{collection.name}</h2>
          <p className="text-xs text-muted-foreground">{collection.description || "Описание отсутствует"}</p>
          <p className="text-[10px] uppercase tracking-[0.5em] text-muted-foreground">ID: {collection.id}</p>
        </div>
        <div className="flex flex-wrap gap-3">
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

      <details className="rounded-2xl border border-border bg-card p-4 shadow-lg" open>
        <summary className="cursor-pointer text-sm font-semibold text-accent">Источники данных</summary>
        <div className="mt-3 grid gap-4 md:grid-cols-2">
          <article className="space-y-1 rounded-2xl border border-border bg-muted/10 p-3">
            <h3 className="text-xs uppercase tracking-[0.4em] text-muted-foreground">Vector Store</h3>
            <p className="text-sm font-semibold text-foreground">{collection.vector_repo_info.status}</p>
            <p className="text-sm text-muted-foreground">Размер: {collection.vector_repo_info.size}</p>
            <p className="text-sm text-muted-foreground">Distance: {collection.vector_repo_info.distance}</p>
            <p className="text-sm text-muted-foreground">Пойнтов: {collection.vector_repo_info.points_count}</p>
          </article>
          <article className="space-y-1 rounded-2xl border border-border bg-muted/10 p-3">
            <h3 className="text-xs uppercase tracking-[0.4em] text-muted-foreground">Keyword Store</h3>
            <p className="text-sm font-semibold text-foreground">{collection.keyword_repo_info.status}</p>
            <p className="text-sm text-muted-foreground">Пойнтов: {collection.keyword_repo_info.points_count}</p>
          </article>
        </div>
      </details>

      <nav className="flex gap-2 border-b border-border pb-3">
        <NavLink
          to="."
          end
          className={({ isActive }) =>
            `rounded-full px-4 py-2 text-sm font-semibold ${
              isActive ? "bg-secondary text-secondary-foreground" : "text-muted-foreground"
            }`}
        >
          Chat
        </NavLink>
        <NavLink
          to="documents"
          className={({ isActive }) =>
            `rounded-full px-4 py-2 text-sm font-semibold ${
              isActive ? "bg-secondary text-secondary-foreground" : "text-muted-foreground"
            }`}
        >
          Documents
        </NavLink>
      </nav>

      <div className="rounded-3xl border border-border bg-card p-4 shadow-xl">
        <Outlet />
      </div>

        <ConfirmDialog
          open={isClearOpen}
          title="Очистить коллекцию?"
          description="Все чанки и исходные файлы будут удалены, но сама коллекция останется."
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
          description="Коллекция, индексы, документы, чанки и исходные файлы будут удалены."
          onCancel={() => setIsDeleteOpen(false)}
          onConfirm={() => {
            setIsDeleteOpen(false);
            handleDelete();
          }}
          loading={deleteMutation.isPending}
        />
    </section>
  );
};

export default CollectionPage;
