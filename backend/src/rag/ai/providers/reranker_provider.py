import logging
from typing import List, Dict, Any, Optional
from src.rag.ai.providers import BaseRerankerProvider, BaseAIProvider
from src.rag.schemas.document import RAGDocument
from src.core.exceptions.provider_exceptions import AIProviderResponseParseError, RerankerError

logger = logging.getLogger(__name__)


class RerankerProvider(BaseAIProvider, BaseRerankerProvider):
    async def rerank(
        self, query: str, documents: List[str], top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        if not documents:
            logger.warning("Reranker request skipped: documents list is empty")
            return []
            
        payload = {
            "model": self.config.model_name,
            "query": query,
            "documents": documents,
            "top_k": top_k or len(documents),
            **self.config.extra_params,
        }

        data = await self._post(payload)

        try:
            results = []
            items = data.get("results", data.get("data"))
            if items is None:
                raise AIProviderResponseParseError("Поле с результатами реранкинга не найдено")

            for item in items:
                results.append({
                    "index": item["index"],
                    "score": item.get("relevance_score", item.get("score", 0.0))
                })
            logger.info("Reranker response: model=%s, results=%d", self.config.model_name, len(results))
            return results
        except (KeyError, TypeError, IndexError) as e:
            logger.error("Reranker response parsing failed: model=%s, error=%s", self.config.model_name, e)
            raise RerankerError(f"Ошибка парсинга результатов реранкинга: {e}")

    async def compress_documents(
        self,
        query: str,
        documents: List[RAGDocument],
        top_k: Optional[int] = None,
    ) -> List[RAGDocument]:
        if not documents:
            logger.warning("Reranker request skipped: documents list is empty")
            return []

        limit = top_k or len(documents)
        texts = [doc.content for doc in documents]

        results = await self.rerank(query=query, documents=texts, top_k=limit)
        
        ranked_docs: List[RAGDocument] = []
        for item in results:
            try:
                doc: RAGDocument = documents[item["index"]]
                doc.metadata["rerank_score"] = item["score"]
                ranked_docs.append(doc)
            except IndexError:
                raise RerankerError(f"Индекс {item['index']} из ответа реранкера выйдет за пределы списка документов")

        return ranked_docs[:limit]