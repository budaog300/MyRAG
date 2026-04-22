from pydantic import BaseModel, Field
from typing import List, Annotated


class RAGDocument(BaseModel):
    id: str | None = None
    content: str
    score: float | None = None
    metadata: dict = Field(default_factory=dict)
    source: str | None = None


class IngestDataSchema(BaseModel):
    collection_name: str
    chunk_size: int = 1000
    chunk_overlap: int = 300


class RawDocumentSchema(BaseModel):
    filename: str
    content: str


class CollectionSchema(BaseModel):
    name: str


class IndexSchema(BaseModel):
    name: str
