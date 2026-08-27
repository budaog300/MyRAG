import os
import hashlib
from uuid import uuid4
from fastapi import UploadFile
from src.broker.publisher import RabbitMQPublisher
from src.rag.schemas.ingest import IngestDataSchema
from src.services.s3_service import S3Service


class DocumentIngestionService:
    """Сервис-оркестратор для первички: сохранение в S3 и постановка в очередь."""

    def __init__(self, s3_service: S3Service, broker: RabbitMQPublisher):
        self.s3_service = s3_service
        self.broker = broker

    async def process_incoming_files(
        self,
        files: list[UploadFile],
        collection_name: str,
        chunk_size: int | None = None,
        chunk_overlap: int | None = None,
        parent_chunk_size: int | None = None,
        parent_chunk_overlap: int | None = None,
    ) -> list[str]:
        """Обрабатывает загружаемые файлы, отправляет в S3 и публикует задачи в RabbitMQ."""
        await self.s3_service.ensure_bucket_exists()
        queued_doc_ids: list[str] = []

        for file in files:
            document_id = uuid4()
            file_content = await file.read()
            content_hash = hashlib.sha256(file_content).hexdigest()

            file_ext = os.path.splitext(file.filename)[1] 
            s3_key = f"raw_documents/{document_id}{file_ext}"

            file_content = await file.read()
            await self.s3_service.upload_file(
                file_data=file_content,
                object_key=s3_key,
                content_type=file.content_type or "application/octet-stream",
            )

            task_data = IngestDataSchema(
                document_id=document_id,
                content_hash=content_hash,
                collection_name=collection_name,
                s3_key=s3_key,
                original_filename=file.filename or "unknown",
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                parent_chunk_size=parent_chunk_size,
                parent_chunk_overlap=parent_chunk_overlap
            )

            await self.broker.publish(task_data)
            queued_doc_ids.append(str(document_id))

        return queued_doc_ids