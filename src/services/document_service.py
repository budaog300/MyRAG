from src.repository import VectorBaseRepository, KeywordBaseRepository
from src.utils import chunk_docs


class DocumentService:
    def __init__(
        self,
        repo: VectorBaseRepository,
        keyword_repo: KeywordBaseRepository,
        model: str = "BAAI/bge-m3",
    ):
        self.repo = repo
        self.keyword_repo = keyword_repo
        self.model = model

    async def ingest(self, folder_path: str, collection_name: str):
        chunks = chunk_docs(folder_path, chunk_size=1000, chunk_overlap=200)
        await self.repo.upsert(collection_name, chunks, model=self.model)
        await self.keyword_repo.index_documents(collection_name, chunks)


if __name__ == "__main__":
    doc = DocumentService()
