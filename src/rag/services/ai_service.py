import logging
from typing import Optional
from src.core.ai_config import ModelConfig, AIServiceConfig, EngineMode
from src.rag.ai.providers import *
from src.core.exceptions.ai_service_exceptions import (    
    AIServiceInitializationError,
    UnsupportedEngineModeError,
)
from src.core.exceptions.provider_exceptions import AIProviderNotConfiguredError

logger = logging.getLogger(__name__)


class AIService:
    """Центральный сервис-фабрика для управления AI-провайдерами (LLM, Embedder, VLM, Reranker)."""

    def __init__(self, config: AIServiceConfig):
        self.config = config

        self.llm: Optional[BaseLLMProvider] = (
            self._init_llm(config.llm) if config.llm and getattr(config.llm, "enabled", True) else None
        )

        self.embedder: Optional[BaseEmbedderProvider] = (
            self._init_embedder(config.embedder) if config.embedder and getattr(config.embedder, "enabled", True) else None
        )

        self.vlm: Optional[BaseVLMProvider] = (
            self._init_vlm(config.vlm) if config.vlm and getattr(config.vlm, "enabled", True) else None
        )

        self.reranker: Optional[BaseRerankerProvider] = (
            self._init_reranker(config.reranker) if config.reranker and getattr(config.reranker, "enabled", True) else None
        )

    def _init_llm(self, config: ModelConfig) -> BaseLLMProvider:
        if config.mode not in (EngineMode.API, EngineMode.LOCAL):
            raise UnsupportedEngineModeError(service_name="LLM", mode=str(config.mode))
        try:
            provider = LLMProvider(config)
            logger.info("LLM провайдер успешно инициализирован в режиме %s", config.mode)
            return provider
        except Exception as exc:
            logger.error("Ошибка инициализации LLM провайдера: %s", exc)
            raise AIServiceInitializationError(service_name="LLM", details=str(exc)) from exc

    def _init_embedder(self, config: ModelConfig) -> BaseEmbedderProvider:
        if config.mode not in (EngineMode.API, EngineMode.LOCAL):
            raise UnsupportedEngineModeError(service_name="Embedder", mode=str(config.mode))
        try:
            provider = EmbedderProvider(config)
            logger.info("Embedder провайдер успешно инициализирован в режиме %s", config.mode)
            return provider
        except Exception as exc:
            logger.error("Ошибка инициализации Embedder провайдера: %s", exc)
            raise AIServiceInitializationError(service_name="Embedder", details=str(exc)) from exc

    def _init_vlm(self, config: ModelConfig) -> BaseVLMProvider:
        if config.mode not in (EngineMode.API, EngineMode.LOCAL):
            raise UnsupportedEngineModeError(service_name="VLM", mode=str(config.mode))
        try:
            provider = VLMProvider(config)
            logger.info("VLM провайдер успешно инициализирован в режиме %s", config.mode)
            return provider
        except Exception as exc:
            logger.error("Ошибка инициализации VLM провайдера: %s", exc)
            raise AIServiceInitializationError(service_name="VLM", details=str(exc)) from exc

    def _init_reranker(self, config: ModelConfig) -> BaseRerankerProvider:
        if config.mode not in (EngineMode.API, EngineMode.LOCAL):
            raise UnsupportedEngineModeError(service_name="Reranker", mode=str(config.mode))
        try:
            provider = RerankerProvider(config)
            logger.info("Reranker провайдер успешно инициализирован в режиме %s", config.mode)
            return provider
        except Exception as exc:
            logger.error("Ошибка инициализации Reranker провайдера: %s", exc)
            raise AIServiceInitializationError(service_name="Reranker", details=str(exc)) from exc

    def get_llm(self) -> BaseLLMProvider:
        if not self.llm:
            raise AIProviderNotConfiguredError(service_name="LLM")
        return self.llm

    def get_embedder(self) -> BaseEmbedderProvider:
        if not self.embedder:
            raise AIProviderNotConfiguredError(service_name="Embedder")
        return self.embedder

    def get_vlm(self) -> BaseVLMProvider:
        if not self.vlm:
            raise AIProviderNotConfiguredError(service_name="VLM")
        return self.vlm

    def get_reranker(self) -> BaseRerankerProvider:
        if not self.reranker:
            raise AIProviderNotConfiguredError(service_name="Reranker")
        return self.reranker