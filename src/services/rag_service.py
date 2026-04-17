from src.generation.llm_generator_v1 import LLMGenerator
from src.repository import VectorBaseRepository


class RAGService:
    def __init__(self, repo: VectorBaseRepository, model: str = "openai/gpt-4o-mini"):
        self.llm = LLMGenerator(model=model)
        self.repo = repo

    async def full_step(
        self,
        query: str,
        collection_name: str,
        *args,
        **kwargs,
    ) -> str:
        context = await self.repo.search_points(query, collection_name)
        # print(context)
        answer = await self.llm.generate(
            query,
            list(map(lambda x: x.payload["content"], context.points)),
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
