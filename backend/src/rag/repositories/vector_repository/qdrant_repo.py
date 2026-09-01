from uuid import UUID
from typing import Any, Dict, List, Set, Tuple
from qdrant_client import AsyncQdrantClient
from qdrant_client.http import models
from qdrant_client.http.exceptions import UnexpectedResponse
from qdrant_client.models import Distance, VectorParams, PointStruct, Document

from src.core.config import settingsQdrant
from src.rag.repositories.vector_repository.base import BaseVectorRepository
from src.rag.schemas.document import VectorCollectionSchema, RAGDocument
from src.rag.ai.providers import BaseEmbedderProvider
from src.core.exceptions.repo_exceptions import (
    CollectionAlreadyExistsError,
    CollectionNotFoundError,
    EmbedderError,
    VectorDatabaseError,
)
from src.core.exceptions.provider_exceptions import AIProviderError

auth_data = settingsQdrant.get_auth_data


class QdrantRepository(BaseVectorRepository):
    def __init__(self, embedder: BaseEmbedderProvider):
        try:
            self.client = AsyncQdrantClient(**auth_data)
        except Exception as e:
            raise VectorDatabaseError(f"Ошибка инициализации клиента Qdrant: {e}")
        self.embedder = embedder

    async def create_collection(
        self,
        collection_name: str,
        size: int = 384,
        distance: str = "COSINE",
    ):
        try:
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
        except UnexpectedResponse as e:
            if e.status_code == 409 or "already exists" in str(e).lower():
                raise CollectionAlreadyExistsError(collection_name)
            raise VectorDatabaseError(str(e))
        except Exception as e:
            raise VectorDatabaseError(f"Неизвестная ошибка при создании коллекции: {e}")

    async def get_collections(self, include_parents: bool = False) -> List[VectorCollectionSchema]:
        try:
            result = await self.client.get_collections()
            if include_parents:
                return [VectorCollectionSchema(name=col.name) for col in result.collections]
            return [
                VectorCollectionSchema(name=col.name)
                for col in result.collections
                if not col.name.endswith("_parents")
            ]
        except Exception as e:
            raise VectorDatabaseError(f"Ошибка при получении списка коллекций: {e}")

    async def get_collection_details(self, collection_name: str) -> VectorCollectionSchema | None:
        try:
            info = await self.client.get_collection(collection_name)
            return VectorCollectionSchema(
                name=collection_name,
                status=info.status,
                points_count=info.points_count or 0,
                size=info.config.params.vectors.size,
                distance=info.config.params.vectors.distance
            )
        except UnexpectedResponse as e:
            if e.status_code == 404:
                raise CollectionNotFoundError(collection_name)
            raise VectorDatabaseError(str(e))
        except Exception as e:
            raise VectorDatabaseError(str(e))

    async def clear_collection(self, collection_name: str):
        try:
            await self.client.delete(
                collection_name=collection_name, 
                points_selector=models.Filter()
            )
            parents_collection_name = f"{collection_name}_parents"
            
            if await self.client.collection_exists(parents_collection_name):
                await self.client.delete(
                    collection_name=parents_collection_name, points_selector=models.Filter()
                )
        except UnexpectedResponse as e:
            if e.status_code == 404:
                return None
            raise VectorDatabaseError(str(e))
        except Exception as e:
            raise VectorDatabaseError(str(e))

    async def delete_collection(self, collection_name: str):
        try:
            await self.client.delete_collection(collection_name=collection_name)
            parents_collection_name = f"{collection_name}_parents"

            if await self.client.collection_exists(parents_collection_name):
                await self.client.delete_collection(
                    collection_name=parents_collection_name
                )
        except UnexpectedResponse as e:
            if e.status_code == 404:
                return None
            raise VectorDatabaseError(str(e))
        except Exception as e:
            raise VectorDatabaseError(str(e))

    async def delete_by_filter(self, collection_name: str, key: str, value: Any) -> None:
        collections_to_clear = [collection_name, f"{collection_name}_parents"]
        for target_coll in collections_to_clear:
            try:
                await self.client.delete(
                    collection_name=target_coll,
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
            except UnexpectedResponse as e:
                if e.status_code == 404:
                    return None
                raise VectorDatabaseError(str(e))
            except Exception as e:
                raise VectorDatabaseError(str(e))

    async def upsert(
        self,
        collection_name: str,
        items: List[Dict[str, Any]],
        is_vector: bool = True
    ):
        texts = [item["content"] for item in items]
        
        try:
            embeddings = await self.embedder.embed_documents(texts)
        except AIProviderError:
            raise
        except Exception as e:
            raise EmbedderError(str(e))

        points = [
            PointStruct(
                id=item["metadata"]["chunk_id"],
                vector=vector if is_vector else {},
                payload=item,
            )
            for item, vector in zip(items, embeddings)          
        ]

        try:
            await self.client.upsert(
                collection_name=collection_name,
                points=points,
            )
        except UnexpectedResponse as e:
            if e.status_code == 404:
                raise CollectionNotFoundError(collection_name)
            raise VectorDatabaseError(str(e))
        except Exception as e:
            raise VectorDatabaseError(str(e))

    async def search_points(
        self,
        query: str,
        collection_name: str,
        limit: int = 30,
        with_payload: bool = True,
        **kwargs,
    ) -> List[RAGDocument]:
        try:
            query_vector = await self.embedder.embed_query(query)
        except AIProviderError:
            raise
        except Exception as e:
            raise EmbedderError(str(e))

        try:
            retrieved_docs = await self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                with_payload=with_payload,
                limit=limit,
            )
            return [
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
        except UnexpectedResponse as e:
            if e.status_code == 404:
                raise CollectionNotFoundError(collection_name)
            raise VectorDatabaseError(str(e))
        except Exception as e:
            raise VectorDatabaseError(str(e))

    async def get_documents_by_ids(
        self,
        collection_name: str,
        ids: List[str],
        with_payload: bool = True,
    ) -> List[RAGDocument]:
        try:
            points = await self.client.retrieve(
                collection_name=collection_name,
                ids=ids,
                with_payload=with_payload,
            )
            return [
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
        except UnexpectedResponse as e:
            if e.status_code == 404:
                raise CollectionNotFoundError(collection_name)
            raise VectorDatabaseError(str(e))
        except Exception as e:
            raise VectorDatabaseError(str(e))

    async def get_chunks(
        self,
        collection_name: str,
        document_id: UUID,
        limit: int | None = None,
        offset: str | None = None,
    ) -> Tuple[List[RAGDocument], str | None]:

        try:            
            query_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="metadata.document_id",
                        match=models.MatchValue(
                            value=str(document_id)
                        ),
                    )
                ]
            )

            points, next_offset = await self.client.scroll(
                collection_name=collection_name,
                scroll_filter=query_filter,
                limit=limit,
                offset=offset,
                with_payload=True,
                with_vectors=False,
            )

            chunks = [
                RAGDocument(
                    id=str(point.id),
                    content=point.payload.get("content", ""),
                    raw_content=point.payload.get("raw_content", ""),
                    metadata=point.payload.get("metadata", {}),
                    source=point.payload.get("source", ""),
                    is_parent=point.payload.get("is_parent", False),
                )
                for point in points
            ]
            return chunks, str(next_offset) if next_offset is not None else None

        except UnexpectedResponse as e:
            if e.status_code == 404:
                raise CollectionNotFoundError(collection_name)

            raise VectorDatabaseError(str(e))

        except Exception as e:
            raise VectorDatabaseError(
                f"Ошибка получения chunks из Qdrant: {e}"
            )    

    async def ping(self) -> bool:
        try:
            await self.client.get_collections()
            return True
        except Exception as e:
            return False

    async def close(self):
        try:
            await self.client.close()
        except Exception as e:
            raise VectorDatabaseError(f"Ошибка при закрытии соединения Qdrant: {e}")