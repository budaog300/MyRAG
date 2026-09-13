from dataclasses import dataclass

from src.db.repositories.collections import CollectionRepository
from src.db.repositories.documents import DocumentRepository
from src.db.repositories.query_history import QueryHistoryRepository


@dataclass
class RepositoryContainer:
    collection_repo: CollectionRepository
    document_repo: DocumentRepository
    query_history_repo: QueryHistoryRepository

    async def ping(self) -> bool:
        return await self.collection_repo.ping()