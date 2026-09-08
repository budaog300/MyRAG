import httpx
import logging
import time
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

logger = logging.getLogger(__name__)


class BaseAIProvider:
    """Базовый класс для всех провайдеров"""
    def __init__(self, config: ModelConfig):
        self.config = config
        self.headers = {"Content-Type": "application/json"}
        if config.api_key:
            self.headers["Authorization"] = f"Bearer {config.api_key}"

    async def _post(self, payload: dict) -> dict:
        start_time = time.perf_counter()
        logger.debug("AI request: model=%s, url=%s", self.config.model_name, self.config.api_url)
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(
                    self.config.api_url, 
                    json=payload,
                    headers=self.headers
                )
                response.raise_for_status()
                elapsed = time.perf_counter() - start_time
                logger.info("AI request completed: model=%s, status=%d, time=%.2fs", self.config.model_name, response.status_code, elapsed)
                return response.json()
                
        except httpx.HTTPStatusError as e:
            elapsed = time.perf_counter() - start_time
            status_code = e.response.status_code
            detail = e.response.text
            logger.error("AI HTTP error: model=%s, status=%d, time=%.2fs, detail=%s", self.config.model_name, status_code, elapsed, detail)
            if status_code in (401, 403):
                raise AIProviderAuthError(detail)
            elif status_code == 429:
                raise AIProviderRateLimitError(detail)
            else:
                raise AIProviderError(f"HTTP ошибка {status_code}: {detail}", status_code=502)
                
        except httpx.TimeoutException as e:
            elapsed = time.perf_counter() - start_time
            logger.error("AI timeout: model=%s, time=%.2fs", self.config.model_name, elapsed)
            raise AIProviderTimeoutError(str(e))
            
        except httpx.RequestError as e:
            elapsed = time.perf_counter() - start_time
            logger.error("AI network error: model=%s, time=%.2fs, error=%s", self.config.model_name, elapsed, e)
            raise AIProviderError(f"Сетевая ошибка при запросе к AI-провайдеру: {e}")
            
        except Exception as e:
            elapsed = time.perf_counter() - start_time
            logger.exception("Unexpected AI provider error: model=%s, time=%.2fs", self.config.model_name, elapsed)
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