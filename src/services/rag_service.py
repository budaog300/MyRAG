from typing import List

from src.generation.llm_generator_v1 import LLMGenerator
from src.retrieval import BaseRetriever
from src.rag import Rerank


class RAGService:
    def __init__(
        self,
        retriever: BaseRetriever,
        model: str = "openai/gpt-4o-mini",
    ):
        self.retriever = retriever
        self.reranker = Rerank()
        self.llm = LLMGenerator(model=model)

    async def full_step(
        self,
        query: str,
        collection_name: str,
        retrieve_limit: int = 30,
        merge_limit: int = 10,
        **kwargs,
    ) -> str:
        retrieved_docs = await self.retriever.retrieve(
            query,
            collection_name,
            retrieve_limit=retrieve_limit,
            merge_limit=merge_limit,
        )
        # print(context)

        reranked_docs = self.reranker.compress_documents(query, retrieved_docs)
        context = [doc.content for doc in reranked_docs]
        answer = await self.llm.generate(
            query,
            context,
            **kwargs,
        )
        return answer

    async def run(
        self,
        query: str,
        collection_name: str,
        retrieve_limit: int = 30,
        merge_limit: int = 10,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> dict:
        return {
            "answer": await self.full_step(
                query=query,
                collection_name=collection_name,
                temperature=temperature,
                max_tokens=max_tokens,
                retrieve_limit=retrieve_limit,
                merge_limit=merge_limit,
            )
        }
