import asyncio
from typing import List

from src.retrieval import BaseRetriever
from src.schemas.schemas import RAGDocument


class HybridRetriever(BaseRetriever):
    def __init__(self, vector_retriever: BaseRetriever, bm25_retriever: BaseRetriever):
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever

    async def retrieve(
        self,
        query: str,
        collection_name: str,
        retrieve_limit: int = 30,
        merge_limit: int = 10,
    ) -> List[RAGDocument]:
        vector_task = self.vector_retriever.retrieve(
            query, collection_name, limit=retrieve_limit
        )
        bm25_task = self.bm25_retriever.retrieve(
            query, collection_name, limit=retrieve_limit
        )
        vector_docs, bm25_docs = await asyncio.gather(vector_task, bm25_task)
        return await self.merge_rrf(vector_docs, bm25_docs, limit=merge_limit)

    async def merge_rrf(
        self,
        vector_docs: List[RAGDocument],
        bm25_docs: List[RAGDocument],
        limit: int = 10,
    ) -> List[RAGDocument]:
        k = 60
        scores = {}
        for source in [vector_docs, bm25_docs]:
            for rank, doc in enumerate(source, start=1):
                if doc.id not in scores:
                    doc.metadata["rrf_score"] = 0.0
                    scores[doc.id] = doc
                scores[doc.id].metadata["rrf_score"] += 1 / (k + rank)
        all_docs = list(scores.values())
        result = sorted(all_docs, key=lambda x: x.metadata["rrf_score"], reverse=True)
        print([doc.id for doc in result])
        return result[:limit]

    async def merge_usual(
        self, vector_docs: List[RAGDocument], bm25_docs: List[RAGDocument]
    ) -> List[RAGDocument]:
        unique_docs = {}
        for source in [vector_docs, bm25_docs]:
            for doc in source:
                if doc.id not in unique_docs:
                    unique_docs[doc.id] = doc

        return list(unique_docs.values())
