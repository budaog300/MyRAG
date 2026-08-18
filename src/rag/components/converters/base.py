from abc import ABC, abstractmethod
from pathlib import Path

class BaseDocumentConverter(ABC):
    @abstractmethod
    def supports(self, file_path: Path) -> bool:
        """Проверяет, поддерживает ли данный конвертер расширение файла"""
        pass

    @abstractmethod
    async def convert(self, file_path: Path) -> str:
        """Преобразует документ в Markdown"""
        pass