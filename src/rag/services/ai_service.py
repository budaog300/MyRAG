from typing import Optional
from src.core.ai_config import ModelConfig, AIServiceConfig, EngineMode
from src.rag.ai.providers import *


class AIService:
    def __init__(self, config: AIServiceConfig):
        self.config = config
        
        # Инициализация LLM
        self.llm: Optional[BaseLLMProvider] = (
            self._init_llm(config.llm)
            if config.llm
            else None
        )
        
        # Инициализация Embeddings
        self.embeddings: Optional[BaseEmbeddingsProvider] = (
            self._init_embeddings(config.embeddings)
            if config.embeddings
            else None
        )
        
        # Инициализация VLM
        self.vlm: Optional[BaseVLMProvider] = (
            self._init_vlm(config.vlm)
            if config.vlm
            else None
        )
        
        # Инициализация Reranker
        self.reranker: Optional[BaseRerankerProvider] = (
            self._init_reranker(config.reranker)
            if config.reranker
            else None
        )

    def _init_llm(self, config: ModelConfig) -> BaseLLMProvider:
        if config.mode in (EngineMode.API, EngineMode.LOCAL):
            return LLMProvider(config)
        raise ValueError(f"Неподдерживаемый режим для LLM: {config.mode}")

    def _init_embeddings(self, config: ModelConfig) -> BaseEmbeddingsProvider:
        if config.mode in (EngineMode.API, EngineMode.LOCAL):
            return EmbeddingsProvider(config)
        raise ValueError(f"Неподдерживаемый режим для Embeddings: {config.mode}")

    def _init_vlm(self, config: ModelConfig) -> BaseVLMProvider:
        if config.mode in (EngineMode.API, EngineMode.LOCAL):
            return VLMProvider(config)
        raise ValueError(f"Неподдерживаемый режим для VLM: {config.mode}")

    def _init_reranker(self, config: ModelConfig) -> BaseRerankerProvider:
        if config.mode in (EngineMode.API, EngineMode.LOCAL):
            return RerankerProvider(config)
        raise ValueError(f"Неподдерживаемый режим для Reranker: {config.mode}")
        