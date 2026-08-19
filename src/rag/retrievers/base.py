from abc import ABC, abstractmethod
from typing import List
from src.rag.schemas.document import RAGDocument


class BaseRetriever(ABC):

    @abstractmethod
    async def retrieve(
        self, query: str, collection_name: str, **kwargs
    ) -> List[RAGDocument]: ...
