from pydantic import BaseModel, Field
from typing import List


class QuerySchema(BaseModel):
    query: str = Field(..., min_length=1, description="Введите поисковый запрос")
    collection_name: str = Field(
        ..., min_length=1, description="Введите название коллекции"
    )


class AddCollectionSchema(BaseModel):
    name: str = Field(..., min_length=5, description="Введите название коллекции")


class CollectionSchema(BaseModel):
    name: str


class RAGDocument(BaseModel):
    id: str | None = None
    content: str
    retrieval_score: float | None = None
    rerank_score: float | None = None
    metadata: dict = Field(default_factory=dict)
    source: str | None = None
