/** Форматы, которые реально поддерживают конвертеры backend (Docling/Text/VLM/Excel). */
export const ALLOWED_EXTENSIONS = [
  "pdf",
  "docx",
  "pptx",
  "html",
  "htm",
  "md",
  "txt",
  "xlsx",
  "png",
  "jpg",
  "jpeg",
  "webp",
] as const;

export const MAX_FILE_SIZE_BYTES = 50 * 1024 * 1024;
export const MAX_FILES_COUNT = 20;

export const FILE_ACCEPT_ATTRIBUTE = ALLOWED_EXTENSIONS.map((ext) => `.${ext}`).join(",");

export interface FileValidationError {
  file: File;
  reason: string;
}

export interface FileValidationResult {
  valid: File[];
  invalid: FileValidationError[];
}

const getExtension = (name: string): string => {
  const dotIndex = name.lastIndexOf(".");
  return dotIndex === -1 ? "" : name.slice(dotIndex + 1).toLowerCase();
};

/** Предварительная валидация на frontend. Backend остаётся источником истины. */
export const validateFiles = (files: File[]): FileValidationResult => {
  const valid: File[] = [];
  const invalid: FileValidationError[] = [];

  files.forEach((file, index) => {
    if (index >= MAX_FILES_COUNT) {
      invalid.push({
        file,
        reason: `Превышен лимит: не более ${MAX_FILES_COUNT} файлов за одну загрузку`,
      });
      return;
    }

    const extension = getExtension(file.name);
    if (!extension || !(ALLOWED_EXTENSIONS as readonly string[]).includes(extension)) {
      invalid.push({
        file,
        reason: `Формат «${extension || "без расширения"}» не поддерживается`,
      });
      return;
    }

    if (file.size === 0) {
      invalid.push({ file, reason: "Файл пустой" });
      return;
    }

    if (file.size > MAX_FILE_SIZE_BYTES) {
      const maxMb = Math.round(MAX_FILE_SIZE_BYTES / (1024 * 1024));
      invalid.push({ file, reason: `Размер превышает ${maxMb} МБ` });
      return;
    }

    valid.push(file);
  });

  return { valid, invalid };
};

/** Расширение для бейджа формата (md, pdf, docx...). */
export const getFileExtensionLabel = (name: string | null | undefined): string | null => {
  if (!name) {
    return null;
  }
  const extension = getExtension(name);
  return extension ? extension.toUpperCase() : null;
};

/** Имя документа без пути (backend может прислать source как путь/ключ S3). */
export const getBaseName = (source: string | null | undefined): string | null => {
  if (!source) {
    return null;
  }
  const normalized = source.replace(/\\/g, "/");
  const base = normalized.split("/").pop()?.trim();
  return base || source.trim();
};
