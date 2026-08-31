from dataclasses import dataclass

from src.db.repositories.collections import CollectionRepository
from src.db.repositories.documents import DocumentRepository


@dataclass
class RepositoryContainer:
    collection_repo: CollectionRepository
    document_repo: DocumentRepository

    async def ping(self) -> bool:
        return await self.collection_repo.ping()