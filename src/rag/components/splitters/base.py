from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.rag.schemas.document import RawDocumentSchema, RAGDocument

class BaseDocumentSplitter(ABC):
    @abstractmethod
    def split(
        self, 
        doc: RawDocumentSchema, 
        markdown_text: str,
        **kwargs
    ) -> List[RAGDocument]:
        """Разбивает Markdown текст на чанки"""
        pass