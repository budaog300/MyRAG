from typing import List, Optional, Dict, Any

from src.rag.retrievers import BaseRetriever
from src.rag.services.ai_service import AIService
from src.rag.repositories.context_enricher import ContextEnricher


class RAGService:
    def __init__(
        self,
        ai_service: AIService,
        retriever: BaseRetriever,
        enricher: Optional[ContextEnricher] = None
    ):
        self.ai_service = ai_service
        self.retriever = retriever
        self.enricher = enricher

    async def _full_step(
        self,
        query: str,
        collection_name: str,
        retrieve_limit: int = 50,
        merge_limit: int = 20,
        top_n: int = 5,
        system_prompt: Optional[str] = None,
        **kwargs,
    ) -> Optional[str]:
        docs = await self.retriever.retrieve(
            query,
            collection_name,
            retrieve_limit=retrieve_limit,
            merge_limit=merge_limit,
        )
        print(docs)
        print(len(docs))
        if self.ai_service.reranker:
            docs = await self.ai_service.reranker.compress_documents(
                query=query, 
                documents=docs, 
                top_n=top_n
            )
        print(f"reranked docs ({len(docs)})", docs)
        if self.enricher:
            docs = await self.enricher.enrich(docs, collection_name)
        print(f"enriched docs ({len(docs)})", docs)
        context_text = "\n\n---\n\n".join([doc.content for doc in docs[:top_n]])
        
        prompt = (
            f"Используй следующий контекст для ответа на вопрос.\n\n"
            f"КОНТЕКСТ:\n{context_text}\n\n"
            f"ВОПРОС: {query}"
        )

        system_prompt = system_prompt or self.ai_service.config.llm.prompt

        answer = await self.ai_service.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            **kwargs,
        )
        return answer or None

    async def run(
        self,
        query: str,
        collection_name: str,
        retrieve_limit: int = 30,
        merge_limit: int = 10,
        top_n: int = 5,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        answer = await self._full_step(
            query=query,
            collection_name=collection_name,
            retrieve_limit=retrieve_limit,
            merge_limit=merge_limit,
            top_n=top_n,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return {"answer": answer}
