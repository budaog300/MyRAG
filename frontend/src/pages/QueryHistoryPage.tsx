import { useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useQueryHistory } from "@/hooks/useQueryHistory";
import ConfirmDialog from "@/components/common/ConfirmDialog";
import Spinner from "@/components/ui/Spinner";
import { formatDate } from "@/lib/utils";
import { toast } from "sonner";

const QueryHistoryPage = () => {
    const { collectionId, queryId } = useParams<{
        collectionId: string;
        queryId: string;
    }>();

    const { query, deleteMutation } = useQueryHistory(collectionId, queryId);
    const [pendingDelete, setPendingDelete] = useState<string | null>(null);
    const navigate = useNavigate();

    if (!collectionId || !queryId) {
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
                <p className="text-sm text-muted-foreground">
                    Не удалось загрузить запрос.
                </p>
            </div>
        );
    }

    const item = query.data;

    if (!item) {
        return <p>Запрос не найден.</p>;
    }

    return (
        <div className="space-y-6">
            <header className="rounded-2xl border border-border bg-card p-6 shadow-xl">
                <p className="text-xs uppercase tracking-[0.4em] text-accent">
                    Информация о запросе
                </p>

                <div className="mt-3">
                    <h2 className="text-2xl font-semibold text-foreground">
                        Запрос
                    </h2>

                    <p className="mt-1 text-xs text-muted-foreground">
                        ID: {queryId}
                    </p>
                </div>

                <div className="mt-5">
                    <button
                        type="button"
                        className="rounded-full border border-border px-4 py-2 text-sm font-semibold text-destructive"
                        onClick={() => setPendingDelete(queryId)}
                        disabled={deleteMutation.isPending}
                    >
                        Удалить запрос
                    </button>
                </div>
            </header>

            <section className="rounded-2xl border border-border bg-card p-6 shadow-xl">
                <h3 className="text-sm font-semibold text-foreground">
                    Запрос
                </h3>

                <p className="mt-4 whitespace-pre-wrap text-sm text-foreground">
                    {item.query}
                </p>
            </section>

            <section className="rounded-2xl border border-border bg-card p-6 shadow-xl">
                <h3 className="text-sm font-semibold text-foreground">
                    Ответ
                </h3>

                <p className="mt-4 whitespace-pre-wrap text-sm text-muted-foreground">
                    {item.answer || "Ответ отсутствует"}
                </p>
            </section>

            <section className="rounded-2xl border border-border bg-card p-6 shadow-xl">
                <h3 className="text-sm font-semibold text-foreground">
                    Свойства запроса
                </h3>

                <div className="mt-4 space-y-3">
                    <p className="text-sm text-muted-foreground">
                        Время выполнения:{" "}
                        {item.response_time_ms != null
                            ? `${item.response_time_ms} мс`
                            : "—"}
                    </p>

                    <p className="text-sm text-muted-foreground">
                        Создан: {formatDate(item.created_at)}
                    </p>
                </div>
            </section>

            <ConfirmDialog
                open={Boolean(pendingDelete)}
                title="Удалить запрос?"
                description="Запрос будет удалён из истории коллекции."
                onCancel={() => setPendingDelete(null)}
                onConfirm={() => {
                    if (!pendingDelete) {
                        return;
                    }

                    deleteMutation.mutate(
                        { queryId: pendingDelete },
                        {
                            onSuccess: () => {
                                toast.success("Запрос удалён");
                                navigate(`/collections/${collectionId}/queries`);
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
        </div>
    );
};

export default QueryHistoryPage;