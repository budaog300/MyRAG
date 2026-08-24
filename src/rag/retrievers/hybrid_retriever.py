import logging
import asyncio
from typing import List

from src.rag.retrievers import BaseRetriever
from src.rag.schemas.document import RAGDocument
from src.core.exceptions.retriever_exceptions import HybridRetrieverError

logger = logging.getLogger(__name__)


class HybridRetriever(BaseRetriever):
    def __init__(self, retrievers: List[BaseRetriever]):
        if not retrievers:
            raise HybridRetrieverError("Список ретриверов не может быть пустым")
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
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        valid_results: List[List[RAGDocument]] = []
        errors = []

        for res in responses:
            if isinstance(res, Exception):
                logger.error(f"Один из ретриверов упал во время гибридного поиска: {res}", exc_info=res)
                errors.append(res)
            elif isinstance(res, list):
                valid_results.append(res)

        if len(errors) == len(self.retrievers):
            raise HybridRetrieverError(f"Все источники поиска вернули ошибку: {errors}")

        return await self._merge_rrf(valid_results, limit=merge_limit)
    
    async def _merge_rrf(
        self,
        sources: List[List[RAGDocument]],
        limit: int = 10,
    ) -> List[RAGDocument]:
        if not sources:
            return []
        
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

    async def _merge_usual(self, sources: List[List[RAGDocument]]) -> List[RAGDocument]:
        unique_docs = {}
        for source in sources:
            for doc in source:
                if doc.id not in unique_docs:
                    unique_docs[doc.id] = doc

        return list(unique_docs.values())
