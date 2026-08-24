from typing import Any, Dict, List
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from qdrant_client.models import Distance, VectorParams, PointStruct, Document

from src.core.config import settingsQdrant
from src.rag.repositories import BaseVectorRepository
from src.rag.schemas.document import CollectionSchema, RAGDocument
from src.rag.ai.providers import BaseEmbedderProvider

auth_data = settingsQdrant.get_auth_data


class QdrantRepository(BaseVectorRepository):
    def __init__(self, embedder: BaseEmbedderProvider):
        self.client = AsyncQdrantClient(**auth_data)
        self.embedder = embedder

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

        parents_collection_name = f"{collection_name}_parents"
        await self.client.create_collection(
            collection_name=parents_collection_name,
            vectors_config={},
        )

    async def get_collections(self, include_parents: bool = False) -> List[CollectionSchema]:
        result = await self.client.get_collections()
        if include_parents:
            return [CollectionSchema(name=col.name) for col in result.collections]
        return [CollectionSchema(name=col.name) for col in result.collections if not col.name.endswith("_parents")]

    async def get_collection_details(self, collection_name: str):
        result = await self.client.get_collection(collection_name)
        return result

    async def clear_collection(self, collection_name: str):
        await self.client.delete(collection_name=collection_name, points_selector=models.Filter())
        parents_collection_name = f"{collection_name}_parents"
        if await self.client.collection_exists(parents_collection_name):
            await self.client.delete(collection_name=parents_collection_name, points_selector=models.Filter())

    async def delete_collection(
        self,
        collection_name: str,
    ):
        await self.client.delete_collection(collection_name=collection_name)
        parents_collection_name = f"{collection_name}_parents"
        if await self.client.collection_exists(parents_collection_name):
            await self.client.delete_collection(collection_name=parents_collection_name)

    async def delete_by_filter(self, collection_name: str, key: str, value: Any) -> None:
        await self.client.delete(
            collection_name=collection_name,
            points_selector=models.FilterSelector(
                filter=models.Filter(
                    must=[
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        )
                    ]
                )
            )
        )

    async def upsert(
        self,
        collection_name: str,
        items: List[Dict[str, Any]],
        # model: str = "sentence-transformers/all-MiniLM-L6-v2",
        is_vector: bool = True
    ):
        texts = [item["content"] for item in items]
        embeddings = await self.embedder.embed_documents(texts)
        points = [
            PointStruct(
                id=item["metadata"]["chunk_id"],
                vector=vector if is_vector else {},
                payload=item,
            )
            for item, vector in zip(items, embeddings)          
        ]

        await self.client.upsert(
            collection_name=collection_name,
            points=points,
        )

    async def search_points(
        self,
        query: str,
        collection_name: str,
        # model: str = "sentence-transformers/all-MiniLM-L6-v2",
        limit: int = 30,
        with_payload: bool = True,
        **kwargs,
    ) -> List[RAGDocument]:
        query_vector = await self.embedder.embed_query(query)
        retrieved_docs = await self.client.query_points(
            collection_name=collection_name,
            query=query_vector,
            with_payload=with_payload,
            limit=limit,
        )

        results = [
            RAGDocument(
                id=str(point.id),
                content=point.payload.get("content", ""),
                raw_content=point.payload.get("raw_content", ""),
                score=point.score,
                metadata=point.payload.get("metadata", {}),
                source=point.payload.get("source", ""),
            )
            for point in retrieved_docs.points
        ]
        return results

    async def get_documents_by_ids(
        self,
        collection_name: str,
        ids: List[str],
        with_payload: bool = True,
    ) -> List[RAGDocument]:
        points = await self.client.retrieve(
            collection_name=collection_name,
            ids=ids,
            with_payload=with_payload,
        )

        results = [
            RAGDocument(
                id=str(point.id),
                content=point.payload.get("content", ""),
                raw_content=point.payload.get("raw_content", ""),
                metadata=point.payload.get("metadata", {}),
                source=point.payload.get("source", ""),
                is_parent=point.payload.get("is_parent", ""),
            )
            for point in points
        ]
        return results

    async def close(self):
        await self.client.close()
