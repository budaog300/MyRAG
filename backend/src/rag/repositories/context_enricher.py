import logging
from typing import List
from src.rag.repositories import BaseVectorRepository
from src.rag.schemas.document import RAGDocument
from src.core.exceptions.repo_exceptions import (
    CollectionNotFoundError,
    ParentDocumentNotFoundError,
    VectorDatabaseError,
)

logger = logging.getLogger(__name__)


class ContextEnricher:
    def __init__(self, repo: BaseVectorRepository):
        self.repo = repo

    async def enrich(self, docs: List[RAGDocument], collection_name: str) -> List[RAGDocument]:
        if not docs:
            logger.warning("Обогащение контекста пропущено: список документов пуст, коллекция=%s", collection_name)
            return []

        parent_ids = list({
            doc.metadata["parent_id"] 
            for doc in docs 
            if doc.metadata.get("parent_id")
        })

        logger.debug("Собраны ID родительских документов: коллекция=%s, родителей=%d", collection_name, len(parent_ids))

        if not parent_ids:
            logger.info("Обогащение контекста пропущено: родительские документы не найдены, коллекция=%s", collection_name)
            return docs

        parents_collection_name = f"{collection_name}_parents"

        try:
            parents = await self.repo.get_documents_by_ids(
                collection_name=parents_collection_name,
                ids=parent_ids,
            )
        except CollectionNotFoundError:
            logger.error("Коллекция родительских документов не найдена: коллекция=%s", parents_collection_name)
            raise
        except VectorDatabaseError as exc:
            logger.error("Ошибка загрузки родительских документов: коллекция=%s, ошибка=%s", parents_collection_name, exc)
            raise

        parents_map = {p.id: p for p in parents}

        enriched_docs = []
        seen_parent_ids = set()

        for doc in docs:
            p_id = doc.metadata.get("parent_id")

            if not p_id:
                enriched_docs.append(doc)
                continue

            if p_id in seen_parent_ids:
                logger.debug("Пропущен дубликат родительского документа: parent_id=%s", p_id)
                continue

            parent_doc = parents_map.get(p_id)

            if not parent_doc:
                logger.error("Родительский документ не найден: parent_id=%s, коллекция=%s", p_id, collection_name)
                raise ParentDocumentNotFoundError(
                    parent_id=p_id,
                    collection_name=collection_name
                )

            doc.content = parent_doc.content
            doc.metadata = {
                **parent_doc.metadata,
                **doc.metadata,
            }
            doc.is_parent = getattr(parent_doc, "is_parent", True)

            seen_parent_ids.add(p_id)
            enriched_docs.append(doc)

        logger.info("Обогащение контекста завершено: коллекция=%s, входных=%d, выходных=%d, использовано родителей=%d", collection_name, len(docs), len(enriched_docs), len(seen_parent_ids))

        return enriched_docs