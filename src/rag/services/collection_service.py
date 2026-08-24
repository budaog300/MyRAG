import asyncio
from typing import List, Dict, Any, Optional
from src.rag.repositories import BaseKeywordRepository, BaseVectorRepository
from src.rag.schemas.document import CollectionSchema


class CollectionService:
    def __init__(self, vector_repo: BaseVectorRepository, keyword_repo: BaseKeywordRepository):
        self.vector_repo = vector_repo
        self.keyword_repo = keyword_repo

    async def create_collection(self, name: str, size: int = 1024, distance: str = "COSINE") -> None:
        await asyncio.gather(
            self.vector_repo.create_collection(collection_name=name, size=size, distance=distance),
            self.keyword_repo.create_index(index=name)
        )

    async def get_collections(self, include_parents: bool = False) -> List[CollectionSchema]:
        return await self.vector_repo.get_collections(include_parents=include_parents)

    async def get_collection_details(self, name: str) -> Dict[str, Any]:
        vector_repo_info, keyword_repo_info = await asyncio.gather(
            self.vector_repo.get_collection_details(name),
            self.keyword_repo.get_index_details(name)
        )
        return {
            "name": name,
            "vector_repo_info": vector_repo_info,
            "keyword_repo_info": keyword_repo_info
        }

    async def delete_document_by_file_id(self, collection_name: str, file_id: str) -> None:
        await asyncio.gather(
            self.vector_repo.delete_by_filter(collection_name, key="metadata.file_id", value=file_id),
            self.vector_repo.delete_by_filter(f"{collection_name}_parents", key="metadata.file_id", value=file_id),
            self.keyword_repo.delete_by_filter(collection_name, field="metadata.file_id", value=file_id)
        )

    async def clear_collection(self, name: str) -> None:
        await asyncio.gather(
            self.vector_repo.clear_collection(name),
            self.vector_repo.clear_collection(f"{name}_parents"),
            self.keyword_repo.clear_index(name)
        )

    async def delete_collection(self, name: str) -> None:
        await asyncio.gather(
            self.vector_repo.delete_collection(name),
            self.vector_repo.delete_collection(f"{name}_parents"),
            self.keyword_repo.delete_index(name)
        )