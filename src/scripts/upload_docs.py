import asyncio
from pathlib import Path
from src.core.logger import logger
from src.rag.services.document_service import DocumentService
from src.rag.schemas.document import RawDocumentSchema
from src.rag.repository import QdrantRepository, ElasticRepository


async def main():
    logger.info("Начинаем загрузку документов в базы...")
    repo = QdrantRepository()
    keyword_repo = ElasticRepository()
    doc_service = DocumentService(
        repo, keyword_repo, model="sentence-transformers/all-MiniLM-L6-v2"
    )
    logger.info("DocumentService создан")
    paths = [path for path in Path("./docs").glob("**/*") if path.is_file()]
    docs = []
    for path in paths:
        # Для текстовых читаем сразу, для бинарных (pdf/docx) передаем байты
        if path.suffix.lower() in [".txt", ".md"]:
            docs.append(
                RawDocumentSchema(
                    source=path.name,
                    content=path.read_text(encoding="utf-8"),
                )
            )
        else:
            docs.append(
                RawDocumentSchema(
                    source=path.name,
                    file_bytes=path.read_bytes(),
                )
            )
    logger.info(f"Считано документов: {len(docs)}")
    await doc_service.ingest_files("sber_docs", docs)
    logger.info("Документы успешно загружены")
    await repo.close()
    await keyword_repo.close()


if __name__ == "__main__":
    asyncio.run(main())
