from src.rag.retrieval import BaseRetriever
from src.rag.repository import KeywordBaseRepository


class BM25Retriever(BaseRetriever):
    def __init__(self, repo: KeywordBaseRepository):
        self.repo = repo

    async def retrieve(self, query: str, index: str, **kwargs):
        return await self.repo.search(query, index, **kwargs)
