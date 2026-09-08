import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Set
from src.core.constants import DOCUMENT_DELIMITER
from src.core.logger import logger


class BaseDocumentConverter(ABC):
    SUPPORTED_EXTENSIONS: Set[str] = set()
    DELIMITER: str = DOCUMENT_DELIMITER

    def supports(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    async def convert(self, file_path: Path) -> str:
        start_time = time.perf_counter()

        try:
            result = await self._convert(file_path)

            elapsed = time.perf_counter() - start_time

            logger.info(
                "Файл %s обработан конвертером %s за %.2f сек.",
                file_path.name,
                self.__class__.__name__,
                elapsed,
            )

            return result

        except Exception:
            elapsed = time.perf_counter() - start_time

            logger.error(
                "Ошибка обработки файла %s конвертером %s через %.2f сек.",
                file_path.name,
                self.__class__.__name__,
                elapsed,
            )

            raise

    @abstractmethod
    async def _convert(self, file_path: Path) -> str:
        """Преобразует документ в Markdown."""
        pass