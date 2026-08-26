from typing import Optional, List, Any
from pydantic import BaseModel, Field
from src.rag.schemas.document import RAGDocument


class CollectionSchema(BaseModel):
    name: str
    size: Optional[int] = None
    distance: Optional[str] = None
    

class IndexSchema(BaseModel):
    name: str


class RAGResponseSchema(BaseModel):
    answer: str | None = Field(default=None, description="Ответ, сгенерированный LLM")
    documents: List[RAGDocument] | None = Field(
        default=None, description="Найденные чанки (если only_context=True)"
    )
    count: int | None = Field(
        default=None, description="Количество найденных чанков"
    )
    only_context: bool | None = Field(
        default=None, description="Флаг: возвращать ответ LLM или нет"
    )
