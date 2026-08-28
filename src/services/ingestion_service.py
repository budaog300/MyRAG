import os
import hashlib
from uuid import uuid4, UUID
from fastapi import UploadFile
from src.broker.publisher import RabbitMQPublisher
from src.rag.schemas.ingest import IngestDataSchema
from src.services.s3_service import S3Service
from src.db.repositories import RepositoryContainer
from src.core.exceptions.repo_exceptions import CollectionNotFoundError


class DocumentIngestionService:
    """Сервис-оркестратор для первички: сохранение в S3 и постановка в очередь."""

    def __init__(
            self,
            s3_service: S3Service,
            broker: RabbitMQPublisher,
            repos: RepositoryContainer
    ):
        self.s3_service = s3_service
        self.broker = broker
        self.repos = repos

    async def process_incoming_files(
        self,
        files: list[UploadFile],
        collection_id: UUID,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        parent_chunk_size: int | None = None,
        parent_chunk_overlap: int | None = None,
    ) -> list[str]:
        """Обрабатывает загружаемые файлы, отправляет в S3 и публикует задачи в RabbitMQ."""
        collection = await self.repos.collection_repo.get_by_id(collection_id)

        if collection is None:
            raise CollectionNotFoundError(str(collection_id))

        await self.s3_service.ensure_bucket_exists()
        queued_doc_ids: list[str] = []

        for file in files:
            file_content = await file.read()
            content_hash = hashlib.sha256(file_content).hexdigest()

            file_ext = os.path.splitext(file.filename)[1]
            document_id = uuid4()
            s3_key = f"raw_documents/{document_id}{file_ext}"

            document = await self.repos.document_repo.create(
                id=document_id,
                collection_id=collection_id,
                filename=file.filename or "unknown",
                mime_type=file.content_type,
                size_bytes=len(file_content),
            )
            await self.repos.document_repo.session.commit()

            await self.s3_service.upload_file(
                file_data=file_content,
                object_key=s3_key,
                content_type=file.content_type or "application/octet-stream",
            )

            task_data = IngestDataSchema(
                document_id=document.id,                
                collection_id=collection.id,
                s3_key=s3_key,
                content_hash=content_hash,
                original_filename=file.filename or "unknown",
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                parent_chunk_size=parent_chunk_size,
                parent_chunk_overlap=parent_chunk_overlap
            )

            await self.broker.publish(task_data)
            queued_doc_ids.append(str(document_id))

        return queued_doc_ids