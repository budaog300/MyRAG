import asyncio
from typing import List

from src.retrieval import BaseRetriever
from src.schemas.schemas import RAGDocument


class HybridRetriever(BaseRetriever):
    def __init__(self, retrievers: List[BaseRetriever]):
        self.retrievers = retrievers

    async def retrieve(
        self,
        query: str,
        collection_name: str,
        retrieve_limit: int = 30,
        merge_limit: int = 10,
    ) -> List[RAGDocument]:
        tasks = [
            r.retrieve(query, collection_name, limit=retrieve_limit)
            for r in self.retrievers
        ]
        results = await asyncio.gather(*tasks)
        return await self.merge_rrf(results, limit=merge_limit)

    async def merge_rrf(
        self,
        sources: List[List[RAGDocument]],
        limit: int = 10,
    ) -> List[RAGDocument]:
        k = 60
        scores = {}
        for source in sources:
            for rank, doc in enumerate(source, start=1):
                if doc.id not in scores:
                    doc.metadata["rrf_score"] = 0.0
                    scores[doc.id] = doc
                scores[doc.id].metadata["rrf_score"] += 1 / (k + rank)
        result = sorted(
            scores.values(), key=lambda x: x.metadata["rrf_score"], reverse=True
        )
        return result[:limit]

    async def merge_usual(self, sources: List[List[RAGDocument]]) -> List[RAGDocument]:
        unique_docs = {}
        for source in sources:
            for doc in source:
                if doc.id not in unique_docs:
                    unique_docs[doc.id] = doc

        return list(unique_docs.values())
