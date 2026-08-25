from typing import Optional, List, Any
from pydantic import BaseModel, Field


class CollectionSchema(BaseModel):
    name: str
    size: Optional[int] = None
    distance: Optional[str] = None
    

class IndexSchema(BaseModel):
    name: str


class RAGResponseSchema(BaseModel):
    answer: str | None = Field(default=None, description="Ответ, сгенерированный LLM")
    documents: List[Any] | None = Field(
        default=None, description="Найденные чанки (если only_context=True)"
    )
    count: int | None = Field(
        default=None, description="Количество найденных чанков"
    )
