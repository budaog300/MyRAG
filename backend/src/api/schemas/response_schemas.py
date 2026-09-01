from typing import Optional, List, Any
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from src.rag.schemas.document import RAGDocument, VectorCollectionSchema, KeywordIndexSchema


class CollectionResponseSchema(BaseModel):
    id: UUID
    name: str
    size: Optional[int] = None
    distance: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CollectionDetailsResponseSchema(CollectionResponseSchema):
    vector_repo_info: VectorCollectionSchema | None = None
    keyword_repo_info: KeywordIndexSchema | None = None


class DocumentSchema(BaseModel):
    id: UUID
    filename: str
    status: str
    mime_type: str | None = None
    size_bytes: int | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentsResponseSchema(BaseModel):
    items: list[DocumentSchema]
    total: int


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

    class Config:
        from_attributes = True
