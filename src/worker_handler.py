import logging
from src.rag.schemas.ingest import IngestDataSchema
from src.rag.schemas.document import RawDocumentSchema
from src.services import S3Service, DocumentService
from src.db.models import DocumentStatus
from src.db.repositories import RepositoryContainer
from src.core.exceptions import BaseAppException

logger = logging.getLogger(__name__)


async def process_document_task(
    task: IngestDataSchema, 
    document_service: DocumentService,
    s3_service: S3Service,
    repos: RepositoryContainer
) -> None:
    logger.info("Начинаем обработку документа %s (%s)", task.document_id, task.original_filename)

    try:
        await repos.document_repo.update_status(
            document_id=task.document_id,
            status=DocumentStatus.PROCESSING
        )
        await repos.document_repo.session.commit()

        file_bytes = await s3_service.download_file(object_key=task.s3_key)

        raw_doc = RawDocumentSchema(
            source=task.original_filename,
            file_bytes=file_bytes,
            document_id=task.document_id,
            content_hash=task.content_hash,
            metadata={
                "original_filename": task.original_filename,
            }
        )

        await document_service.ingest_files(
            collection_name=str(task.collection_id),
            documents=[raw_doc],
            chunk_size=task.chunk_size,
            chunk_overlap=task.chunk_overlap,
        )

        await repos.document_repo.update_status(
            document_id=task.document_id,
            status=DocumentStatus.READY
        )
        await repos.document_repo.session.commit()

        logger.info("Документ %s успешно обработан и заиндексирован", task.document_id)
    except Exception as exc:
        await repos.document_repo.update_status(
            task.document_id,
            DocumentStatus.FAILED,
            error_message=str(exc),
        )
        await repos.document_repo.session.commit()

        logger.exception(
            "Ошибка обработки документа %s",
            task.document_id,
        )
        raise