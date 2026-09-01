import httpx
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

from src.core.ai_config import ModelConfig
from src.rag.schemas.document import RAGDocument
from src.core.exceptions.provider_exceptions import (
    AIProviderAuthError,
    AIProviderError,
    AIProviderRateLimitError,
    AIProviderTimeoutError
)


class BaseAIProvider:
    """Базовый класс для всех провайдеров"""
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
                
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            detail = e.response.text
            if status_code in (401, 403):
                raise AIProviderAuthError(detail)
            elif status_code == 429:
                raise AIProviderRateLimitError(detail)
            else:
                raise AIProviderError(f"HTTP ошибка {status_code}: {detail}", status_code=502)
                
        except httpx.TimeoutException as e:
            raise AIProviderTimeoutError(str(e))
            
        except httpx.RequestError as e:
            raise AIProviderError(f"Сетевая ошибка при запросе к AI-провайдеру: {e}")
            
        except Exception as e:
            raise AIProviderError(f"Непредвиденная ошибка AI-провайдера: {e}")


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


class BaseEmbedderProvider(ABC):
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

    @abstractmethod
    async def compress_documents(
        self,
        query: str,
        documents: List[RAGDocument],
        top_k: Optional[int] = None,
    ) -> List[RAGDocument]:
        ...


class BaseVLMProvider(ABC):
    @abstractmethod
    async def analyze_image(
        self, image_bytes: bytes, prompt: str, mime_type: str = "image/jpeg"
    ) -> str:
        pass