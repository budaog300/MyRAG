import httpx
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from src.core.ai_config import ModelConfig


class BaseAIProvider:
    """Базовый класс для всех OpenAI-совместимых провайдеров"""
    def __init__(self, config: ModelConfig):
        self.config = config
        self.headers = {"Content-Type": "application/json"}
        if config.api_key:
            self.headers["Authorization"] = f"Bearer {config.api_key}"

    async def _post(self, payload: dict) -> dict:
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(
                    self.config.api_url, 
                    json=payload, 
                    headers=self.headers
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            print(f"Ошибка при генерации ответа: {e}")
            raise e


class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        temperature: float = 0.3, 
        max_tokens: int = 512
    ) -> str:
        pass


class BaseEmbeddingsProvider(ABC):
    @abstractmethod
    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        pass

    @abstractmethod
    async def embed_query(self, text: str) -> List[float]:
        pass


class BaseRerankerProvider(ABC):
    @abstractmethod
    async def rerank(
        self, query: str, documents: List[str], top_n: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Возвращает список словарей вида [{'index': int, 'score': float, 'text': str}]"""
        pass


class BaseVLMProvider(ABC):
    @abstractmethod
    async def analyze_image(
        self, image_bytes: bytes, prompt: str, mime_type: str = "image/jpeg"
    ) -> str:
        pass