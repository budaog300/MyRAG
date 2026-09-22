import { type FormEvent, useState } from "react";
import type { CollectionDetails, UpdateCollectionRequest } from "@/types/collection";
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

interface CollectionUpdateDialogProps {
  open: boolean;
  loading?: boolean;
  collection: CollectionDetails;
  onClose: () => void;
  onSubmit: (payload: UpdateCollectionRequest) => void;
}

const CollectionUpdateDialog = ({
  open,
  loading,
  collection,
  onClose,
  onSubmit,
}: CollectionUpdateDialogProps) => {
  const [name, setName] = useState(collection.name);
  const [description, setDescription] = useState(collection.description ?? "");
  const [prevOpen, setPrevOpen] = useState(open);

  if (open !== prevOpen) {
    setPrevOpen(open);
    if (open) {
      setName(collection.name);
      setDescription(collection.description ?? "");
    }
  }

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();

    const payload: UpdateCollectionRequest = {};

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

  const nameTooShort = name.trim().length < 5;

  return (
    <Dialog open={open} onOpenChange={(next) => !loading && !next && onClose()}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>Изменить коллекцию</DialogTitle>
          <DialogDescription>Измените название или описание коллекции.</DialogDescription>
        </DialogHeader>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1.5">
            <Label htmlFor="update-name">
              Название <span className="text-red-500">*</span>
            </Label>
            <Input
              id="update-name"
              required
              minLength={5}
              value={name}
              onChange={(event) => setName(event.target.value)}
              disabled={loading}
              aria-invalid={nameTooShort}
            />
            {nameTooShort && <p className="text-xs text-red-600">Минимум 5 символов</p>}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="update-description">Описание</Label>
            <Textarea
              id="update-description"
              rows={4}
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              disabled={loading}
            />
          </div>

          <DialogFooter>
            <Button type="button" variant="secondary" onClick={onClose} disabled={loading}>
              Отмена
            </Button>
            <Button type="submit" disabled={nameTooShort || loading}>
              {loading ? "Сохранение…" : "Сохранить"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

export default CollectionUpdateDialog;
