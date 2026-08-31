from typing import Annotated
from fastapi import APIRouter, File, Form, UploadFile, status
from src.rag.schemas.ingest import IngestionConfigParams
from src.api.deps import IngestionServiceDep

router = APIRouter(prefix="/ingest", tags=["Ingestion"])


@router.post(
    "",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Загрузка документации (RAG). Загрузить файлы в S3 и поставить задачи в очередь"
)
async def ingest_documents_async(
    ingestion_service: IngestionServiceDep,
    files: list[UploadFile] = File(...),
    collection_id: Annotated[str, Form(description="Название коллекции")] = ...,
    parent_chunk_size: Annotated[int | None, Form(description="Размер родительского чанка")] = None,
    parent_chunk_overlap: Annotated[int | None, Form(description="Перекрытие родительских чанков")] = None,
    chunk_size: Annotated[int | None, Form(description="Размер дочернего чанка")] = None,
    chunk_overlap: Annotated[int | None, Form(description="Перекрытие дочерних чанков")] = None
):
    config = IngestionConfigParams(
        collection_id=collection_id,
        parent_chunk_size=parent_chunk_size,
        parent_chunk_overlap=parent_chunk_overlap,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    doc_ids = await ingestion_service.process_incoming_files(
        files=files,
        config=config,
    )

    return {
        "status": "queued",
        "count": len(doc_ids),
        "document_ids": doc_ids,
    }