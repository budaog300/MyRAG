import { type FormEvent, useState } from "react";
import FilePicker from "@/components/documents/FilePicker";
import InfoTooltip from "@/components/ui/InfoTooltip";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";

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

  const handleClose = () => {
    setName("");
    setDescription("");
    setFiles([]);
    onClose();
  };

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!name.trim() || loading) {
      return;
    }
    onSubmit({
      name: name.trim(),
      description: description.trim() || undefined,
      files,
    });
  };

  const nameTooShort = name.length > 0 && name.trim().length < 5;

  return (
    <Dialog open={open} onOpenChange={(next) => !loading && !next && handleClose()}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Создать коллекцию</DialogTitle>
          <DialogDescription>
            Коллекцию можно создать пустой, а документы загрузить позже.
          </DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-1.5">
              <Label htmlFor="create-name">
                Название <span className="text-red-500">*</span>
              </Label>
              <Input
                id="create-name"
                required
                minLength={5}
                placeholder="Например: Кадровые регламенты"
                value={name}
                onChange={(event) => setName(event.target.value)}
                disabled={loading}
                aria-invalid={nameTooShort}
              />
              {nameTooShort && (
                <p className="text-xs text-red-600">Минимум 5 символов</p>
              )}
            </div>

            <div className="space-y-1.5">
              <Label htmlFor="create-description" className="flex items-center gap-1.5">
                Описание
                <InfoTooltip text="Необязательное описание, чтобы было понятно, для чего коллекция используется." />
              </Label>
              <Textarea
                id="create-description"
                rows={2}
                placeholder="Для чего эта база знаний…"
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                disabled={loading}
              />
            </div>
          </div>

          <FilePicker files={files} onFilesChange={setFiles} disabled={loading} />

          <DialogFooter>
            <Button type="button" variant="secondary" onClick={handleClose} disabled={loading}>
              Отмена
            </Button>
            <Button type="submit" disabled={!name.trim() || nameTooShort || loading}>
              {loading ? "Создание…" : "Создать"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default CollectionCreateDialog;
