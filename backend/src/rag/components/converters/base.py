import time
import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Set
from src.core.constants import DOCUMENT_DELIMITER

logger = logging.getLogger(__name__)


class BaseDocumentConverter(ABC):
    SUPPORTED_EXTENSIONS: Set[str] = set()
    DELIMITER: str = DOCUMENT_DELIMITER

    def supports(self, filename: str) -> bool:
        return Path(filename).suffix.lower() in self.SUPPORTED_EXTENSIONS

    async def convert(self, file_bytes: bytes, filename: str) -> str:
        start_time = time.perf_counter()

        try:
            result = await self._convert(file_bytes, filename)

            elapsed = time.perf_counter() - start_time

            logger.info(
                "Файл %s обработан конвертером %s за %.2f сек.",
                filename,
                self.__class__.__name__,
                elapsed,
            )

            return result

        except Exception:
            elapsed = time.perf_counter() - start_time

            logger.error(
                "Ошибка обработки файла %s конвертером %s через %.2f сек.",
                filename,
                self.__class__.__name__,
                elapsed,
            )

            raise

    @abstractmethod
    async def _convert(self, file_bytes: bytes, filename: str) -> str:
        """Преобразует документ в Markdown."""
        pass