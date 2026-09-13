import { type FormEvent, useEffect, useState } from "react";
import FilePicker from "@/components/documents/FilePicker";
import InfoTooltip from "@/components/ui/InfoTooltip";

interface CollectionCreateDialogProps {
  open: boolean;
  loading?: boolean;
  onClose: () => void;
  onSubmit: (payload: {
    name: string;
    description?: string;
    files: File[];
  }) => void;
}

const CollectionCreateDialog = ({ open, loading, onClose, onSubmit }: CollectionCreateDialogProps) => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [files, setFiles] = useState<File[]>([]);

  const resetForm = () => {
    setName("");
    setDescription("");
    setFiles([]);
  };

  useEffect(() => {
    if (!open) {
      resetForm();
    }
  }, [open]);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!name.trim()) {
      return;
    }
    onSubmit({
      name: name.trim(),
      description: description.trim() || undefined,
      files,
    });
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
        className="w-full max-w-4xl space-y-6 rounded-3xl border border-border bg-black p-6 shadow-2xl"
        onClick={(event) => event.stopPropagation()}
        onSubmit={handleSubmit}
      >
        <header>
          <h3 className="text-xl font-semibold">Создать коллекцию</h3>
          <p className="text-sm text-muted-foreground">Коллекцию можно создать без документов.</p>
        </header>

        <div className="grid gap-4 md:grid-cols-2">
          <label className="space-y-1 text-sm text-muted-foreground">
            <span>Название <span className="text-destructive">*</span></span>
            <input
              className="w-full rounded-2xl border border-border bg-muted/20 px-3 py-2 text-foreground focus:border-primary"
              required
              minLength={5}
              value={name}
              onChange={(event) => setName(event.target.value)}
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
              rows={2}
            />
          </label>
        </div>

        <FilePicker files={files} onFilesChange={setFiles} disabled={loading} />

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
            {loading ? "Создание..." : "Создать"}
          </button>
        </div>
      </form>
    </div>
  );
};

export default CollectionCreateDialog;
