from src.rag.retrievers import BaseRetriever
from src.rag.repositories import BaseKeywordRepository


class BM25Retriever(BaseRetriever):
    def __init__(self, repo: BaseKeywordRepository):
        self.repo = repo

    async def retrieve(self, query: str, index: str, **kwargs):
        return await self.repo.search(query, index, **kwargs)
