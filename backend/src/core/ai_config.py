from typing import Dict, Any, Optional, Generic, TypeVar
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, computed_field




class EngineMode(str, Enum):
    LOCAL = "local"
    CLOUD = "cloud"


class ModelConfig(BaseModel):
    enabled: bool = True
    mode: EngineMode
    model_name: str
    api_url: str
    api_key: Optional[str] = None
    timeout: float = 60.0
    max_tokens: Optional[int] = None
    prompt: Optional[str] = None

    model_config = ConfigDict(extra="allow")

    @computed_field
    @property
    def extra_params(self) -> Dict[str, Any]:
        return self.model_extra or {}

    
class VLMConfig(ModelConfig):
    picture_prompt: Optional[str] = None
    code_formula_prompt: Optional[str] = None


T = TypeVar("T", bound=ModelConfig)


class AIProviderConfig(BaseModel, Generic[T]):
    primary: Optional[T] = None
    fallback: Optional[T] = None


class AIServiceConfig(BaseModel):
    llm: Optional[AIProviderConfig[ModelConfig]] = None
    embedder: Optional[AIProviderConfig[ModelConfig]] = None
    vlm: Optional[AIProviderConfig[VLMConfig]] = None
    reranker: Optional[AIProviderConfig[ModelConfig]] = None