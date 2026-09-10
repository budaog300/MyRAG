import logging
from typing import Optional, TypeVar
from collections.abc import Callable
from src.core.ai_config import ModelConfig, VLMConfig, AIServiceConfig, AIProviderConfig
from src.rag.ai.providers import *
from src.core.exceptions.ai_service_exceptions import (    
    AIServiceInitializationError
)
from src.core.config import settingsAI

logger = logging.getLogger(__name__)
T = TypeVar("T")


class AIService:
    """Центральный сервис-фабрика для управления AI-провайдерами (LLM, Embedder, VLM, Reranker)."""

    def __init__(self, config: AIServiceConfig | None = None):
        self.config = config or settingsAI.build_ai_config()

        llm, llm_fallback = self._init_provider_pair(self.config.llm, self._init_llm)
        embedder, embedder_fallback = self._init_provider_pair(self.config.embedder, self._init_embedder)
        vlm, vlm_fallback = self._init_provider_pair(self.config.vlm, self._init_vlm)
        reranker, reranker_fallback = self._init_provider_pair(self.config.reranker, self._init_reranker)

        self.llm = FallbackProvider(llm, llm_fallback) if llm else None
        self.embedder = FallbackProvider(embedder, embedder_fallback) if embedder else None
        self.vlm = FallbackProvider(vlm, vlm_fallback) if vlm else None
        self.reranker = FallbackProvider(reranker, reranker_fallback) if reranker else None

    def _init_provider_pair(self, config: AIProviderConfig | None, init_func: Callable[[ModelConfig], T]) -> tuple[Optional[T], Optional[T]]:
        if not config:
            return None, None

        primary = init_func(config.primary) if config.primary else None
        fallback = init_func(config.fallback) if config.fallback else None

        return primary, fallback

    def _init_llm(self, config: ModelConfig) -> BaseLLMProvider:
        try:
            provider = LLMProvider(config)
            logger.info("LLM провайдер успешно инициализирован в режиме %s", config.mode)
            return provider
        except AIProviderError:
            raise
        except Exception as exc:
            logger.error("Ошибка инициализации LLM провайдера: %s", exc, exc_info=True)
            raise AIServiceInitializationError(service_name="LLM", details=str(exc)) from exc

    def _init_embedder(self, config: ModelConfig) -> BaseEmbedderProvider:
        try:
            provider = EmbedderProvider(config)
            logger.info("Embedder провайдер успешно инициализирован в режиме %s", config.mode)
            return provider
        except AIProviderError:
            raise
        except Exception as exc:
            logger.error("Ошибка инициализации Embedder провайдера: %s", exc, exc_info=True)
            raise AIServiceInitializationError(service_name="Embedder", details=str(exc)) from exc

    def _init_vlm(self, config: VLMConfig) -> BaseVLMProvider:
        try:
            provider = VLMProvider(config)
            logger.info("VLM провайдер успешно инициализирован в режиме %s", config.mode)
            return provider
        except AIProviderError:
            raise
        except Exception as exc:
            logger.error("Ошибка инициализации VLM провайдера: %s", exc, exc_info=True)
            raise AIServiceInitializationError(service_name="VLM", details=str(exc)) from exc

    def _init_reranker(self, config: ModelConfig) -> BaseRerankerProvider:
        try:
            provider = RerankerProvider(config)
            logger.info("Reranker провайдер успешно инициализирован в режиме %s", config.mode)
            return provider
        except AIProviderError:
            raise
        except Exception as exc:
            logger.error("Ошибка инициализации Reranker провайдера: %s", exc, exc_info=True)
            raise AIServiceInitializationError(service_name="Reranker", details=str(exc)) from exc