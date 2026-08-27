from typing import Any, Dict, List, Set, Tuple
from uuid import UUID
from abc import ABC, abstractmethod
from src.rag.schemas.document import RAGDocument


class BaseVectorRepository(ABC):
    def __init__(self):
        self.client = None

    @abstractmethod
    async def create_collection(
        self, collection_name: str, size: int = 384, distance: str = "COSINE", **kwargs
    ): ...

    @abstractmethod
    async def get_collections(self, include_parents: bool = False): ...

    @abstractmethod
    async def get_collection_details(self): ...

    @abstractmethod
    async def clear_collection(self, collection_name: str): ...

    @abstractmethod
    async def delete_collection(self, collection_name: str): ...

    @abstractmethod
    async def delete_by_filter(self, collection_name: str, key: str, value: Any) -> None: ...

    @abstractmethod
    async def upsert(
        self,
        collection_name: str,
        items: List[Dict[str, Any]],
        # model: str = "sentence-transformers/all-MiniLM-L6-v2",
        **kwargs
    ): ...

    @abstractmethod
    async def search_points(
        self,
        query: str,
        collection_name: str,
        # model: str = "sentence-transformers/all-MiniLM-L6-v2",
        limit: int = 30,
        **kwargs
    ) -> List[RAGDocument]: ...

    @abstractmethod
    async def get_documents_by_ids(
        self,
        collection_name: str,
        ids: List[str],
        **kwargs
    ) -> List[RAGDocument]: ...

    @abstractmethod
    async def get_chunks(
        self,
        collection_name: str,
        document_id: UUID | None = None,
        limit: int = 100,
        offset: str | None = None,
    ) -> Tuple[List[RAGDocument], str | None]:
        ...

    @abstractmethod
    async def get_s3_keys_by_document_id(
        self,
        collection_name: str,
        document_id: UUID,
    ) -> Set[str]:
        ...

    @abstractmethod
    async def get_s3_keys(
        self,
        collection_name: str,
    ) -> Set[str]:
        ...

    @abstractmethod
    async def ping(self) -> bool: ...
    
    @abstractmethod
    async def close(self): ...
