# src/rag/services/convert_service.py
from pathlib import Path
from typing import List
from src.rag.components.converters import BaseDocumentConverter

class DocumentConverterService:
    def __init__(self, converters: List[BaseDocumentConverter]):
        self.converters = converters

    async def convert_to_markdown(self, source: str | Path) -> str:
        file_path = Path(source)
        
        for converter in self.converters:
            if converter.supports(file_path):
                return await converter.convert(file_path)

        raise ValueError(f"Не найден поддерживаемый конвертер для файла: {file_path}")