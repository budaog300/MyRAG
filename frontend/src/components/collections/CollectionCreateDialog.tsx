import { type FormEvent, useEffect, useState } from "react";
import FilePicker from "@/components/documents/FilePicker";

interface CollectionCreateDialogProps {
  open: boolean;
  loading?: boolean;
  onClose: () => void;
  onSubmit: (payload: {
    name: string;
    size?: number;
    distance?: string;
    description?: string;
    files: File[];
  }) => void;
}

const distanceOptions = ["cos", "dot", "euclid"];

const CollectionCreateDialog = ({ open, loading, onClose, onSubmit }: CollectionCreateDialogProps) => {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [size, setSize] = useState(1536);
  const [distance, setDistance] = useState("cos");
  const [files, setFiles] = useState<File[]>([]);
  const [advancedOpen, setAdvancedOpen] = useState(false);

  const resetForm = () => {
    setName("");
    setDescription("");
    setSize(1536);
    setDistance("cos");
    setFiles([]);
    setAdvancedOpen(false);
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
      size,
      distance,
      files,
    });
  };

  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4">
      <form
        className="w-full max-w-2xl space-y-6 rounded-3xl border border-border bg-card p-6 shadow-2xl"
        onSubmit={handleSubmit}
      >
        <header>
          <h3 className="text-xl font-semibold">Создать коллекцию</h3>
          <p className="text-sm text-muted-foreground">Коллекцию можно создать без документов.</p>
        </header>

        <div className="grid gap-4 md:grid-cols-2">
          <label className="space-y-1 text-sm text-muted-foreground">
            <span>Название</span>
            <input
              className="w-full rounded-2xl border border-border bg-muted/20 px-3 py-2 text-foreground focus:border-primary"
              required
              value={name}
              onChange={(event) => setName(event.target.value)}
            />
          </label>
          <label className="space-y-1 text-sm text-muted-foreground">
            <span>Описание</span>
            <textarea
              className="w-full rounded-2xl border border-border bg-muted/20 px-3 py-2 text-foreground focus:border-primary"
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              rows={2}
            />
          </label>
        </div>

        <div>
          <button
            type="button"
            className="text-sm font-semibold text-secondary"
            onClick={() => setAdvancedOpen((prev) => !prev)}
          >
            {advancedOpen ? "Скрыть" : "Advanced settings"}
          </button>
          {advancedOpen && (
            <div className="mt-3 grid gap-4 md:grid-cols-2">
              <label className="space-y-1 text-sm text-muted-foreground">
                <span>Размер векторного пространства</span>
                <input
                  type="number"
                  min={1}
                  value={size}
                  onChange={(event) => setSize(Number(event.target.value))}
                  className="w-full rounded-2xl border border-border bg-muted/20 px-3 py-2 text-foreground focus:border-primary"
                />
              </label>
              <label className="space-y-1 text-sm text-muted-foreground">
                <span>Алгоритм схожести</span>
                <select
                  value={distance}
                  onChange={(event) => setDistance(event.target.value)}
                  className="w-full rounded-2xl border border-border bg-muted/20 px-3 py-2 text-foreground focus:border-primary"
                >
                  {distanceOptions.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </label>
            </div>
          )}
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
