from src.repository import VectorBaseRepository
from src.utils import chunk_docs


class DocumentService:
    def __init__(self, repo: VectorBaseRepository, model: str = "BAAI/bge-m3"):
        self.repo = repo
        self.model = model

    async def process_and_upload_embeddings(
        self, folder_path: str, collection_name: str
    ):
        chunks = chunk_docs(folder_path, chunk_size=1000, chunk_overlap=200)
        await self.repo.upsert(collection_name, chunks, model=self.model)


if __name__ == "__main__":
    doc = DocumentService()
