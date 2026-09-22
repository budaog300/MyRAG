import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQueries } from "@/hooks/useQueries";
import { usePagination } from "@/hooks/usePagination";
import { formatDate } from "@/lib/utils";
import Pagination from "@/components/common/Pagination";
import ConfirmDialog from "@/components/common/ConfirmDialog";
import Spinner from "@/components/ui/Spinner";
import { Button } from "@/components/ui/button";
import { toast } from "sonner";

const QueriesPage = () => {
    const { collectionId } = useParams<{ collectionId: string }>();
    const { pagination, setPage, setSize } = usePagination();
    const { page, size } = pagination;
    const { query, deleteMutation, clearMutation } = useQueries({
        collectionId: collectionId ?? "",
        page,
        size,
    });
    const [pendingDelete, setPendingDelete] = useState<string | null>(null);
    const [pendingClear, setPendingClear] = useState(false);
    const navigate = useNavigate();

    if (!collectionId) {
        return null;
    }

    const items = query.data?.items ?? [];
    const total = query.data?.total ?? 0;

    return (
        <div className="space-y-6">
            <div className="rounded-2xl border border-border bg-card p-6 shadow-xl">
                <div className="flex flex-wrap items-center justify-between gap-3">
                    <h3 className="text-lg font-semibold">
                        История запросов
                    </h3>

                    {items.length > 0 && (
                        <Button
                            variant="destructive-outline"
                            size="sm"
                            className="rounded-full px-3.5"
                            onClick={() => setPendingClear(true)}
                            disabled={clearMutation.isPending}
                        >
                            Очистить историю
                        </Button>
                    )}
                </div>
            </div>

            <div className="rounded-2xl border border-border bg-card p-4 shadow-xl">
                {query.isLoading && (
                    <div className="py-10 text-center">
                        <Spinner />
                    </div>
                )}

                {query.isError && (
                    <div className="space-y-3 text-center text-sm text-muted-foreground">
                        <p>Не удалось загрузить историю запросов.</p>
                        <Button
                            variant="link"
                            className="h-auto px-0 text-sm"
                            onClick={() => query.refetch()}
                        >
                            Повторить
                        </Button>
                    </div>
                )}

                {!query.isLoading &&
                    !query.isError &&
                    items.length === 0 && (
                        <p className="py-10 text-center text-sm text-muted-foreground">
                            Запросов ещё не было
                        </p>
                    )}

                {!query.isLoading &&
                    !query.isError &&
                    items.length > 0 && (
                        <div className="overflow-x-auto">
                            <table className="min-w-full text-left text-sm">
                                <thead>
                                    <tr>
                                        <th className="px-3 py-2 text-xs uppercase tracking-[0.3em] text-muted-foreground">
                                            Запрос
                                        </th>
                                        <th className="px-3 py-2 text-xs uppercase tracking-[0.3em] text-muted-foreground">
                                            Дата
                                        </th>
                                        <th className="px-3 py-2 text-xs uppercase tracking-[0.3em] text-muted-foreground">
                                            Действия
                                        </th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {items.map((item) => (
                                        <tr
                                            key={item.id}
                                            className="border-t border-border transition hover:bg-muted/10"
                                        >
                                            <td
                                                className="max-w-[300px] cursor-pointer truncate px-3 py-3 text-foreground"
                                                onClick={() =>
                                                    navigate(
                                                        `/collections/${collectionId}/queries/${item.id}`,
                                                    )
                                                }
                                            >
                                                {item.query.length > 50
                                                    ? `${item.query.slice(0, 50)}...`
                                                    : item.query}
                                            </td>

                                            <td className="px-3 py-3 text-muted-foreground">
                                                {formatDate(item.created_at)}
                                            </td>

                                            <td className="px-3 py-3">
                                                <Button
                                                    variant="destructive-outline"
                                                    size="sm"
                                                    className="rounded-full px-3 text-[11px]"
                                                    onClick={() =>
                                                        setPendingDelete(
                                                            item.id,
                                                        )
                                                    }
                                                >
                                                    Удалить
                                                </Button>
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
                title="Удалить запрос?"
                description="Запрос будет удалён из истории коллекции."
                onCancel={() => setPendingDelete(null)}
                onConfirm={() => {
                    if (!collectionId || !pendingDelete) {
                        return;
                    }

                    deleteMutation.mutate(
                        { queryId: pendingDelete },
                        {
                            onSuccess: () => {
                                toast.success("Запрос удалён");
                                setPendingDelete(null);
                            },
                            onError: () => {
                                toast.error("Не удалось удалить запрос");
                                setPendingDelete(null);
                            },
                        },
                    );
                }}
                loading={deleteMutation.isPending}
            />
            <ConfirmDialog
                open={pendingClear}
                title="Очистить историю?"
                description="Все запросы этой коллекции будут удалены из истории."
                onCancel={() => setPendingClear(false)}
                onConfirm={() => {
                    clearMutation.mutate(undefined, {
                        onSuccess: () => {
                            toast.success("История запросов очищена");
                            setPendingClear(false);
                        },
                        onError: () => {
                            toast.error("Не удалось очистить историю");
                            setPendingClear(false);
                        },
                    });
                }}
                loading={clearMutation.isPending}
            />
        </div>
    );
};

export default QueriesPage;