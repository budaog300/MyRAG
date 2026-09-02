import { type FormEvent, useEffect, useState } from "react";

import InfoTooltip from "@/components/ui/InfoTooltip";

import type {
    CollectionDetails,
    UpdateCollectionPayload,
} from "@/types/collections";

interface CollectionUpdateDialogProps {
    open: boolean;
    loading?: boolean;
    collection: CollectionDetails;
    onClose: () => void;
    onSubmit: (payload: UpdateCollectionPayload) => void;
}

const CollectionUpdateDialog = ({
    open,
    loading,
    collection,
    onClose,
    onSubmit,
}: CollectionUpdateDialogProps) => {
    const [name, setName] = useState("");
    const [description, setDescription] = useState("");

    useEffect(() => {
        if (open) {
            setName(collection.name);
            setDescription(collection.description ?? "");
        }
    }, [open, collection]);

    const handleSubmit = (event: FormEvent) => {
        event.preventDefault();

        const payload: UpdateCollectionPayload = {};

        if (name.trim() !== collection.name) {
            payload.name = name.trim();
        }

        if (description !== (collection.description ?? "")) {
            payload.description = description;
        }

        if (Object.keys(payload).length === 0) {
            onClose();
            return;
        }

        onSubmit(payload);
    };

    if (!open) {
        return null;
    }

    return (
        <div
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4"
            onClick={onClose}
        >
            <form
                className="w-full max-w-2xl space-y-6 rounded-3xl border border-border bg-black p-6 shadow-2xl"
                onClick={(event) => event.stopPropagation()}
                onSubmit={handleSubmit}
            >
                <header>
                    <h3 className="text-xl font-semibold">
                        Изменить коллекцию
                    </h3>

                    <p className="text-sm text-muted-foreground">
                        Измените название или описание коллекции.
                    </p>
                </header>

                <div className="space-y-4">
                    <label className="space-y-1 text-sm text-muted-foreground">
                        <span>
                            Название{" "}
                            <span className="text-destructive">*</span>
                        </span>

                        <input
                            className="w-full rounded-2xl border border-border bg-muted/20 px-3 py-2 text-foreground focus:border-primary"
                            required
                            minLength={5}
                            value={name}
                            onChange={(event) => setName(event.target.value)}
                            disabled={loading}
                        />
                    </label>

                    <label className="space-y-1 text-sm text-muted-foreground">
                        <span className="flex items-center gap-1.5">
                            <span>Описание</span>

                            <InfoTooltip text="Необязательное описание коллекции, чтобы было понятно, для чего она используется." />
                        </span>

                        <textarea
                            className="w-full rounded-2xl border border-border bg-muted/20 px-3 py-2 text-foreground focus:border-primary"
                            value={description}
                            onChange={(event) => setDescription(event.target.value)}
                            rows={3}
                            disabled={loading}
                        />
                    </label>
                </div>

                <div className="flex justify-end gap-3">
                    <button
                        type="button"
                        className="rounded-full border border-border px-4 py-2 text-sm font-semibold text-muted-foreground"
                        onClick={onClose}
                        disabled={loading}
                    >
                        Отмена
                    </button>

                    <button
                        type="submit"
                        disabled={!name.trim() || loading}
                        className="rounded-full bg-secondary px-4 py-2 text-sm font-semibold text-secondary-foreground disabled:opacity-50"
                    >
                        {loading ? "Сохранение..." : "Сохранить"}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default CollectionUpdateDialog;