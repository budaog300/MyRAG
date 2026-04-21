import asyncio
from pathlib import Path
from src.services.document_service import DocumentService
from src.services.schemas import RawDocumentSchema
from src.repository import QdrantRepository, ElasticRepository


async def main():
    repo = QdrantRepository()
    keyword_repo = ElasticRepository()
    doc_service = DocumentService(
        repo, keyword_repo, model="sentence-transformers/all-MiniLM-L6-v2"
    )
    paths = [path for path in Path("./docs").iterdir() if path.is_file()]
    docs = [
        RawDocumentSchema(filename=path, content=path.read_text(encoding="utf-8"))
        for path in paths
    ]
    await doc_service.ingest_files("sber_docs", docs)
    await repo.close()
    await keyword_repo.close()


if __name__ == "__main__":
    asyncio.run(main())
