import logging
from typing import List, Dict, Any
from elasticsearch import AsyncElasticsearch, helpers
from elasticsearch.exceptions import BadRequestError, NotFoundError

from src.core.config import settingsElastic
from src.rag.repositories.keyword_repository.base import BaseKeywordRepository
from src.rag.schemas.document import RAGDocument, KeywordIndexSchema
from src.core.exceptions.repo_exceptions import (
    CollectionAlreadyExistsError,
    CollectionNotFoundError,
    KeywordDatabaseError,
)

logger = logging.getLogger(__name__)
auth_data = settingsElastic.get_auth_data


class ElasticRepository(BaseKeywordRepository):
    def __init__(self):
        try:
            self.client = AsyncElasticsearch(**auth_data)
            logger.info("Клиент Elasticsearch успешно создан")
        except Exception as e:
            logger.exception("Ошибка создания клиента Elasticsearch")
            raise KeywordDatabaseError(f"Ошибка подключения к Elasticsearch: {e}")

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
        try:
            await self.client.indices.create(index=index, mappings=mappings)
            logger.info("Индекс Elasticsearch успешно создан: индекс=%s", index)
        except BadRequestError as e:
            if "resource_already_exists_exception" in str(e):
                logger.error("Индекс Elasticsearch уже существует: индекс=%s", index)
                raise CollectionAlreadyExistsError(index)
            logger.error("Ошибка создания индекса Elasticsearch: индекс=%s, ошибка=%s", index, e)
            raise KeywordDatabaseError(str(e))
        except Exception as e:
            logger.exception("Непредвиденная ошибка создания индекса Elasticsearch: индекс=%s", index)
            raise KeywordDatabaseError(str(e))

    async def get_indices(self, include_parents: bool = False) -> List[KeywordIndexSchema]:
        try:
            indices = await self.client.cat.indices(format="json")
            result = [
                KeywordIndexSchema(name=index["index"])
                for index in indices
                if include_parents
                or (
                    not index["index"].endswith("_parents")
                    and not index["index"].startswith(".")
                )
            ]
            logger.info("Список индексов Elasticsearch получен: количество=%d", len(result))
            return result
        except Exception as e:
            logger.error("Ошибка получения списка индексов Elasticsearch: ошибка=%s", e)
            raise KeywordDatabaseError(f"Ошибка получения списка индексов: {e}")

    async def get_index_details(self, index: str) -> KeywordIndexSchema | None:
        try:
            info = await self.client.count(index=index)
            logger.info("Информация об индексе получена: индекс=%s, документов=%d", index, info["count"])
            return KeywordIndexSchema(
                name=index,
                points_count=info["count"]
            )
        except NotFoundError:
            logger.error("Индекс Elasticsearch не найден: индекс=%s", index)
            raise CollectionNotFoundError(index)
        except Exception as e:
            logger.error("Ошибка получения информации об индексе: индекс=%s, ошибка=%s", index, e)
            raise KeywordDatabaseError(str(e))

    async def delete_index(self, index: str):
        try:
            await self.client.indices.delete(index=index)
        except NotFoundError:
            logger.warning("Индекс Elasticsearch не найден при удалении: индекс=%s", index)
            return None
        except Exception as e:
            logger.error("Ошибка удаления индекса Elasticsearch: индекс=%s, ошибка=%s", index, e)
            raise KeywordDatabaseError(str(e))

    async def clear_index(self, index: str):
        try:
            await self.client.delete_by_query(index=index, query={"match_all": {}})
            logger.info("Индекс Elasticsearch успешно удалён: индекс=%s", index)
        except NotFoundError:
            logger.warning("Индекс Elasticsearch не найден при очистке: индекс=%s", index)
            return None
        except Exception as e:
            logger.error("Ошибка очистки индекса Elasticsearch: индекс=%s, ошибка=%s", index, e)
            raise KeywordDatabaseError(str(e))

    async def delete_by_filter(self, index_name: str, field: str, value: Any) -> None:
        field_name = field if field.endswith(".keyword") or not isinstance(value, str) else f"{field}.keyword"
        query = {
            "query": {
                "term": {
                    field_name: value
                }
            }
        }
        try:
            await self.client.delete_by_query(
                index=index_name,
                body=query,
                conflicts="proceed",
                refresh=True
            )
            logger.info("Документы Elasticsearch удалены по фильтру: индекс=%s, поле=%s", index_name, field_name)
        except NotFoundError:
            logger.warning("Индекс Elasticsearch не найден при удалении по фильтру: индекс=%s", index_name)
            return None
        except Exception as e:
            logger.error("Ошибка удаления документов по фильтру: индекс=%s, ошибка=%s", index_name, e)
            raise KeywordDatabaseError(str(e))

    async def index_documents(self, index: str, items: List[Dict[str, Any]]):
        actions = [
            {
                "_index": index,
                "_id": item["metadata"]["chunk_id"],
                "_source": {
                    "content": item["content"],
                    "metadata": item["metadata"],
                    "source": item["source"],
                },
            }
            for item in items
        ]
        try:
            await helpers.async_bulk(self.client, actions)
            await self.client.indices.refresh(index=index)
            logger.info("Индексация документов в Elasticsearch завершена: индекс=%s, документов=%d", index, len(items))
        except NotFoundError:
            logger.error("Индекс Elasticsearch не найден при индексации: индекс=%s", index)
            raise CollectionNotFoundError(index)
        except Exception as e:
            logger.error("Ошибка массовой индексации Elasticsearch: индекс=%s, документов=%d, ошибка=%s", index, len(items), e)
            raise KeywordDatabaseError(f"Ошибка массовой индексации: {e}")

    async def search(
        self, query: str, index: str, limit: int = 30, **kwargs
    ) -> List[RAGDocument]:
        logger.info("Поиск в Elasticsearch: индекс=%s, лимит=%d, длина запроса=%d", index, limit, len(query))
        try:
            retrieved_docs = await self.client.search(
                index=index,
                query={"match": {"content": query}},
                size=limit,
            )
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

            logger.info("Поиск в Elasticsearch завершён: индекс=%s, найдено=%d", index, len(result))
            return result
        except NotFoundError:
            logger.error("Индекс Elasticsearch не найден при поиске: индекс=%s", index)
            raise CollectionNotFoundError(index)
        except Exception as e:
            logger.error("Ошибка поиска в Elasticsearch: индекс=%s, ошибка=%s", index, e)
            raise KeywordDatabaseError(str(e))

    async def get_documents_by_ids(
        self,
        index: str,
        ids: List[str],
        **kwargs
    ) -> List[RAGDocument]:
        try:
            response = await self.client.mget(index=index, ids=ids)
            result = [
                RAGDocument(
                    id=doc["_id"],
                    content=doc["_source"]["content"],
                    metadata=doc["_source"]["metadata"],
                    source=doc["_source"]["source"],
                )
                for doc in response["docs"]
                if doc.get("found", False)
            ]
            logger.info("Документы Elasticsearch получены по ID: индекс=%s, запрошено=%d, найдено=%d", index, len(ids), len(result))
            return result
        except NotFoundError:
            logger.error("Индекс Elasticsearch не найден при получении документов: индекс=%s", index)
            raise CollectionNotFoundError(index)
        except Exception as e:
            logger.error("Ошибка получения документов Elasticsearch по ID: индекс=%s, ошибка=%s", index, e)
            raise KeywordDatabaseError(str(e))

    async def ping(self) -> bool:
        try:
            result = await self.client.ping()
            logger.info("Проверка Elasticsearch завершена: доступен=%s", result)
            return result
        except Exception as e:
            logger.error("Ошибка проверки доступности Elasticsearch: ошибка=%s", e)
            raise

    async def close(self):
        try:
            await self.client.close()
            logger.info("Клиент Elasticsearch успешно закрыт")
        except Exception as e:
            logger.error("Ошибка при закрытии Elasticsearch: ошибка=%s", e)
            raise KeywordDatabaseError(f"Ошибка при закрытии Elasticsearch: {e}")