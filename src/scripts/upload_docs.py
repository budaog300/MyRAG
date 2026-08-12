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
    paths = [path for path in Path("./docs").iterdir() if path.is_file()]
    docs = [
        RawDocumentSchema(filename=str(path), content=path.read_text(encoding="utf-8"))
        for path in paths
    ]
    logger.info("Документы считаны")
    await doc_service.ingest_files("sber_docs", docs)
    logger.info("Документы загружены")
    await repo.close()
    await keyword_repo.close()
    logger.info("Загрузка окончена")


if __name__ == "__main__":
    asyncio.run(main())
