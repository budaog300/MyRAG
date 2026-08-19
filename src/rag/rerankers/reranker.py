from typing import List, Optional
from src.rag.ai.providers import BaseRerankerProvider
from src.rag.schemas.document import RAGDocument


class Reranker:
    """
    Высокоуровневый компонент RAG. 
    Принимает RAGDocument, вызывает провайдер реранкинга 
    и возвращает сжатый/отсортированный список с обновленными метаданными
    """

    def __init__(
        self, 
        reranker_provider: Optional[BaseRerankerProvider] = None, 
        top_n: int = 5
    ):
        self.reranker = reranker_provider
        self.top_n = top_n

    async def compress_documents(
        self,
        query: str,
        documents: List[RAGDocument],
        top_n: Optional[int] = None,
    ) -> List[RAGDocument]:
        if not documents:
            return []

        limit = top_n if top_n is not None else self.top_n

        if self.reranker is None:
            return documents[:limit]

        texts = [doc.content for doc in documents]

        reranked_docs = await self.reranker.rerank(
            query=query, 
            documents=texts, 
            top_n=limit
        )
        print(f"{reranked_docs=}")
        ranked_docs: List[RAGDocument] = []
        for item in reranked_docs:
            doc_idx = item["index"]
            score = item["score"]

            doc = documents[doc_idx]
            doc.metadata["rerank_score"] = score
            ranked_docs.append(doc)

        return ranked_docs