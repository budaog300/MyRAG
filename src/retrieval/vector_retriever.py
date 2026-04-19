from src.retrieval import BaseRetriever
from src.repository import VectorBaseRepository


class VectorRetriever(BaseRetriever):
    def __init__(self, repo: VectorBaseRepository):
        self.repo = repo

    async def retrieve(self, query: str, collection_name: str):
        return await self.repo.search_points(query, collection_name)
