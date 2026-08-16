import hashlib
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


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
    source: str
    content: Optional[str] = None
    file_bytes: Optional[bytes] = None
    doc_id: str = Field(default="")
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def model_post_init(self, __context: Any) -> None:
        if not self.doc_id:
            data_to_hash = self.source.encode("utf-8") + (
                self.content.encode("utf-8") if self.content else (self.file_bytes or b"")
            )
            self.doc_id = hashlib.md5(data_to_hash).hexdigest()


class CollectionSchema(BaseModel):
    name: str


class IndexSchema(BaseModel):
    name: str
