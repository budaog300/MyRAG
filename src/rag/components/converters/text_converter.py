# src/rag/components/converters/text_converter.py
import logging
import asyncio
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

    SUPPORTED_EXTENSIONS: Set[str] = {".md", ".markdown", ".txt"}

    async def convert(self, file_path: Path) -> str:
        if not file_path.exists():
            raise DocumentFileNotFoundError(file_path=str(file_path))

        if not self.supports(file_path):
            raise UnsupportedFileFormatError(extension=file_path.suffix)

        try:
            return await asyncio.to_thread(file_path.read_text, encoding="utf-8")
        except UnicodeDecodeError as exc:
            logger.error(f"Ошибка кодировки файла {file_path.name}: {exc}")
            raise FileEncodingError(file_path=file_path.name, encoding="utf-8") from exc

        except PermissionError as exc:
            logger.error(f"Нет прав на чтение файла {file_path.name}: {exc}")
            raise DocumentConversionError(
                message=f"Отказано в доступе при чтении файла '{file_path.name}'",
                status_code=403,
            ) from exc

        except Exception as exc:
            logger.error(f"Ошибка чтения файла {file_path.name}: {exc}")
            raise DocumentConversionError(
                message=f"Ошибка при чтении файла '{file_path.name}': {exc}"
            ) from exc