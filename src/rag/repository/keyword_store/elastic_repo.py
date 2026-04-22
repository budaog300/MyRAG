import asyncio
from typing import List, Dict, Any
from elasticsearch import AsyncElasticsearch, helpers

from src.core.config import settingsElastic
from src.rag.repository import KeywordBaseRepository
from src.rag.schemas.document import RAGDocument, IndexSchema

auth_data = settingsElastic.get_auth_data


class ElasticRepository(KeywordBaseRepository):
    def __init__(self):
        self.client = AsyncElasticsearch(**auth_data)

    async def create_index(self, index: str):
        mappings = {
            "properties": {
                "id": {"type": "keyword"},
                "content": {"type": "text"},
                "retrieval_score": {"type": "float"},
                "rerank_score": {"type": "float"},
                "source": {"type": "keyword"},
                "metadata": {"type": "object", "enabled": True},
            }
        }
        await self.client.indices.create(index=index, mappings=mappings)

    async def get_indices(self) -> List[IndexSchema]:
        indices = await self.client.cat.indices(format="json")
        print(indices)
        return [IndexSchema(name=index["index"]) for index in indices]

    async def get_index_details(self, index: str):
        return await self.client.count(index=index)

    async def delete_index(self, index: str):
        await self.client.indices.delete(index=index)

    async def clear_index(self, index: str):
        return await self.client.delete_by_query(index=index, query={"match_all": {}})

    async def index_documents(self, index: str, items: List[Dict[str, Any]]):
        actions = [
            {
                "_index": index,
                "_id": i + 1,
                "_source": {
                    "content": item["content"],
                    "metadata": item["metadata"],
                    "source": item["source"],
                },
            }
            for i, item in enumerate(items)
        ]
        success, failed = await helpers.async_bulk(self.client, actions)
        print("SUCCESS:", success)
        print("FAILED:", failed)
        await self.client.indices.refresh(index=index)

    async def search(
        self, query: str, index: str, limit: int = 10, **kwargs
    ) -> List[RAGDocument]:
        retrieved_docs = await self.client.search(
            index=index,
            query={"match": {"content": query}},
            size=limit,
        )

        print(f"Elastic output={retrieved_docs}")

        result = [
            RAGDocument(
                id=hit["_id"],
                content=hit["_source"]["content"],
                score=hit["_score"],
                metadata=hit["_source"]["metadata"],
                source=hit["_source"]["source"],
            )
            for hit in retrieved_docs["hits"]["hits"]
        ]
        return result

    async def close(self):
        await self.client.close()
