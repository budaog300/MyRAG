import os
from typing import Any
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from src.core.ai_config import AIProviderConfig, AIServiceConfig, ModelConfig, VLMConfig, EngineMode
from src.core.utils.config_loader import load_yaml
from src.core.prompts import PICTURE_DESCRIPTION_PROMPT, CODE_FORMULA_PROMPT


class SettingsQdrant(BaseSettings):
    QDRANT_URL: str = Field(default="http://localhost:6333")
    QDRANT_API_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    @property
    def get_auth_data(self) -> dict:
        return {
            "url": self.QDRANT_URL,
            "api_key": self.QDRANT_API_KEY,
        }


class SettingsElastic(BaseSettings):
    ELASTIC_URL: str = Field(default="http://localhost:9200")
    ELASTIC_API_KEY: str | None = None

    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    @property
    def get_auth_data(self) -> dict:
        return {
            "hosts": self.ELASTIC_URL,
            "api_key": self.ELASTIC_API_KEY,
        }


class SettingsRabbitMQ(BaseSettings):    
    RABBITMQ_HOST: str = Field(default="localhost")
    RABBITMQ_PORT: int = Field(default=5672)
    RABBITMQ_USER: str = Field(default="guest")
    RABBITMQ_PASSWORD: str = Field(default="guest")
    RABBITMQ_VHOST: str = Field(default="/")
    DOCUMENTS_EXCHANGE: str = Field(default="documents_exchange")
    DOCUMENTS_QUEUE: str = Field(default="documents_queue")
    DOCUMENTS_ROUTING_KEY: str = Field(default="documents.ingest")

    model_config = SettingsConfigDict(env_file=None, extra="ignore")
    
    @property
    def get_auth_data(self) -> str:
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/{self.RABBITMQ_VHOST.lstrip('/')}"


class SettingsS3(BaseSettings):
    S3_ENDPOINT_URL: str = Field(default="http://localhost:9000")
    S3_ACCESS_KEY: str = Field(default="admin")
    S3_SECRET_KEY: str = Field(default="admin12345")
    S3_BUCKET_NAME: str = Field(default="documents")
    S3_REGION: str = Field(default="us-east-1")

    model_config = SettingsConfigDict(env_file=None, extra="ignore")


class SettingsDB(BaseSettings):
    DB_USER: str = Field(default="postgres")
    DB_PASSWORD: str = Field(default="123")
    DB_HOST: str = Field(default="localhost")
    DB_PORT: int = Field(default=5432)
    DB_NAME: str = Field(default="rag_db")
    DB_POOL_SIZE: int = Field(default=10)
    DB_MAX_OVERFLOW: int = Field(default=20)

    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    @property
    def get_auth_data(self) -> str:
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class SettingsAI(BaseSettings):
    LLM_MODE: EngineMode = EngineMode.CLOUD
    VLM_MODE: EngineMode = EngineMode.CLOUD
    EMBED_MODE: EngineMode = EngineMode.CLOUD
    RERANK_MODE: EngineMode = EngineMode.CLOUD

    model_config = SettingsConfigDict(env_file=None, extra="ignore")

    def build_ai_config(self) -> AIServiceConfig:
        config = load_yaml("ai.yaml")

        return AIServiceConfig(
            llm=self._build_provider_config(config["llm"], self.LLM_MODE),
            embedder=self._build_provider_config(config["embedding"], self.EMBED_MODE),
            vlm=self._build_provider_config(
                config["vlm"],
                self.VLM_MODE,
                VLMConfig,
                picture_prompt=PICTURE_DESCRIPTION_PROMPT,
                code_formula_prompt=CODE_FORMULA_PROMPT,
            ),
            reranker=self._build_provider_config(config["reranker"], self.RERANK_MODE),
        )

    def _build_model_config(self, config: dict, mode: EngineMode, config_class: type[ModelConfig] = ModelConfig, **extra: Any) -> ModelConfig | None:
        if not config["enabled"]:
            return None
        
        provider = config[mode.value]
        api_key = os.getenv(provider["api_key_env"]) if provider.get("api_key_env") else None

        return config_class(
            mode=mode,
            model_name=provider["model"],
            api_url=provider["api_url"],
            api_key=api_key,
            **extra
        )

    def _build_provider_config(self, config: dict, mode: EngineMode, config_class: type[ModelConfig] = ModelConfig, **extra: Any) -> AIProviderConfig | None:
        if not config["enabled"]:
            return None

        primary = self._build_model_config(config, mode, config_class, **extra)

        fallback_mode = config.get("fallback_mode")
        fallback = None

        if fallback_mode:
            fallback_mode = EngineMode(fallback_mode)
            if fallback_mode != mode:
                fallback = self._build_model_config(config, fallback_mode, config_class, **extra)

        return AIProviderConfig(primary=primary, fallback=fallback)


settingsAI = SettingsAI()
settingsQdrant = SettingsQdrant()
settingsElastic = SettingsElastic()
settingsRabbitMQ = SettingsRabbitMQ()
settingsS3 = SettingsS3()
settingsDB = SettingsDB()