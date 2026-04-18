from typing import List

from src.generation.llm_generator_v1 import LLMGenerator
from src.repository import VectorBaseRepository
from src.rag import Rerank


class RAGService:
    def __init__(
        self,
        repo: VectorBaseRepository,
        # processors: List | None,
        model: str = "openai/gpt-4o-mini",
    ):
        self.repo = repo
        # self.processors = processors or []
        self.reranker = Rerank()
        self.llm = LLMGenerator(model=model)

    async def full_step(
        self,
        query: str,
        collection_name: str,
        *args,
        **kwargs,
    ) -> str:
        retrieved_docs = await self.repo.search_points(query, collection_name)
        # print(context)

        reranked_docs = self.reranker.compress_documents(query, retrieved_docs)
        context = [doc.content for doc in reranked_docs]
        answer = await self.llm.generate(
            query,
            context,
            *args,
            **kwargs,
        )
        return answer

    async def run(
        self,
        query: str,
        collection_name: str,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> dict:
        return {
            "answer": await self.full_step(
                query, collection_name, temperature, max_tokens
            )
        }
