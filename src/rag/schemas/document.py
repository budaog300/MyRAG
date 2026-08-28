import hashlib
from uuid import UUID
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class RAGDocument(BaseModel):
    id: str | None = None
    content: str
    raw_content: str | None = None
    score: float | None = None
    metadata: dict = Field(default_factory=dict)
    source: str | None = None
    is_parent: bool = False


class RawDocumentSchema(BaseModel):
    source: str
    content: Optional[str] = None
    file_bytes: Optional[bytes] = None
    document_id: UUID
    content_hash: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CollectionSchema(BaseModel):
    id: UUID
    name: str
    size: Optional[int] = None
    distance: Optional[str] = None
    description: Optional[str] = None


class IndexSchema(BaseModel):
    name: str
