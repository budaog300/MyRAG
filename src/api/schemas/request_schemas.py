from uuid import UUID, uuid4
from datetime import datetime
from pydantic import BaseModel, Field


class QuerySchema(BaseModel):
    query: str = Field(..., min_length=1, description="Введите поисковый запрос")
    collection_name: str = Field(
        ..., min_length=1, description="Введите название коллекции"
    )


class AddCollectionSchema(BaseModel):
    name: str = Field(..., min_length=5, description="Введите название коллекции")
    size: int = Field(..., ge=1, description="Введите размер векторной размерности")
    distance: str = Field(..., min_length=1, description="Введите вид расстояния")


class AddIndexSchema(BaseModel):
    name: str = Field(..., min_length=5, description="Введите название индекса")


class IngestDataSchema(BaseModel):
    task_id: UUID = Field(default_factory=uuid4)
    collection_name: str = Field(..., description="Назание коллекции")
    document_id: UUID
    s3_key: str = Field(..., description="Ключ файла в S3 (например, 'documents/uuid.pdf')")
    original_filename: str = Field(..., description="Исходное имя файла")
    chunk_size: int = 500
    chunk_overlap: int = 50