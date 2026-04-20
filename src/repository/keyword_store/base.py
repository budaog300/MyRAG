from abc import ABC, abstractmethod
from typing import List, Dict, Any
from src.schemas.schemas import RAGDocument


class KeywordBaseRepository(ABC):
    def __init__(self):
        self.client = None

    @abstractmethod
    async def create_index(self, index: str): ...

    @abstractmethod
    async def get_indices(self): ...

    @abstractmethod
    async def delete_index(self, index: str): ...

    @abstractmethod
    async def clear_index(self, index: str): ...

    @abstractmethod
    async def index_documents(self, index: str, items: List[Dict[str, Any]]): ...

    @abstractmethod
    async def search(self, query: str, index: str, **kwargs) -> List[RAGDocument]: ...

    @abstractmethod
    async def close(): ...
