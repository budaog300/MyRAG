from uuid import uuid4, UUID
from pydantic import BaseModel, Field


class IngestionConfigParams(BaseModel):
    collection_id: UUID = Field(..., description="ID коллекции")
    parent_chunk_size: int | None = Field(default=None, ge=1, description="Размер родительского чанка")
    parent_chunk_overlap: int | None = Field(default=None, ge=0, description="Перекрытие родительских чанков")
    chunk_size: int | None = Field(default=None, ge=1, description="Размер дочернего чанка")
    chunk_overlap: int | None = Field(default=None, ge=0, description="Перекрытие дочерних чанков")


class IngestDataSchema(IngestionConfigParams):
    task_id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    s3_key: str = Field(..., description="Ключ файла в S3")
    original_filename: str = Field(..., description="Исходное имя файла")
    content_hash: str