import asyncio
from src.services.document_service import DocumentService
from src.repository import QdrantRepository, ElasticRepository


async def main():
    repo = QdrantRepository()
    keyword_repo = ElasticRepository()
    doc_service = DocumentService(
        repo, keyword_repo, model="sentence-transformers/all-MiniLM-L6-v2"
    )
    await doc_service.ingest("./docs", "sber_docs")
    await repo.close()
    await keyword_repo.close()


if __name__ == "__main__":
    asyncio.run(main())
