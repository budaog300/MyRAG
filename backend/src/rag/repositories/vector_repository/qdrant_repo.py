import logging
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

logger = logging.getLogger(__name__)
auth_data = settingsQdrant.get_auth_data


class QdrantRepository(BaseVectorRepository):
    def __init__(self, embedder: BaseEmbedderProvider):
        try:
            self.client = AsyncQdrantClient(**auth_data)
            logger.info("Клиент Qdrant успешно создан")
        except Exception as e:
            logger.exception("Ошибка инициализации клиента Qdrant")
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
            logger.info("Коллекции Qdrant успешно созданы: коллекция=%s, родители=%s", collection_name, parents_collection_name)
        except UnexpectedResponse as e:
            if e.status_code == 409 or "already exists" in str(e).lower():
                logger.error("Коллекция Qdrant уже существует: коллекция=%s", collection_name)
                raise CollectionAlreadyExistsError(collection_name)
            logger.error("Ошибка создания коллекции Qdrant: коллекция=%s, ошибка=%s", collection_name, e)
            raise VectorDatabaseError(str(e))
        except Exception as e:
            logger.exception("Непредвиденная ошибка создания коллекции Qdrant: коллекция=%s", collection_name)
            raise VectorDatabaseError(f"Неизвестная ошибка при создании коллекции: {e}")

    async def get_collections(self, include_parents: bool = False) -> List[VectorCollectionSchema]:
        try:
            result = await self.client.get_collections()
            if include_parents:
                collections = [
                    VectorCollectionSchema(name=col.name)
                    for col in result.collections
                ]
            else:
                collections = [
                    VectorCollectionSchema(name=col.name)
                    for col in result.collections
                    if not col.name.endswith("_parents")
                ]

            logger.info("Список коллекций Qdrant получен: количество=%d", len(collections))
            return collections
        except Exception as e:
            logger.error("Ошибка получения списка коллекций Qdrant: ошибка=%s", e)
            raise VectorDatabaseError(f"Ошибка при получении списка коллекций: {e}")

    async def get_collection_details(self, collection_name: str) -> VectorCollectionSchema | None:
        try:
            info = await self.client.get_collection(collection_name)
            result = VectorCollectionSchema(
                name=collection_name,
                status=info.status,
                points_count=info.points_count or 0,
                size=info.config.params.vectors.size,
                distance=info.config.params.vectors.distance,
            )
            logger.info("Информация о коллекции Qdrant получена: коллекция=%s, точек=%d", collection_name, result.points_count)
            return result

        except UnexpectedResponse as e:
            if e.status_code == 404:
                logger.error("Коллекция Qdrant не найдена: коллекция=%s", collection_name)
                raise CollectionNotFoundError(collection_name)
            logger.error("Ошибка получения информации о коллекции Qdrant: коллекция=%s, ошибка=%s", collection_name, e)
            raise VectorDatabaseError(str(e))
        except Exception as e:
            logger.error("Ошибка получения информации о коллекции Qdrant: коллекция=%s, ошибка=%s", collection_name, e)
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
            logger.info("Коллекция Qdrant очищена: коллекция=%s", collection_name)
        except UnexpectedResponse as e:
            if e.status_code == 404:
                logger.warning("Коллекция Qdrant не найдена при очистке: коллекция=%s", collection_name)
                return None
            logger.error("Ошибка очистки коллекции Qdrant: коллекция=%s, ошибка=%s", collection_name, e)
            raise VectorDatabaseError(str(e))
        except Exception as e:
            logger.error("Ошибка очистки коллекции Qdrant: коллекция=%s, ошибка=%s", collection_name, e)
            raise VectorDatabaseError(str(e))

    async def delete_collection(self, collection_name: str):
        try:
            await self.client.delete_collection(collection_name=collection_name)
            parents_collection_name = f"{collection_name}_parents"

            if await self.client.collection_exists(parents_collection_name):
                await self.client.delete_collection(
                    collection_name=parents_collection_name
                )
            logger.info("Коллекция Qdrant успешно удалена: коллекция=%s", collection_name)
        except UnexpectedResponse as e:
            if e.status_code == 404:
                logger.warning("Коллекция Qdrant не найдена при удалении: коллекция=%s", collection_name)
                return None
            logger.error("Ошибка удаления коллекции Qdrant: коллекция=%s, ошибка=%s", collection_name, e)
            raise VectorDatabaseError(str(e))
        except Exception as e:
            logger.error("Ошибка удаления коллекции Qdrant: коллекция=%s, ошибка=%s", collection_name, e)
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
                logger.debug("Фильтр применён к коллекции Qdrant: коллекция=%s, поле=%s", target_coll, key)
            except UnexpectedResponse as e:
                if e.status_code == 404:
                    logger.warning("Коллекция Qdrant не найдена при удалении по фильтру: коллекция=%s", target_coll)
                    return None
                logger.error("Ошибка удаления по фильтру Qdrant: коллекция=%s, ошибка=%s", target_coll, e)
                raise VectorDatabaseError(str(e))
            except Exception as e:
                logger.exception("Ошибка удаления по фильтру Qdrant: коллекция=%s, ошибка=%s", target_coll, e)
                raise VectorDatabaseError(str(e))
        logger.info("Удаление по фильтру Qdrant завершено: коллекция=%s", collection_name)

    async def upsert(
        self,
        collection_name: str,
        items: List[Dict[str, Any]],
        is_vector: bool = True
    ):
        texts = [item["content"] for item in items]
        
        try:
            embeddings = await self.embedder.embed_documents(texts)
            if len(items) != len(embeddings):
                logger.error("Количество embeddings не совпадает с количеством документов: коллекция=%s, документов=%d, embeddings=%d", collection_name, len(items), len(embeddings))
                raise EmbedderError(
                    f"Количество embeddings ({len(embeddings)}) не совпадает "
                    f"с количеством items ({len(items)})"
                )
        except AIProviderError:
            raise
        except EmbedderError:
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
            logger.info("Документы успешно сохранены в Qdrant: коллекция=%s, документов=%d", collection_name, len(points))
        except UnexpectedResponse as e:
            if e.status_code == 404:
                logger.error("Коллекция Qdrant не найдена при сохранении: коллекция=%s", collection_name)
                raise CollectionNotFoundError(collection_name)
            logger.error("Ошибка сохранения документов в Qdrant: коллекция=%s, документов=%d, ошибка=%s", collection_name, len(points), e)
            raise VectorDatabaseError(str(e))
        except Exception as e:
            logger.error("Ошибка сохранения документов в Qdrant: коллекция=%s, ошибка=%s", collection_name, e)
            raise VectorDatabaseError(str(e))

    async def search_points(
        self,
        query: str,
        collection_name: str,
        limit: int = 30,
        with_payload: bool = True,
        **kwargs,
    ) -> List[RAGDocument]:
        logger.info("Поиск в Qdrant: коллекция=%s, лимит=%d, длина запроса=%d", collection_name, limit, len(query))
        try:
            query_vector = await self.embedder.embed_query(query)
        except AIProviderError:
            raise
        except Exception as e:
            logger.error("Ошибка получения embedding для поиска Qdrant: коллекция=%s, ошибка=%s", collection_name, e)
            raise EmbedderError(str(e))

        try:
            retrieved_docs = await self.client.query_points(
                collection_name=collection_name,
                query=query_vector,
                with_payload=with_payload,
                limit=limit,
            )
            result = [
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
            logger.info("Поиск в Qdrant завершён: коллекция=%s, найдено=%d", collection_name, len(result))
            return result
        except UnexpectedResponse as e:
            if e.status_code == 404:
                logger.error("Коллекция Qdrant не найдена при поиске: коллекция=%s", collection_name)
                raise CollectionNotFoundError(collection_name)
            logger.error("Ошибка поиска в Qdrant: коллекция=%s, ошибка=%s", collection_name, e)
            raise VectorDatabaseError(str(e))
        except Exception as e:
            logger.error("Ошибка поиска в Qdrant: коллекция=%s, ошибка=%s", collection_name, e)
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
            result = [
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
            logger.info("Документы Qdrant получены по ID: коллекция=%s, запрошено=%d, найдено=%d", collection_name, len(ids), len(result))
            return result
        except UnexpectedResponse as e:
            if e.status_code == 404:
                logger.error("Коллекция Qdrant не найдена при получении документов: коллекция=%s", collection_name)
                raise CollectionNotFoundError(collection_name)
            logger.error("Ошибка получения документов Qdrant по ID: коллекция=%s, ошибка=%s", collection_name, e)
            raise VectorDatabaseError(str(e))
        except Exception as e:
            logger.error("Ошибка получения документов Qdrant по ID: коллекция=%s, ошибка=%s", collection_name, e)
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
            next_offset_value = str(next_offset) if next_offset is not None else None
            logger.info("Chunks из Qdrant получены: коллекция=%s, document_id=%s, найдено=%d, есть следующая страница=%s", collection_name, document_id, len(chunks), next_offset_value is not None)
            return chunks, next_offset_value

        except UnexpectedResponse as e:
            if e.status_code == 404:
                logger.error("Коллекция Qdrant не найдена при получении chunks: коллекция=%s", collection_name)
                raise CollectionNotFoundError(collection_name)
            logger.error("Ошибка получения chunks из Qdrant: коллекция=%s, document_id=%s, ошибка=%s", collection_name, document_id, e)
            raise VectorDatabaseError(str(e))

        except Exception as e:
            logger.error("Ошибка получения chunks из Qdrant: коллекция=%s, document_id=%s, ошибка=%s", collection_name, document_id, e)
            raise VectorDatabaseError(
                f"Ошибка получения chunks из Qdrant: {e}"
            )    

    async def ping(self) -> bool:
        try:
            await self.client.get_collections()
            logger.info("Qdrant доступен")
            return True
        except Exception as e:
            logger.error("Qdrant недоступен: ошибка=%s", e)
            return False

    async def close(self):
        try:
            await self.client.close()
            logger.info("Клиент Qdrant успешно закрыт")
        except Exception as e:
            logger.error("Ошибка при закрытии соединения Qdrant: ошибка=%s", e)
            raise VectorDatabaseError(
                f"Ошибка при закрытии соединения Qdrant: {e}"
            )