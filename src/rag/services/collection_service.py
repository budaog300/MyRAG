import logging
import asyncio
from typing import List, Dict, Any, Optional
from src.rag.repositories import BaseKeywordRepository, BaseVectorRepository
from src.rag.schemas.document import CollectionSchema
from src.core.exceptions.repo_exceptions import (
    CollectionAlreadyExistsError,
    CollectionNotFoundError,
    CollectionOperationError,
    DocumentNotFoundError,
    InvalidCollectionNameError,
)

logger = logging.getLogger(__name__)


class CollectionService:
    def __init__(self, vector_repo: BaseVectorRepository, keyword_repo: BaseKeywordRepository):
        self.vector_repo = vector_repo
        self.keyword_repo = keyword_repo

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
        except CollectionAlreadyExistsError:
            raise
        except Exception as exc:
            logger.error(f"Ошибка при создании коллекции '{name}': {exc}")
            raise CollectionOperationError(operation="create", collection_name=name, details=str(exc)) from exc

    async def get_collections(self, include_parents: bool = False) -> List[CollectionSchema]:
        try:
            return await self.vector_repo.get_collections(include_parents=include_parents)
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
        except CollectionNotFoundError:
            raise
        except Exception as exc:
            logger.error(f"Ошибка при получении деталей коллекции '{name}': {exc}")
            raise CollectionOperationError(
                operation="get_details",
                collection_name=name,
                details=str(exc),
            ) from exc

    async def delete_document_by_file_id(self, collection_name: str, file_id: str) -> None:
        self._validate_collection_name(collection_name)
        if not file_id or not file_id.strip():
            raise CollectionOperationError(
                operation="delete_document",
                collection_name=collection_name,
                details="file_id не может быть пустым.",
            )

        logger.info(f"Удаление документов с file_id='{file_id}' из коллекции '{collection_name}'")
        try:
            await asyncio.gather(
                self.vector_repo.delete_by_filter(collection_name, key="metadata.file_id", value=file_id),
                self.vector_repo.delete_by_filter(f"{collection_name}_parents", key="metadata.file_id", value=file_id),
                self.keyword_repo.delete_by_filter(collection_name, field="metadata.file_id", value=file_id),
            )
        except (CollectionNotFoundError, DocumentNotFoundError):
            raise
        except Exception as exc:
            logger.error(f"Ошибка при удалении файлов file_id='{file_id}' из коллекции '{collection_name}': {exc}")
            raise CollectionOperationError(
                operation="delete_document",
                collection_name=collection_name,
                details=str(exc),
            ) from exc

    async def clear_collection(self, name: str) -> None:
        self._validate_collection_name(name)

        logger.info(f"Очистка содержимого коллекции '{name}'")
        try:
            await asyncio.gather(
                self.vector_repo.clear_collection(name),
                self.vector_repo.clear_collection(f"{name}_parents"),
                self.keyword_repo.clear_index(name),
            )
        except CollectionNotFoundError:
            raise
        except Exception as exc:
            logger.error(f"Ошибка при очистке коллекции '{name}': {exc}")
            raise CollectionOperationError(operation="clear", collection_name=name, details=str(exc)) from exc

    async def delete_collection(self, name: str) -> None:
        self._validate_collection_name(name)

        logger.info(f"Удаление коллекции '{name}")
        try:
            await asyncio.gather(
                self.vector_repo.delete_collection(name),
                self.vector_repo.delete_collection(f"{name}_parents"),
                self.keyword_repo.delete_index(name),
            )
        except CollectionNotFoundError:
            raise
        except Exception as exc:
            logger.error(f"Ошибка при удалении коллекции '{name}': {exc}")
            raise CollectionOperationError(operation="delete", collection_name=name, details=str(exc)) from exc