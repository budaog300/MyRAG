import asyncio
from src.services.document_service import DocumentService
from src.repository import QdrantRepository


async def main():
    repo = QdrantRepository()
    doc_service = DocumentService(repo, model="sentence-transformers/all-MiniLM-L6-v2")
    await doc_service.process_and_upload_embeddings("./docs", "sber_docs")
    await repo.close()


if __name__ == "__main__":
    asyncio.run(main())
