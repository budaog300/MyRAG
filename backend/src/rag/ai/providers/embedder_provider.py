import logging
from typing import List
from src.rag.ai.providers import BaseEmbedderProvider, BaseAIProvider
from src.core.exceptions.provider_exceptions import EmbedderError

logger = logging.getLogger(__name__)


class EmbedderProvider(BaseAIProvider, BaseEmbedderProvider):
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        payload = {
            "model": self.config.model_name,
            "input": texts,
            **self.config.extra_params,
        }

        data = await self._post(payload)
        
        try:
            embeddings = [item["embedding"] for item in data["data"]]            
            return embeddings
        except (KeyError, TypeError) as e:
            raise EmbedderError(f"Не удалось извлечь эмбеддинги из ответа: {e}")

    async def embed_query(self, text: str) -> List[float]:
        res = await self.embed_documents([text])
        if not res:
            logger.error("Получен пустой список эмбеддингов для query")
            raise EmbedderError("Получен пустой список эмбеддингов для запроса")
        return res[0]