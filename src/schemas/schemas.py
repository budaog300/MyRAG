from pydantic import BaseModel, Field
from typing import List


class QuerySchema(BaseModel):
    query: str = Field(..., min_length=1, description="Введите поисковый запрос")
    collection_name: str = Field(
        ..., min_length=1, description="Введите название коллекции"
    )


class RAGDocument(BaseModel):
    id: str | None = None
    content: str
    score: float | None = None
    metadata: dict = Field(default_factory=dict)
    source: str | None = None


class AddCollectionSchema(BaseModel):
    name: str = Field(..., min_length=5, description="Введите название коллекции")


class CollectionSchema(BaseModel):
    name: str


class AddIndexSchema(BaseModel):
    name: str = Field(..., min_length=5, description="Введите название индекса")


class IndexSchema(BaseModel):
    name: str
