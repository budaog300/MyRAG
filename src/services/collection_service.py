import logging
import asyncio
from uuid import UUID
from typing import List, Dict, Any, Optional

from src.services.s3_service import S3Service
from src.rag.repositories import BaseKeywordRepository, BaseVectorRepository
from src.rag.schemas.document import CollectionSchema
from src.db.repositories import RepositoryContainer
from src.db.models import CollectionModel
from src.core.exceptions import BaseAppException
from src.core.exceptions.repo_exceptions import (
    CollectionOperationError,
    InvalidCollectionNameError,
    CollectionNotFoundError
)

logger = logging.getLogger(__name__)


class CollectionService:
    def __init__(
            self, 
            vector_repo: BaseVectorRepository, 
            keyword_repo: BaseKeywordRepository, 
            s3_service: S3Service,
            repos: RepositoryContainer,
        ):
        self.vector_repo = vector_repo
        self.keyword_repo = keyword_repo
        self.s3_service = s3_service
        self.repos = repos

    def _validate_collection_name(self, name: str) -> None:
        """Проверяет валидность названия коллекции."""
        if not name or not name.strip():
            raise InvalidCollectionNameError(collection_name=name)

    async def create_collection(
        self,
        name: str,
        size: int = 1024,
        distance: str = "COSINE",
        description: str | None = None,
    ) -> CollectionModel:
        self._validate_collection_name(name)

        if size <= 0:
            raise CollectionOperationError(
                operation="create",
                collection_name=name,
                details="Размерность вектора (size) должна быть больше 0.",
            )

        logger.info(f"Создание коллекции '{name}' (size={size}, distance={distance})")

        collection = await self.repos.collection_repo.create(
            name=name,
            description=description,
        )

        await self.repos.collection_repo.session.commit()

        collection_name = str(collection.id)
       
        try:
            await asyncio.gather(
                self.vector_repo.create_collection(collection_name=collection_name, size=size, distance=distance),
                self.keyword_repo.create_index(index=collection_name),
            )
        except BaseAppException:
            raise
        except Exception as exc:
            logger.error(f"Ошибка при создании коллекции '{name}': {exc}")
            raise CollectionOperationError(operation="create", collection_name=name, details=str(exc)) from exc

    async def get_collections(self) -> List[CollectionSchema]:
        try:
            collections = await self.repos.collection_repo.get_all()
            return collections
        except BaseAppException:
            raise
        except Exception as exc:
            logger.error(f"Ошибка при получении списка коллекций: {exc}")
            raise CollectionOperationError(
                operation="get_collections",
                collection_name="all",
                details=str(exc),
            ) from exc

    async def get_collection_details(self, collection_id: UUID) -> Dict[str, Any]:
        try:
            collection = await self.repos.collection_repo.get_by_name(collection_id)

            collection_name = str(collection.id)

            if collection is None:
                raise CollectionNotFoundError(collection_name)
            
            vector_repo_info, keyword_repo_info = await asyncio.gather(
                self.vector_repo.get_collection_details(collection_name),
                self.keyword_repo.get_index_details(collection_name),
            )

            return {
                "id": collection_name,
                "name": collection.name,
                "description": collection.description,
                "created_at": collection.created_at,
                "updated_at": collection.updated_at,
                "vector_repo_info": vector_repo_info,
                "keyword_repo_info": keyword_repo_info,
            }
        except BaseAppException:
            raise
        except Exception as exc:
            logger.error(f"Ошибка при получении деталей коллекции '{collection_id}': {exc}")
            raise CollectionOperationError(
                operation="get_details",
                collection_name=collection_id,
                details=str(exc),
            ) from exc

    async def clear_collection(self, collection_id: UUID) -> None:
        collection = await self.repos.collection_repo.get_by_name(collection_id)
        if collection is None:
            raise CollectionNotFoundError(collection_id)
        logger.info(f"Очистка содержимого коллекции '{collection.name}'")
        try:
            documents = await self.repos.document_repo.get_by_collection_id(collection.id)
            collection_name = str(collection_id)
            await asyncio.gather(
                self.vector_repo.clear_collection(collection_name),
                self.keyword_repo.clear_index(collection_name),
                *[
                    self.s3_service.delete_file(document.s3_key)
                    for document in documents
                ]
            )
            logger.info(f"Коллекция '{collection.name}' очищена. Удалено S3 файлов: {len(documents)}")
        except BaseAppException:
            raise
        except Exception as exc:
            logger.error(f"Ошибка при очистке коллекции '{collection.name}': {exc}")
            raise CollectionOperationError(operation="clear", collection_name=collection.name, details=str(exc)) from exc

    async def delete_collection(self, collection_id: UUID) -> None:
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
        self, collection_id: UUID, document_id: UUID,
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