import logging
import os
import hashlib
from uuid import uuid4, UUID
from fastapi import UploadFile
from src.broker.publisher import RabbitMQPublisher
from src.rag.schemas.ingest import IngestDataSchema, IngestionConfigParams
from src.services.s3_service import S3Service
from src.db.repositories import RepositoryContainer
from src.core.exceptions.repo_exceptions import CollectionNotFoundError

logger = logging.getLogger(__name__)


class DocumentIngestionService:
    """Сервис-оркестратор для первички: сохранение в S3 и постановка в очередь."""

    def __init__(
            self,
            s3_service: S3Service,
            broker: RabbitMQPublisher,
            db_repo: RepositoryContainer
    ):
        self.s3_service = s3_service
        self.broker = broker
        self.db_repo = db_repo

    async def process_incoming_files(
        self,
        files: list[UploadFile],
        config: IngestionConfigParams
    ) -> list[str]:
        """Обрабатывает загружаемые файлы, отправляет в S3 и публикует задачи в RabbitMQ."""
        logger.info("Начата загрузка документов: collection_id=%s, файлов=%d", config.collection_id, len(files))

        collection = await self.db_repo.collection_repo.get_by_id(config.collection_id)

        if collection is None:
            raise CollectionNotFoundError(str(config.collection_id))

        await self.s3_service.ensure_bucket_exists()
        queued_doc_ids: list[str] = []

        for file in files:
            filename = file.filename or "unknown"
            try:
                logger.info("Начата обработка загружаемого файла: filename=%s, collection_id=%s", filename, collection.id)

                file_content = await file.read()
                content_hash = hashlib.sha256(file_content).hexdigest()
                file_ext = os.path.splitext(filename)[1]
                document_id = uuid4()
                s3_key = f"raw_documents/{document_id}{file_ext}"

                logger.debug("Файл прочитан: filename=%s, size_bytes=%d", filename, len(file_content))

                document = await self.db_repo.document_repo.create(
                    id=document_id,
                    collection_id=config.collection_id,
                    filename=filename,
                    s3_key=s3_key,
                    mime_type=file.content_type,
                    size_bytes=len(file_content),
                )

                await self.db_repo.document_repo.session.commit()

                logger.debug("Документ создан в БД: document_id=%s, filename=%s", document.id, filename)

                await self.s3_service.upload_file(
                    file_data=file_content,
                    object_key=s3_key,
                    content_type=file.content_type or "application/octet-stream",
                )

                logger.debug("Файл загружен в S3: document_id=%s, s3_key=%s", document.id, s3_key)

                task_data = IngestDataSchema(
                    document_id=document.id,
                    collection_id=collection.id,
                    s3_key=s3_key,
                    content_hash=content_hash,
                    original_filename=filename,
                    chunk_size=config.chunk_size,
                    chunk_overlap=config.chunk_overlap,
                    parent_chunk_size=config.parent_chunk_size,
                    parent_chunk_overlap=config.parent_chunk_overlap,
                )

                await self.broker.publish(task_data)
                logger.info("Задача обработки опубликована: document_id=%s", document.id)
                queued_doc_ids.append(str(document_id))

            except Exception as exc:
                logger.error("Ошибка обработки загружаемого файла: filename=%s, ошибка=%s", filename, exc, exc_info=True)
                raise

        logger.info("Загрузка документов завершена: collection_id=%s, успешно поставлено в очередь=%d", config.collection_id, len(queued_doc_ids))
        return queued_doc_ids