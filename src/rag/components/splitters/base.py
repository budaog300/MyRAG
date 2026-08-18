from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.rag.schemas.document import RawDocumentSchema, RAGDocument

class BaseDocumentSplitter(ABC):
    @abstractmethod
    def split(
        self, 
        doc: RawDocumentSchema, 
        markdown_text: str,
        chunk_size: int = 1000,
        chunk_overlap: int = 100
    ) -> List[RAGDocument]:
        """Разбивает Markdown текст на обогащенные чанки"""
        pass