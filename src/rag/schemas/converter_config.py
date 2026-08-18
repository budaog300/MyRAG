from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class VLMConfig(BaseModel):
    enabled: bool = True
    api_url: str = "http://localhost:11434/v1/chat/completions" 
    api_key: Optional[str] = None
    model_name: str = "qwen3-vl:2b"
    max_tokens: int = 4096
    timeout: int = 90
    extra_params: Dict[str, Any] = Field(default_factory=dict)