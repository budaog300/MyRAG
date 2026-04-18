from typing import Any, Dict, List
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Document

from src.core.config import settingsQdrant
from src.repository.base import VectorBaseRepository
from src.schemas.schemas import CollectionSchema, RAGDocument

auth_data = settingsQdrant.get_auth_data


class QdrantRepository(VectorBaseRepository):
    def __init__(self):
        self.client = AsyncQdrantClient(url=auth_data["QDRANT_URL"])

    async def create_collection(
        self,
        collection_name: str,
        size: int = 384,
        distance: str = "COSINE",
    ):
        await self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=size, distance=getattr(Distance, distance)
            ),
        )

    async def get_collections(self):
        result = await self.client.get_collections()
        return [CollectionSchema(name=col.name) for col in result.collections]

    async def get_collection_details(self, collection_name: str):
        result = await self.client.get_collection(collection_name)
        return result

    async def delete_collection(
        self,
        collection_name: str,
    ):
        await self.client.delete_collection(collection_name=collection_name)

    async def upsert(
        self,
        collection_name: str,
        items: List[Dict[str, Any]],
        model: str = "sentence-transformers/all-MiniLM-L6-v2",
    ):
        points = [
            PointStruct(
                id=i + 1,
                vector=Document(
                    text=item["content"],
                    model=model,
                ),
                payload=item,
            )
            for i, item in enumerate(items)
        ]

        await self.client.upsert(
            collection_name=collection_name,
            points=points,
        )

    async def search_points(
        self,
        query: str,
        collection_name: str,
        model: str = "sentence-transformers/all-MiniLM-L6-v2",
        limit: int = 10,
        with_payload: bool = True,
    ) -> List[RAGDocument]:
        retrieved_docs = await self.client.query_points(
            collection_name=collection_name,
            query=Document(text=query, model=model),
            with_payload=with_payload,
            limit=limit,
        )

        results = [
            RAGDocument(
                id=str(point.id),
                content=point.payload.get("content", ""),
                retrieval_score=point.score,
                metadata=point.payload.get("metadata", {}),
                source=point.payload.get("source", ""),
            )
            for point in retrieved_docs.points
        ]
        print(results)
        return results

    async def close(self):
        await self.client.close()
