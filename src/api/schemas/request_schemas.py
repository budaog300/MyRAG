import hashlib
from uuid import UUID, uuid4
from typing import Any
from pydantic import BaseModel, Field


class QuerySchema(BaseModel):
    query: str = Field(..., min_length=1, description="Введите поисковый запрос")
    retrieve_limit: int = Field(default=30, ge=1, description="Количество чанков, извлекаемых из векторной БД")
    merge_limit: int = Field(default=10, ge=1, description="Лимит объединения чанков после первичного ретрива")
    top_k: int = Field(default=5, ge=1, description="Количество итоговых документов после реранкинга для передачи в LLM")
    temperature: float = Field(default=0.3, ge=0.0, le=2.0, description="Температура генерации LLM (от 0.0 до 2.0)")
    max_tokens: int = Field(default=1024, ge=1, description="Максимальное количество токенов в ответе LLM")
    only_context: bool = Field(default=True, description="Если True, возвращает только найденные чанки без вызова LLM")


class AddCollectionSchema(BaseModel):
    name: str = Field(..., min_length=5, description="Введите название коллекции")
    size: int = Field(..., ge=1, description="Введите размер векторной размерности")
    distance: str = Field(..., min_length=1, description="Введите вид расстояния")


class AddIndexSchema(BaseModel):
    name: str = Field(..., min_length=5, description="Введите название индекса")


class IngestionConfigParams(BaseModel):
    collection_name: str = Field(..., description="Название коллекции")
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