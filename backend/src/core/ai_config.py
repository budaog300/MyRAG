from typing import Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict, computed_field


class EngineMode(str, Enum):
    LOCAL = "local"
    API = "api"


class ModelConfig(BaseModel):
    enabled: bool = True
    mode: EngineMode = EngineMode.API
    model_name: str
    api_url: str = "http://localhost:11434/v1/chat/completions" 
    api_key: Optional[str] = None
    timeout: float = 60.0
    max_tokens: Optional[int] = None
    prompt: Optional[str] = None

    model_config = ConfigDict(extra="allow")

    @computed_field
    @property
    def extra_params(self) -> Dict[str, Any]:
        """Возвращает все доп. аргументы, переданные через kwargs"""
        return self.model_extra or {}


class VLMConfig(ModelConfig):
    picture_prompt: Optional[str] = None
    code_formula_prompt: Optional[str] = None


class AIServiceConfig(BaseModel):
    llm: Optional[ModelConfig] = None
    embedder: Optional[ModelConfig] = None
    vlm: Optional[VLMConfig] = None
    reranker: Optional[ModelConfig] = None