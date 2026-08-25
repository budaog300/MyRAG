import logging
from src.api.schemas.request_schemas import IngestDataSchema
from src.rag.schemas.document import RawDocumentSchema
from src.rag.services import S3Service, DocumentService

logger = logging.getLogger(__name__)


async def process_document_task(
    task: IngestDataSchema, 
    document_service: DocumentService,
    s3_service: S3Service
) -> None:
    logger.info("Начинаем обработку документа %s (%s)", task.document_id, task.original_filename)

    file_bytes = await s3_service.download_file(object_key=task.s3_key)

    raw_doc = RawDocumentSchema(
        source=task.original_filename,
        file_bytes=file_bytes,
        doc_id=str(task.document_id),
        metadata={
            "s3_key": task.s3_key,
            "task_id": str(task.task_id),
            "original_filename": task.original_filename,
        }
    )

    await document_service.ingest_files(
        collection_name=task.collection_name,
        documents=[raw_doc],
        chunk_size=task.chunk_size,
        chunk_overlap=task.chunk_overlap,
    )

    logger.info("Документ %s успешно обработан и заиндексирован", task.document_id)