from abc import ABC, abstractmethod
from typing import List
from src.schemas.schemas import RAGDocument


class BaseRetriever(ABC):
    @abstractmethod
    async def retrieve(self, query: str, collection_name: str) -> List[RAGDocument]: ...
