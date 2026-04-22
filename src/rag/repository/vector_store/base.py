from typing import Any, Dict, List
from abc import ABC, abstractmethod
from src.rag.schemas.document import RAGDocument


class VectorBaseRepository(ABC):
    def __init__(self):
        self.client = None

    @abstractmethod
    async def create_collection(
        self, collection_name: str, size: int = 384, distance: str = "COSINE", **kwargs
    ): ...

    @abstractmethod
    async def get_collections(self): ...

    @abstractmethod
    async def get_collection_details(self): ...

    @abstractmethod
    async def clear_collection(self, collection_name: str): ...

    @abstractmethod
    async def delete_collection(self, collection_name: str): ...

    @abstractmethod
    async def upsert(
        self,
        collection_name: str,
        items: List[Dict[str, Any]],
        model: str = "sentence-transformers/all-MiniLM-L6-v2",
        **kwargs
    ): ...

    @abstractmethod
    async def search_points(
        self,
        query: str,
        collection_name: str,
        model: str = "sentence-transformers/all-MiniLM-L6-v2",
        limit: int = 10,
        **kwargs
    ) -> List[RAGDocument]: ...

    @abstractmethod
    async def close(self): ...
