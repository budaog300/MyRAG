from abc import ABC, abstractmethod
from pathlib import Path
from typing import Set
from src.core.constants import DOCUMENT_DELIMITER

class BaseDocumentConverter(ABC):
    SUPPORTED_EXTENSIONS: Set[str] = set()
    DELIMITER: str = DOCUMENT_DELIMITER

    def supports(self, file_path: Path) -> bool:
        """Проверяет, поддерживает ли данный конвертер расширение файла"""
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    @abstractmethod
    async def convert(self, file_path: Path) -> str:
        """Преобразует документ в Markdown"""
        pass