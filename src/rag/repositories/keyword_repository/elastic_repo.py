import asyncio
from typing import List, Dict, Any
from elasticsearch import AsyncElasticsearch, helpers
from elasticsearch.exceptions import BadRequestError, NotFoundError

from src.core.config import settingsElastic
from src.rag.repositories import BaseKeywordRepository
from src.rag.schemas.document import RAGDocument, IndexSchema
from src.core.exceptions.repo_exceptions import (
    CollectionAlreadyExistsError,
    CollectionNotFoundError,
    KeywordDatabaseError,
)

auth_data = settingsElastic.get_auth_data


class ElasticRepository(BaseKeywordRepository):
    def __init__(self):
        try:
            self.client = AsyncElasticsearch(**auth_data)
        except Exception as e:
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
        except BadRequestError as e:
            if "resource_already_exists_exception" in str(e):
                raise CollectionAlreadyExistsError(index)
            raise KeywordDatabaseError(str(e))
        except Exception as e:
            raise KeywordDatabaseError(str(e))

    async def get_indices(self, include_parents: bool = False) -> List[IndexSchema]:
        try:
            indices = await self.client.cat.indices(format="json")
            if include_parents:
                return [IndexSchema(name=index["index"]) for index in indices]
            return [
                IndexSchema(name=index["index"])
                for index in indices
                if not index["index"].endswith("_parents") and not index["index"].startswith(".")
            ]
        except Exception as e:
            raise KeywordDatabaseError(f"Ошибка получения списка индексов: {e}")

    async def get_index_details(self, index: str):
        try:
            return await self.client.count(index=index)
        except NotFoundError:
            raise CollectionNotFoundError(index)
        except Exception as e:
            raise KeywordDatabaseError(str(e))

    async def delete_index(self, index: str):
        try:
            await self.client.indices.delete(index=index)
            parents_index = f"{index}_parents"
            if await self.client.indices.exists(index=parents_index):
                await self.client.indices.delete(index=parents_index)
        except NotFoundError:
            raise CollectionNotFoundError(index)
        except Exception as e:
            raise KeywordDatabaseError(str(e))

    async def clear_index(self, index: str):
        try:
            await self.client.delete_by_query(index=index, query={"match_all": {}})
            parents_index = f"{index}_parents"
            if await self.client.indices.exists(index=parents_index):
                await self.client.delete_by_query(index=parents_index, query={"match_all": {}})
        except NotFoundError:
            raise CollectionNotFoundError(index)
        except Exception as e:
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
        except NotFoundError:
            raise CollectionNotFoundError(index_name)
        except Exception as e:
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
        except NotFoundError:
            raise CollectionNotFoundError(index)
        except Exception as e:
            raise KeywordDatabaseError(f"Ошибка массовой индексации: {e}")

    async def search(
        self, query: str, index: str, limit: int = 30, **kwargs
    ) -> List[RAGDocument]:
        try:
            retrieved_docs = await self.client.search(
                index=index,
                query={"match": {"content": query}},
                size=limit,
            )
            return [
                RAGDocument(
                    id=hit["_id"],
                    content=hit["_source"]["content"],
                    score=hit["_score"],
                    metadata=hit["_source"]["metadata"],
                    source=hit["_source"]["source"],
                )
                for hit in retrieved_docs["hits"]["hits"]
            ]
        except NotFoundError:
            raise CollectionNotFoundError(index)
        except Exception as e:
            raise KeywordDatabaseError(str(e))

    async def get_documents_by_ids(
        self,
        index: str,
        ids: List[str],
        **kwargs
    ) -> List[RAGDocument]:
        try:
            response = await self.client.mget(index=index, ids=ids)
            return [
                RAGDocument(
                    id=doc["_id"],
                    content=doc["_source"]["content"],
                    metadata=doc["_source"]["metadata"],
                    source=doc["_source"]["source"],
                )
                for doc in response["docs"]
                if doc.get("found", False)
            ]
        except NotFoundError:
            raise CollectionNotFoundError(index)
        except Exception as e:
            raise KeywordDatabaseError(str(e))

    async def close(self):
        try:
            await self.client.close()
        except Exception as e:
            raise KeywordDatabaseError(f"Ошибка при закрытии Elasticsearch: {e}")