import logging
import asyncio
from uuid import UUID
from typing import List, Dict, Any, Optional

from src.services.s3_service import S3Service
from src.rag.repositories import BaseKeywordRepository, BaseVectorRepository
from src.db.repositories import RepositoryContainer
from src.db.models import CollectionModel, DocumentModel
from src.core.exceptions import BaseAppException
from src.core.exceptions.repo_exceptions import (
    CollectionOperationError,
    InvalidCollectionNameError,
    CollectionNotFoundError,
    DocumentNotFoundError
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
            size=size,
            distance=distance,
            description=description,
        )

        await self.repos.collection_repo.session.commit()

        collection_name = str(collection.id)
       
        try:
            await asyncio.gather(
                self.vector_repo.create_collection(collection_name=collection_name, size=size, distance=distance),
                self.keyword_repo.create_index(index=collection_name),
            )
            return collection
        except BaseAppException:
            raise
        except Exception as exc:
            logger.error(f"Ошибка при создании коллекции '{name}': {exc}")
            raise CollectionOperationError(operation="create", collection_name=name, details=str(exc)) from exc

    async def get_collections(self) -> List[CollectionModel]:
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
            collection = await self.repos.collection_repo.get_by_id(collection_id)
            
            if collection is None:
                raise CollectionNotFoundError(collection_name)

            collection_name = str(collection.id)
            
            vector_repo_info, keyword_repo_info = await asyncio.gather(
                self.vector_repo.get_collection_details(collection_name),
                self.keyword_repo.get_index_details(collection_name),
            )

            return {
                "id": collection_name,
                "name": collection.name,
                "description": collection.description,
                "size": collection.size,
                "distance": collection.distance,
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
        collection = await self.repos.collection_repo.get_by_id(collection_id)
        if collection is None:
            raise CollectionNotFoundError(collection_id)
        logger.info(f"Очистка содержимого коллекции '{collection.name}'")
        try:
            documents = await self.repos.document_repo.get_all(collection.id)
            collection_name = str(collection_id)
            await asyncio.gather(
                self.vector_repo.clear_collection(collection_name),
                self.keyword_repo.clear_index(collection_name),
                *[
                    self.s3_service.delete_file(document.s3_key)
                    for document in documents
                ]
            )
            for document in documents:
                await self.repos.document_repo.delete(document)
            await self.repos.document_repo.session.commit()
            logger.info(f"Коллекция '{collection.name}' очищена. Удалено S3 файлов: {len(documents)}")
        except BaseAppException:
            raise
        except Exception as exc:
            logger.error(f"Ошибка при очистке коллекции '{collection.name}': {exc}")
            raise CollectionOperationError(operation="clear", collection_name=collection.name, details=str(exc)) from exc

    async def delete_collection(self, collection_id: UUID) -> None:
        collection = await self.repos.collection_repo.get_by_id(collection_id)
        if collection is None:
            raise CollectionNotFoundError(collection_id)
        logger.info(f"Удаление коллекции '{collection.name}")
        try:
            documents = await self.repos.document_repo.get_all(collection.id)
            collection_name = str(collection_id)
            await asyncio.gather(
                self.vector_repo.delete_collection(collection_name),
                self.keyword_repo.delete_index(collection_name),
                *[
                    self.s3_service.delete_file(document.s3_key)
                    for document in documents
                ]
            )
            await self.repos.collection_repo.delete(collection)
            await self.repos.collection_repo.session.commit()
            
            logger.info(f"Коллекция '{collection.name}' очищена. Удалено S3 файлов: {len(documents)}")
        except BaseAppException:
            raise
        except Exception as exc:
            logger.error(f"Ошибка при удалении коллекции '{collection.name}': {exc}")
            raise CollectionOperationError(operation="delete", collection_name=collection.name, details=str(exc)) from exc

    async def get_documents(
        self,
        collection_id: UUID,
        limit: int = 5,
        offset: int = 0,
    ) -> list[DocumentModel]:
        try:
            collection = await self.repos.collection_repo.get_by_id(collection_id)

            if collection is None:
                raise CollectionNotFoundError(str(collection_id))

            documents = await self.repos.document_repo.get_all(
                collection_id=collection_id,
                limit=limit,
                offset=offset,
            )
            total = await self.repos.document_repo.count_by_collection_id(
                collection_id
            )
            return documents, total
        except BaseAppException:
            raise
        except Exception as exc:
            logger.error(f"Ошибка при получении списка документов из коллекции '{collection_id}': {exc}")
            raise CollectionOperationError(
                operation="get_details",
                collection_name=collection_id,
                details=str(exc),
            ) from exc

    async def get_document(
        self,
        collection_id: UUID,
        document_id: UUID,
    ) -> DocumentModel:
        try:
            collection = await self.repos.collection_repo.get_by_id(collection_id)

            if collection is None:
                raise CollectionNotFoundError(str(collection_id))

            document = await self.repos.document_repo.get_by_id(
                collection_id=collection_id,
                document_id=document_id,
            )

            if document is None:
                raise DocumentNotFoundError(str(document_id), str(collection_id))
            
            return document
        except BaseAppException:
            raise
        except Exception as exc:
            logger.error(f"Ошибка при получении документа {document_id} из коллекции '{collection_id}': {exc}")
            raise CollectionOperationError(
                operation="get_details",
                collection_name=collection_id,
                details=str(exc),
            ) from exc

    async def delete_document(
        self, collection_id: UUID, document_id: UUID,
    ) -> None:
        collection = await self.repos.collection_repo.get_by_id(collection_id)
        if collection is None:
            raise CollectionNotFoundError(collection_id)

        logger.info(f"Удаление документов с document_id='{document_id}' из коллекции '{collection.name}'")
        try:
            document = await self.repos.document_repo.get_by_id(document_id)
            if document is None or document.collection_id != collection.id:
                raise DocumentNotFoundError(str(document_id), str(collection_id))
            collection_name = str(collection_id)
            await asyncio.gather(
                self.vector_repo.delete_by_filter(
                    collection_name,
                    key="metadata.document_id",
                    value=str(document_id),
                ),
                self.keyword_repo.delete_by_filter(
                    collection_name,
                    field="metadata.document_id",
                    value=str(document_id),
                ),
                self.s3_service.delete_file(document.s3_key),
            )
            await self.repos.document_repo.delete(document)
            await self.repos.document_repo.session.commit()

            logger.info(f"Документ '{document_id}' успешно удален из коллекции '{collection_name}'.")

        except BaseAppException:
            raise
        except Exception as exc:
            logger.error("Ошибка удаления документа '%s' из коллекции '%s': %s", document_id, collection.name, exc, exc_info=True)

            raise CollectionOperationError(
                operation="delete_document",
                collection_name=collection.name,
                details=str(exc),
            ) from exc