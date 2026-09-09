import logging
import asyncio
from langchain_community.document_loaders import TextLoader
from typing import List, Dict, Any

from src.rag.components.splitters import BaseDocumentSplitter
from src.services.convert_service import DocumentConverterService
from src.rag.schemas.document import RawDocumentSchema
from src.rag.repositories import BaseVectorRepository
from src.rag.repositories import BaseKeywordRepository
from src.core.exceptions import BaseAppException
from src.core.exceptions.document_service_exceptions import (    
    DocumentIngestionError,
    EmptyDocumentListError    
)
from src.core.exceptions.converter_exceptions import (
    DocumentConversionError
)
from src.core.exceptions.repo_exceptions import InvalidCollectionNameError
from src.core.exceptions.splitter_exception import TextSplittingError

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(
        self,
        repo: BaseVectorRepository,
        keyword_repo: BaseKeywordRepository,
        converter_service: DocumentConverterService,
        splitter: BaseDocumentSplitter
    ):
        self.repo = repo
        self.keyword_repo = keyword_repo
        self.converter_service = converter_service
        self.splitter = splitter
        
    async def ingest_files(
        self,
        collection_name: str,
        documents: List[RawDocumentSchema],
        chunk_size: int = 1000,
        chunk_overlap: int = 100,
    ) -> None:
        if not collection_name or not collection_name.strip():
            raise InvalidCollectionNameError(collection_name=collection_name)

        if not documents:
            raise EmptyDocumentListError(collection_name=collection_name)
        
        all_children: List[Dict[str, Any]] = []
        all_parents: List[Dict[str, Any]] = []

        logger.info("Начата индексация документов: коллекция=%s, документов=%d", collection_name, len(documents))

        for doc in documents:
            try:
                logger.info("Начата обработка документа: collection=%s, source=%s", collection_name, doc.source)
                markdown_text = await self.converter_service.convert_to_markdown(doc.source)

                chunks = self.splitter.split(
                    doc=doc,
                    markdown_text=markdown_text,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                )

                children_count = 0
                parents_count = 0

                for chunk in chunks:
                    chunk_dict = chunk.model_dump() if hasattr(chunk, "model_dump") else chunk

                    if chunk_dict.get("is_parent"):
                        all_parents.append(chunk_dict)
                        parents_count += 1
                    else:
                        all_children.append(chunk_dict)
                        children_count += 1
                logger.info("Документ обработан: source=%s, children=%d, parents=%d", doc.source, children_count, parents_count)
            except (DocumentConversionError, TextSplittingError) as exc:
                logger.error("Ошибка обработки документа: source=%s, ошибка=%s", doc.source, exc, exc_info=True)
                raise
            except Exception as exc:
                logger.error("Непредвиденная ошибка обработки документа: source=%s, ошибка=%s", doc.source, exc, exc_info=True)
                raise DocumentIngestionError(
                    collection_name=collection_name,
                    details=f"Сбой при подготовке документа '{doc.source}': {exc}",
                ) from exc

        if not all_children and not all_parents:
            logger.warning("После обработки документов чанки не сформированы: коллекция=%s", collection_name)
            return

        logger.info("Подготовка чанков завершена: коллекция=%s, children=%d, parents=%d", collection_name, len(all_children), len(all_parents))

        tasks = [
            self.repo.upsert(collection_name, all_children, is_vector=True),
            self.keyword_repo.index_documents(collection_name, all_children),
        ]

        if all_parents:
            parents_collection_name = f"{collection_name}_parents"
            tasks.append(self.repo.upsert(parents_collection_name, all_parents, is_vector=False))

        try:
            logger.info("Начато сохранение чанков: коллекция=%s, children=%d, parents=%d", collection_name, len(all_children), len(all_parents))
            await asyncio.gather(*tasks)
            logger.info("Индексация документов успешно завершена: коллекция=%s, children=%d, parents=%d", collection_name, len(all_children), len(all_parents))

        except BaseAppException:
            raise
        except Exception as exc:
            logger.error("Ошибка сохранения чанков: коллекция=%s, ошибка=%s", collection_name, exc, exc_info=True)
            raise DocumentIngestionError(
                collection_name=collection_name,
                details=f"Ошибка сохранения данных в хранилища: {exc}",
            ) from exc