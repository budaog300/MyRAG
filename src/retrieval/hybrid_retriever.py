from rank_bm25 import BM25Okapi

from src.retrieval import VectorRetriever, BM25Retriever, BaseRetriever


class HybridRetriever(BaseRetriever):
    def __init__(
        self, vector_retriever: VectorRetriever, bm25_retriever: BM25Retriever
    ):
        self.vector_retriever = vector_retriever
        self.bm25_retriever = bm25_retriever

    async def retrieve(self, query: str, collection_name: str): ...

    async def merge(self): ...
