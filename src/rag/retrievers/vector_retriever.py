from src.rag.retrievers import BaseRetriever
from src.rag.repositories import BaseVectorRepository


class VectorRetriever(BaseRetriever):
    def __init__(self, repo: BaseVectorRepository):
        self.repo = repo

    async def retrieve(self, query: str, collection_name: str, **kwargs):
        return await self.repo.search_points(query, collection_name, **kwargs)
