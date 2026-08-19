from abc import ABC, abstractmethod
from typing import List, Optional
from src.rag.schemas.document import RAGDocument


class BaseReranker(ABC):
    """Абстрактный базовый класс для компонентов реранкинга RAG Документов"""

    @abstractmethod
    async def compress_documents(
        self,
        query: str,
        documents: List[RAGDocument],
        top_n: Optional[int] = None,
    ) -> List[RAGDocument]:
        """
        Ранжирует документы по релевантности запросу и возвращает 
        отсортированный список длиной top_n
        """
        ...