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

    async def convert_to_markdown(self, source: str | Path) -> str:
        file_path = Path(source)
        if not file_path.exists():
            logger.error("Файл для конвертации не найден: path=%s", file_path)
            raise DocumentFileNotFoundError(file_path=str(file_path))

        for converter in self.converters:
            if converter.supports(file_path):
                converter_name = converter.__class__.__name__
                logger.info("Выбран конвертер: converter=%s, file=%s", converter_name, file_path.name)
                try:
                    return await converter.convert(file_path)
                except DocumentConversionError:
                    raise
                except Exception as exc:
                    logger.error("Ошибка конвертации файла: file=%s, converter=%s, ошибка=%s", file_path.name, converter_name, exc, exc_info=True)
                    raise DocumentConversionError(
                        message=f"Сбой конвертации файла '{file_path.name}': {exc}"
                    ) from exc

        logger.warning("Подходящий конвертер не найден: file=%s, extension=%s", file_path.name, file_path.suffix.lower())
        raise NoConverterAvailableError(
            file_path=file_path.name,
            extension=file_path.suffix.lower(),
        )