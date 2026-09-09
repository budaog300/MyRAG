import logging
from pathlib import Path
from typing import List
from src.rag.components.converters import BaseDocumentConverter
from src.core.exceptions.converter_exceptions import (
    DocumentConversionError,
    DocumentFileNotFoundError,
    NoConverterAvailableError,
)

logger = logging.getLogger(__name__)


class DocumentConverterService:
    def __init__(self, converters: List[BaseDocumentConverter]):
        self.converters = converters

    async def convert_to_markdown(self, file_bytes: bytes, filename: str) -> str:
        for converter in self.converters:
            if converter.supports(filename):
                converter_name = converter.__class__.__name__
                logger.info("Выбран конвертер: converter=%s, file=%s", converter_name, filename)
                try:
                    return await converter.convert(file_bytes, filename)
                except DocumentConversionError:
                    raise
                except Exception as exc:
                    logger.error("Ошибка конвертации файла: file=%s, converter=%s, ошибка=%s", filename, converter_name, exc, exc_info=True)
                    raise DocumentConversionError(message=f"Сбой конвертации файла '{filename}': {exc}") from exc

        extension = Path(filename).suffix.lower()
        logger.warning("Подходящий конвертер не найден: file=%s, extension=%s", filename, extension)
        raise NoConverterAvailableError(file_path=filename, extension=extension)