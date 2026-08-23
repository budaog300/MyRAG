from typing import List
from src.rag.ai.providers import BaseEmbedderProvider, BaseAIProvider


class EmbeddingsProvider(BaseAIProvider, BaseEmbedderProvider):
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        payload = {
            "model": self.config.model_name,
            "input": texts,
            **self.config.extra_params,
        }

        data = await self._post(payload)
        return [item["embedding"] for item in data["data"]]

    async def embed_query(self, text: str) -> List[float]:
        res = await self.embed_documents([text])
        return res[0]