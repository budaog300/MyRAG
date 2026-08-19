from enum import Enum
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class EngineMode(str, Enum):
    API = "api"
    OLLAMA = "ollama"
    LOCAL = "local"


class ModelConfig(BaseModel):
    enabled: bool = True
    mode: EngineMode = EngineMode.API
    model_name: str
    api_url: Optional[str] = None
    api_key: Optional[str] = None
    timeout: float = 60.0
    extra_params: Dict[str, Any] = Field(default_factory=dict)


class AIServiceConfig(BaseModel):
    llm: ModelConfig = None
    vlm: Optional[ModelConfig] = None
    embeddings: ModelConfig = None
    reranker: Optional[ModelConfig] = None