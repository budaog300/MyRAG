from src.core.exceptions import BaseAppException


class DocumentConversionError(BaseAppException):
    """Базовое исключение для ошибок конвертации документов."""

    def __init__(
        self,
        message: str = "Ошибка при конвертации документа",
        status_code: int = 422,
    ):
        super().__init__(message=message, status_code=status_code)


class UnsupportedFileFormatError(DocumentConversionError):
    """Файл имеет неподдерживаемое расширение."""

    def __init__(self, extension: str):
        super().__init__(
            message=f"Формат файла '{extension}' не поддерживается для конвертации.",
            status_code=400,
        )


class DocumentFileNotFoundError(DocumentConversionError):
    """Файл не найден по указанному пути."""

    def __init__(self, file_path: str):
        super().__init__(
            message=f"Файл для конвертации не найден по пути: {file_path}",
            status_code=404,
        )


class PipelineInitializationError(DocumentConversionError):
    """Ошибка при сборке или конфигурации пайплайна конвертера."""

    def __init__(self, reason: str):
        super().__init__(
            message=f"Ошибка инициализации конвертера: {reason}",
            status_code=500,
        )


class VLMProviderServiceError(DocumentConversionError):
    """Ошибка при обращении к внешней VLM во время обогащения/описания изображений."""

    def __init__(self, details: str):
        super().__init__(
            message=f"Сбой VLM-сервиса при обработке медиа-контента: {details}",
            status_code=502,
        )


class FileEncodingError(DocumentConversionError):
    """Ошибка декодирования файла (не подходящая кодировка)."""

    def __init__(self, file_path: str, encoding: str = "utf-8"):
        super().__init__(
            message=f"Не удалось прочитать файл '{file_path}' в кодировке {encoding}. Файл имеет другой формат или содержит некорректные символы.",
            status_code=400,
        )


class EmptyDocumentError(DocumentConversionError):
    """Документ не содержит валидных данных для конвертации."""

    def __init__(self, file_path: str):
        super().__init__(
            message=f"Файл '{file_path}' пуст или содержит только скрытые/пустые листы.",
            status_code=422,
        )


class CorruptedExcelFileError(DocumentConversionError):
    """Файл Excel поврежден или зашифрован/защищен паролем."""

    def __init__(self, file_path: str, details: str = ""):
        super().__init__(
            message=f"Не удалось прочитать файл Excel '{file_path}'. Возможно, он поврежден или защищен паролем. {details}".strip(),
            status_code=400,
        )


class NoConverterAvailableError(DocumentConversionError):
    """Не найден конвертер, поддерживающий данный формат файла."""

    def __init__(self, file_path: str, extension: str):
        super().__init__(
            message=f"Не найден подходящий конвертер для файла '{file_path}' (расширение: '{extension}').",
            status_code=415,
        )