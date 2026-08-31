import {
  type DragEvent,
  type Dispatch,
  type InputHTMLAttributes,
  type SetStateAction,
  useMemo,
  useRef,
  useState,
} from "react";

type FileUpdater = Dispatch<SetStateAction<File[]>>;

interface FilePickerProps {
  files: File[];
  onFilesChange: FileUpdater;
  disabled?: boolean;
}

interface DirectoryInputAttributes extends InputHTMLAttributes<HTMLInputElement> {
  webkitdirectory?: boolean;
}

const directoryInputProps: DirectoryInputAttributes = {
  accept: "*/*",
  multiple: true,
  webkitdirectory: true,
};

const FilePicker = ({ files, onFilesChange, disabled }: FilePickerProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const addFiles = (incoming: FileList | null) => {
    if (!incoming) {
      return;
    }

    const nextFiles = Array.from(incoming);
    const combined = [...files, ...nextFiles];
    const unique = Array.from(
      new Map(combined.map((file) => [`${file.name}-${file.size}-${file.lastModified}`, file])).values(),
    );
    onFilesChange(unique);
    if (inputRef.current) {
      inputRef.current.value = "";
    }
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    event.stopPropagation();
    setIsDragging(false);
    addFiles(event.dataTransfer.files);
  };

  const handleRemove = (index: number) => {
    onFilesChange((prev: File[]) => prev.filter((_, idx) => idx !== index));
  };

  const helperText = useMemo(() => {
    if (!files.length) {
      return "Поддерживается drag-and-drop, multiple, выбрать директорию\n(webkitdirectory)";
    }
    return `${files.length} файлов выбрано`;
  }, [files.length]);

  return (
    <div className="space-y-2">
      <div
        className={`rounded-2xl border-2 border-dashed px-4 py-6 text-center text-sm transition ${
          isDragging ? "border-secondary bg-secondary/20" : "border-border"
        }`}
        onDragEnter={(event) => {
          event.preventDefault();
          event.stopPropagation();
          setIsDragging(true);
        }}
        onDragOver={(event) => {
          event.preventDefault();
          event.stopPropagation();
          setIsDragging(true);
        }}
        onDragLeave={(event) => {
          event.preventDefault();
          event.stopPropagation();
          setIsDragging(false);
        }}
        onDrop={handleDrop}
      >
        <p className="text-sm font-semibold text-foreground">Перетащите файлы сюда</p>
        <p className="text-xs text-muted-foreground">{helperText}</p>
        <button
          type="button"
          className="mt-3 text-xs font-semibold text-secondary"
          disabled={disabled}
          onClick={() => {
            inputRef.current?.click();
          }}
        >
          Выбрать вручную
        </button>
        <input
          {...directoryInputProps}
          ref={inputRef}
          type="file"
          className="hidden"
          disabled={disabled}
          onChange={(event) => addFiles(event.target.files)}
        />
      </div>
      {files.length > 0 && (
        <div className="space-y-2 rounded-2xl border border-border bg-muted/20 p-3 text-xs text-muted-foreground">
          {files.map((file, index) => (
            <div key={`${file.name}-${file.size}-${file.lastModified}`} className="flex items-center justify-between gap-2">
              <div className="flex flex-col">
                <span className="text-sm text-foreground">{file.name}</span>
                <span className="text-[11px] text-muted-foreground">{(file.size / 1024).toFixed(1)} KB</span>
              </div>
              <button
                type="button"
                className="rounded-full bg-border/80 px-3 py-1 text-[11px] font-semibold text-foreground"
                onClick={() => handleRemove(index)}
                disabled={disabled}
              >
                Удалить
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FilePicker;
