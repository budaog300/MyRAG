from typing import List
from src.rag.repositories import BaseVectorRepository
from src.rag.schemas.document import RAGDocument


class ContextEnricher:
    def __init__(self, repo: BaseVectorRepository):
        self.repo = repo

    async def enrich(self, docs: List[RAGDocument], collection_name: str) -> List[RAGDocument]:
        parent_ids = list({
            doc.metadata["parent_id"] 
            for doc in docs 
            if doc.metadata.get("parent_id")
        })

        if not parent_ids:
            return docs

        parents = await self.repo.get_documents_by_ids(
            collection_name=f"{collection_name}_parents",
            ids=parent_ids,
        )
        parents_map = {p.id: p for p in parents}

        for doc in docs:
            p_id = doc.metadata.get("parent_id")
            if p_id and p_id in parents_map:
                doc.content = parents_map[p_id].content

        return docs