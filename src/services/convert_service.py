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
            logger.error(f"Файл для конвертации не найден по пути: {file_path}")
            raise DocumentFileNotFoundError(file_path=str(file_path))

        for converter in self.converters:
            if converter.supports(file_path):
                logger.info(f"Используется конвертер {converter.__class__.__name__} для файла: {file_path.name}")
                try:
                    return await converter.convert(file_path)
                except DocumentConversionError:
                    raise
                except Exception as exc:
                    logger.error(f"Ошибка при конвертации файла {file_path.name} через {converter.__class__.__name__}: {exc}")
                    raise DocumentConversionError(
                        message=f"Сбой конвертации файла '{file_path.name}': {exc}"
                    ) from exc

        logger.warning(f"Нет подходящего конвертера для файла: {file_path.name}")
        raise NoConverterAvailableError(
            file_path=file_path.name,
            extension=file_path.suffix.lower(),
        )