import {
  type ChangeEvent,
  type DragEvent,
  type Dispatch,
  type SetStateAction,
  useRef,
  useState,
} from "react";
import { AlertCircle, FilePlus2, X } from "lucide-react";
import { formatFileSize, cn } from "@/lib/utils";
import {
  FILE_ACCEPT_ATTRIBUTE,
  MAX_FILES_COUNT,
  validateFiles,
} from "@/lib/fileValidation";
import { Button } from "@/components/ui/button";

type FileUpdater = Dispatch<SetStateAction<File[]>>;

interface FilePickerProps {
  files: File[];
  onFilesChange: FileUpdater;
  disabled?: boolean;
}

interface ValidationError {
  file: File;
  reason: string;
}

const fileKey = (file: File) => `${file.name}-${file.size}-${file.lastModified}`;

const FilePicker = ({ files, onFilesChange, disabled }: FilePickerProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [errors, setErrors] = useState<ValidationError[]>([]);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const addFiles = (incoming: FileList | null) => {
    if (!incoming) return;

    const combined = [...files, ...Array.from(incoming)];
    const unique = Array.from(new Map(combined.map((file) => [fileKey(file), file])).values());
    const { valid, invalid } = validateFiles(unique);

    setErrors(invalid);
    onFilesChange(valid);

    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);
    if (!disabled) addFiles(event.dataTransfer.files);
  };

  const handleRemove = (file: File) => {
    onFilesChange((prev) => prev.filter((item) => fileKey(item) !== fileKey(file)));
    setErrors((prev) => prev.filter((error) => fileKey(error.file) !== fileKey(file)));
  };

  const handleInputChange = (event: ChangeEvent<HTMLInputElement>) => {
    addFiles(event.target.files);
  };

  return (
    <div className="space-y-3">
      <div
        className={cn(
          "rounded-2xl border-2 border-dashed px-4 py-8 text-center transition-colors duration-200",
          isDragging
            ? "border-accent-400 bg-accent-50/70"
            : "border-slate-300 bg-slate-50/50 hover:border-slate-400",
          disabled && "pointer-events-none opacity-60"
        )}
        onDragEnter={(event) => {
          event.preventDefault();
          event.stopPropagation();
          if (!disabled) setIsDragging(true);
        }}
        onDragOver={(event) => {
          event.preventDefault();
          event.stopPropagation();
          if (!disabled) setIsDragging(true);
        }}
        onDragLeave={(event) => {
          event.preventDefault();
          event.stopPropagation();
          setIsDragging(false);
        }}
        onDrop={handleDrop}
      >
        <span className="mx-auto mb-3 flex h-11 w-11 items-center justify-center rounded-xl bg-accent-50 text-accent-600">
          <FilePlus2 className="h-5 w-5" aria-hidden="true" />
        </span>
        <p className="text-sm font-semibold text-slate-800">Добавьте документы</p>
        <p className="mt-1 text-xs text-muted-foreground">
          Перетащите файлы сюда или выберите на устройстве
        </p>
        <Button
          type="button"
          variant="outline"
          size="sm"
          className="mt-3"
          disabled={disabled}
          onClick={() => inputRef.current?.click()}
        >
          Выбрать файлы
        </Button>
        <p className="mt-3 text-[11px] text-slate-400">
          PDF, DOCX, PPTX, XLSX, HTML, MD, TXT, PNG, JPG, WEBP · до 50 МБ · до {MAX_FILES_COUNT} файлов
        </p>
        <input
          accept={FILE_ACCEPT_ATTRIBUTE}
          multiple
          ref={inputRef}
          type="file"
          className="hidden"
          disabled={disabled}
          onChange={handleInputChange}
        />
      </div>

      {files.length > 0 && (
        <div className="space-y-2 rounded-xl border border-border bg-card p-3">
          <p className="text-xs font-semibold text-muted-foreground">
            Выбрано файлов: <span className="text-slate-700">{files.length}</span>
          </p>
          <ul className="space-y-2">
            {files.map((file) => (
              <li
                key={fileKey(file)}
                className="flex items-center justify-between gap-2 rounded-lg bg-slate-50 px-3 py-2"
              >
                <div className="min-w-0">
                  <p className="truncate text-sm text-slate-800">{file.name}</p>
                  <p className="text-[11px] text-slate-400">{formatFileSize(file.size)}</p>
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon-sm"
                  onClick={() => handleRemove(file)}
                  disabled={disabled}
                  aria-label={`Убрать файл ${file.name}`}
                >
                  <X className="h-4 w-4" aria-hidden="true" />
                </Button>
              </li>
            ))}
          </ul>
        </div>
      )}

      {errors.length > 0 && (
        <div className="space-y-2 rounded-xl border border-red-200 bg-red-50/70 p-3">
          <p className="flex items-center gap-1.5 text-xs font-semibold text-red-700">
            <AlertCircle className="h-3.5 w-3.5" aria-hidden="true" />
            Файлы не добавлены:
          </p>
          <ul className="space-y-1.5">
            {errors.map((error) => (
              <li key={fileKey(error.file)} className="text-xs leading-relaxed text-red-700">
                <span className="font-medium">{error.file.name}</span> — {error.reason}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default FilePicker;
