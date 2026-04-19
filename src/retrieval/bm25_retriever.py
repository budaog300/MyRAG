from src.retrieval import BaseRetriever


class BM25Retriever(BaseRetriever):
    def __init__(self, repo):
        self.repo = repo

    async def retrieve(self, query: str, collection_name: str):
        return await self.repo.search_points(query, collection_name)
