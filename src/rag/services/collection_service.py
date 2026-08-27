import logging
import asyncio
from uuid import UUID
from typing import List, Dict, Any, Optional
from src.rag.services.s3_service import S3Service
from src.rag.repositories import BaseKeywordRepository, BaseVectorRepository
from src.rag.schemas.document import CollectionSchema, RAGDocument
from src.core.exceptions import BaseAppException
from src.core.exceptions.repo_exceptions import (
    CollectionOperationError,
    InvalidCollectionNameError,
)

logger = logging.getLogger(__name__)


class CollectionService:
    def __init__(self, vector_repo: BaseVectorRepository, keyword_repo: BaseKeywordRepository, s3_service: S3Service):
        self.vector_repo = vector_repo,
        self.keyword_repo = keyword_repo,
        self.s3_service = s3_service

    def _validate_collection_name(self, name: str) -> None:
        """Проверяет валидность названия коллекции."""
        if not name or not name.strip():
            raise InvalidCollectionNameError(collection_name=name)

    async def create_collection(self, name: str, size: int = 1024, distance: str = "COSINE") -> None:
        self._validate_collection_name(name)

        if size <= 0:
            raise CollectionOperationError(
                operation="create",
                collection_name=name,
                details="Размерность вектора (size) должна быть больше 0.",
            )

        logger.info(f"Создание коллекции '{name}' (size={size}, distance={distance})")
        try:
            await asyncio.gather(
                self.vector_repo.create_collection(collection_name=name, size=size, distance=distance),
                self.keyword_repo.create_index(index=name),
            )
        except BaseAppException:
            raise
        except Exception as exc:
            logger.error(f"Ошибка при создании коллекции '{name}': {exc}")
            raise CollectionOperationError(operation="create", collection_name=name, details=str(exc)) from exc

    async def get_collections(self, include_parents: bool = False) -> List[CollectionSchema]:
        try:
            return await self.vector_repo.get_collections(include_parents=include_parents)
        except BaseAppException:
            raise
        except Exception as exc:
            logger.error(f"Ошибка при получении списка коллекций: {exc}")
            raise CollectionOperationError(
                operation="get_collections",
                collection_name="all",
                details=str(exc),
            ) from exc

    async def get_collection_details(self, name: str) -> Dict[str, Any]:
        self._validate_collection_name(name)

        try:
            vector_repo_info, keyword_repo_info = await asyncio.gather(
                self.vector_repo.get_collection_details(name),
                self.keyword_repo.get_index_details(name),
            )
            return {
                "name": name,
                "vector_repo_info": vector_repo_info,
                "keyword_repo_info": keyword_repo_info,
            }
        except BaseAppException:
            raise
        except Exception as exc:
            logger.error(f"Ошибка при получении деталей коллекции '{name}': {exc}")
            raise CollectionOperationError(
                operation="get_details",
                collection_name=name,
                details=str(exc),
            ) from exc

    async def clear_collection(self, name: str) -> None:
        self._validate_collection_name(name)

        logger.info(f"Очистка содержимого коллекции '{name}'")
        try:
            s3_keys = await self.vector_repo.get_s3_keys(
                collection_name=name,
            )
            await asyncio.gather(
                self.vector_repo.clear_collection(name),
                self.keyword_repo.clear_index(name),
            )
            await asyncio.gather(
                *[
                    self.s3_service.delete_file(s3_key)
                    for s3_key in s3_keys
                ]
            )
            logger.info(f"Коллекция '{name}' очищена. Удалено S3 файлов: {len(s3_keys)}")
        except BaseAppException:
            raise
        except Exception as exc:
            logger.error(f"Ошибка при очистке коллекции '{name}': {exc}")
            raise CollectionOperationError(operation="clear", collection_name=name, details=str(exc)) from exc

    async def delete_collection(self, name: str) -> None:
        self._validate_collection_name(name)

        logger.info(f"Удаление коллекции '{name}")
        try:
            s3_keys = await self.vector_repo.get_s3_keys(
                collection_name=name,
            )
            await asyncio.gather(
                self.vector_repo.delete_collection(name),
                self.keyword_repo.delete_index(name),
            )
            await asyncio.gather(
                *[
                    self.s3_service.delete_file(s3_key)
                    for s3_key in s3_keys
                ]
            )
            logger.info(f"Коллекция '{name}' удалена. Удалено S3 файлов: {len(s3_keys)}")
        except BaseAppException:
            raise
        except Exception as exc:
            logger.error(f"Ошибка при удалении коллекции '{name}': {exc}")
            raise CollectionOperationError(operation="delete", collection_name=name, details=str(exc)) from exc

    async def delete_document(
        self, name: str, document_id: UUID,
    ) -> None:
        self._validate_collection_name(name)
        if document_id is None:
            raise CollectionOperationError(
                operation="delete_document",
                collection_name=name,
                details="document_id не может быть пустым.",
            )

        logger.info(f"Удаление документов с document_id='{document_id}' из коллекции '{name}'")

        try:
            s3_keys = await self.vector_repo.get_s3_keys_by_document_id(
                collection_name=name,
                document_id=document_id,
            )

            await asyncio.gather(
                self.vector_repo.delete_by_filter(name, key="metadata.document_id", value=str(document_id)),
                self.keyword_repo.delete_by_filter(name, field="metadata.document_id", value=str(document_id)),
            )
            await asyncio.gather(
                *[
                    self.s3_service.delete_file(s3_key)
                    for s3_key in s3_keys
                ]
            )

            logger.info(f"Документ '{document_id}' успешно удален из коллекции '{name}'. Удалено S3 файлов: {len(s3_keys)}")

        except BaseAppException:
            raise
        except Exception as exc:
            logger.error("Ошибка удаления документа '%s' из коллекции '%s': %s", document_id, name, exc, exc_info=True)

            raise CollectionOperationError(
                operation="delete_document",
                collection_name=name,
                details=str(exc),
            ) from exc

    async def get_chunks(
        self,
        collection_name: str,
        document_id: UUID | None = None,
        limit: int = 100,
        offset: str | None = None,
    ) -> List[RAGDocument]:

        self._validate_collection_name(collection_name)

        if limit <= 0:
            raise CollectionOperationError(
                operation="get_chunks",
                collection_name=collection_name,
                details="limit должен быть больше 0",
            )

        try:
            return await self.vector_repo.get_chunks(
                collection_name=collection_name,
                document_id=document_id,
                limit=limit,
                offset=offset
            )

        except BaseAppException:
            raise

        except Exception as exc:
            logger.error("Ошибка получения chunks коллекции '%s': %s", collection_name, exc)

            raise CollectionOperationError(operation="get_chunks", collection_name=collection_name, details=str(exc)) from exc
