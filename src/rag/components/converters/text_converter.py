# src/rag/components/converters/text_converter.py
import asyncio
from pathlib import Path
from typing import Set

from src.rag.components.converters import BaseDocumentConverter


class TextDocumentConverter(BaseDocumentConverter):
    """
    Конвертер для файлов, которые уже находятся в формате Markdown или Plain Text.
    Просто читает содержимое файла без тяжелой обработки.
    """

    SUPPORTED_EXTENSIONS: Set[str] = {".md", ".markdown", ".txt"}

    def supports(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS

    async def convert(self, file_path: Path) -> str:
        return await asyncio.to_thread(file_path.read_text, encoding="utf-8")