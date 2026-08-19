from typing import List, Optional
from src.ai.base import BaseRerankerProvider
from src.schemas import RAGDocument  # замените на ваш импорт RAGDocument


class RAGDocumentReranker:
    """
    Высокоуровневый компонент RAG. 
    Принимает RAGDocument, вызывает провайдер реранкинга 
    и возвращает сжатый/отсортированный список с обновленными метаданными.
    """

    def __init__(
        self, 
        reranker: Optional[BaseRerankerProvider] = None, 
        top_n: int = 5
    ):
        self.reranker = reranker
        self.top_n = top_n

    async def compress_documents(
        self,
        query: str,
        documents: List[RAGDocument],
        top_n: Optional[int] = None,
    ) -> List[RAGDocument]:
        """
        Реранкает документы и обновляет их rerank_score в metadata.
        """
        if not documents:
            return []

        limit = top_n if top_n is not None else self.top_n

        # Фолбэк: если реранкер отключен в конфиге (None), 
        # просто возвращаем первые N документов без изменений
        if self.reranker is None:
            return documents[:limit]

        # 1. Извлекаем чистый текст из RAGDocument
        texts = [doc.content for doc in documents]

        # 2. Делаем запрос к низкоуровневому провайдеру
        results = await self.reranker.rerank(
            query=query, 
            documents=texts, 
            top_n=limit
        )

        # 3. Собираем итоговый список RAGDocument с обновленными метаданными
        ranked_docs: List[RAGDocument] = []
        for item in results:
            doc_idx = item["index"]
            score = item["score"]

            doc = documents[doc_idx]
            doc.metadata["rerank_score"] = score
            ranked_docs.append(doc)

        return ranked_docs