from typing import Optional
from src.rag.ai.provider_config import AIServiceConfig, EngineMode
from src.rag.ai.providers import BaseAIProvider, BaseEmbeddingsProvider, BaseLLMProvider, BaseVLMProvider


class AIService:
    def __init__(self, config: AIServiceConfig):
        self.config = config
        
        # Инициализация LLM
        self.llm: BaseLLM = self._init_llm(config.llm)
        
        # Инициализация Embeddings
        self.embeddings: BaseEmbeddings = self._init_embeddings(config.embeddings)
        
        # Инициализация VLM (опционально)
        self.vlm: Optional[BaseVLM] = (
            self._init_vlm(config.vlm) if config.vlm and config.vlm.enabled else None
        )
        
        # Инициализация Reranker (опционально)
        self.reranker: Optional[BaseReranker] = (
            UniversalRerankerProvider(config.reranker)
            if config.reranker and config.reranker.enabled
            else None
        )

    def _init_llm(self, config) -> BaseLLM:
        if config.mode in (EngineMode.API, EngineMode.OLLAMA):
            return OpenAICompatibleProvider(config)
        raise ValueError(f"Неподдерживаемый режим для LLM: {config.mode}")

    def _init_embeddings(self, config) -> BaseEmbeddings:
        if config.mode in (EngineMode.API, EngineMode.OLLAMA):
            return OpenAICompatibleProvider(config)
        raise ValueError(f"Неподдерживаемый режим для Embeddings: {config.mode}")

    def _init_vlm(self, config) -> BaseVLM:
        return OpenAICompatibleProvider(config)