from typing import List
from src.rag.repositories import BaseVectorRepository
from src.rag.schemas.document import RAGDocument
from src.core.exceptions.repo_exceptions import (
    CollectionNotFoundError,
    ParentDocumentNotFoundError,
    VectorDatabaseError,
)


class ContextEnricher:
    def __init__(self, repo: BaseVectorRepository):
        self.repo = repo

    async def enrich(self, docs: List[RAGDocument], collection_name: str) -> List[RAGDocument]:
        if not docs:
            return []

        parent_ids = list({
            doc.metadata["parent_id"] 
            for doc in docs 
            if doc.metadata.get("parent_id")
        })

        if not parent_ids:
            return docs

        parents_collection_name = f"{collection_name}_parents"

        try:
            parents = await self.repo.get_documents_by_ids(
                collection_name=parents_collection_name,
                ids=parent_ids,
            )
        except CollectionNotFoundError:
            raise CollectionNotFoundError(parents_collection_name)
        except VectorDatabaseError as e:
            raise

        parents_map = {p.id: p for p in parents}

        for doc in docs:
            p_id = doc.metadata.get("parent_id")
            if not p_id:
                continue

            parent_doc = parents_map.get(p_id)
            if not parent_doc:
                raise ParentDocumentNotFoundError(parent_id=p_id, collection_name=collection_name)

            doc.content = parent_doc.content
            doc.metadata.update(parent_doc.metadata)
            doc.is_parent = getattr(parent_doc, "is_parent", True)

        return docs