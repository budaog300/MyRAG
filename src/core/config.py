from pydantic_settings import BaseSettings, SettingsConfigDict
from src.core.ai_config import AIServiceConfig, ModelConfig, EngineMode


class SettingsQdrant(BaseSettings):
    QDRANT_URL: str
    QDRANT_API_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env.qdrant")

    @property
    def get_auth_data(self) -> dict:
        return {
            "url": self.QDRANT_URL,
            "api_key": self.QDRANT_API_KEY,
        }


class SettingsElastic(BaseSettings):
    ELASTIC_URL: str
    ELASTIC_API_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=".env.elastic")

    @property
    def get_auth_data(self) -> dict:
        return {
            "hosts": self.ELASTIC_URL,
            "api_key": self.ELASTIC_API_KEY,
        }


class SettingsAI(BaseSettings):
    # LLM
    LLM_ENABLED: bool = True
    LLM_MODE: EngineMode = EngineMode.API
    LLM_MODEL: str = "qwen3:4b"
    LLM_API_URL: str = "http://ollama:11434/v1/chat/completions"
    LLM_API_KEY: str = ""

    # VLM
    VLM_ENABLED: bool = True
    VLM_MODE: EngineMode = EngineMode.API
    VLM_MODEL: str = "qwen3-vl:2b"
    VLM_API_URL: str = "http://ollama:11434/v1/chat/completions"
    VLM_API_KEY: str = ""

    # Embeddings
    EMBED_ENABLED: bool = True
    EMBED_MODE: EngineMode = EngineMode.API
    EMBED_MODEL: str = "bge-m3"
    EMBED_API_URL: str = "http://ollama:11434/v1/embeddings"
    EMBED_API_KEY: str = ""

    # Reranker
    RERANK_ENABLED: bool = True
    RERANK_MODE: EngineMode = EngineMode.API
    RERANK_MODEL: str = "qllama/bge-reranker-v2-m3"
    RERANK_API_URL: str = "http://ollama:11434/v1/embeddings"
    RERANK_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env.ai", extra="ignore")

    def build_ai_config(self) -> AIServiceConfig:
        """Сборка AIServiceConfig из env-переменных"""
        return AIServiceConfig(
            llm=ModelConfig(
                enabled=self.LLM_ENABLED,
                mode=EngineMode(self.LLM_MODE),
                model_name=self.LLM_MODEL,
                api_url=self.LLM_API_URL,
                api_key=self.LLM_API_KEY,
            ) if self.LLM_ENABLED else None,
            embeddings=ModelConfig(
                enabled=self.EMBED_ENABLED,
                mode=EngineMode(self.EMBED_MODE),
                model_name=self.EMBED_MODEL,
                api_url=self.EMBED_API_URL,
                api_key=self.EMBED_API_KEY,
            ) if self.EMBED_ENABLED else None,
            vlm=ModelConfig(
                enabled=self.VLM_ENABLED,
                mode=EngineMode(self.VLM_MODE),
                model_name=self.VLM_MODEL,
                api_url=self.VLM_API_URL,
                api_key=self.VLM_API_KEY,
            ) if self.VLM_ENABLED else None,
            reranker=ModelConfig(
                enabled=self.RERANK_ENABLED,
                mode=EngineMode(self.RERANK_MODE),
                model_name=self.RERANK_MODEL,
                api_url=self.RERANK_API_URL,
                api_key=self.RERANK_API_KEY,
            ) if self.RERANK_ENABLED else None,
        )


settingsAI = SettingsAI()
settingsQdrant = SettingsQdrant()
settingsElastic = SettingsElastic()