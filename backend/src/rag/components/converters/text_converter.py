import asyncio
import logging
from pathlib import Path
from typing import Set

from src.rag.components.converters import BaseDocumentConverter
from src.core.exceptions.converter_exceptions import (
    DocumentConversionError,
    DocumentFileNotFoundError,
    FileEncodingError,
    UnsupportedFileFormatError,
)

logger = logging.getLogger(__name__)


class TextDocumentConverter(BaseDocumentConverter):
    """Конвертер для простых текстовых файлов (.txt, .md)."""

    SUPPORTED_EXTENSIONS: Set[str] = {".md", ".txt"}

    async def _convert(self, file_bytes: bytes, filename: str) -> str:
        if not self.supports(filename):
            raise UnsupportedFileFormatError(extension=Path(filename).suffix)
        try:
            content = file_bytes.decode("utf-8")
            return content
        except UnicodeDecodeError as exc:
            logger.error(f"Ошибка кодировки файла {filename}: {exc}")
            raise FileEncodingError(file_path=filename, encoding="utf-8") from exc

        except PermissionError as exc:
            logger.error(f"Нет прав на чтение файла {filename}: {exc}")
            raise DocumentConversionError(
                message=f"Отказано в доступе при чтении файла '{filename}'",
                status_code=403,
            ) from exc

        except Exception as exc:
            logger.error(f"Ошибка чтения файла {filename}: {exc}")
            raise DocumentConversionError(
                message=f"Ошибка при чтении файла '{filename}': {exc}"
            ) from exc