import logging
from uuid import UUID
from typing import Optional, Dict, Any, List, Union, Tuple

from src.rag.retrievers import BaseRetriever
from src.rag.schemas.document import RAGDocument
from src.services.ai_service import AIService
from src.rag.repositories.context_enricher import ContextEnricher
from src.db.repositories import RepositoryContainer
from src.core.exceptions import BaseAppException
from src.core.exceptions.rag_service_exceptions import (
    ContextEnrichmentError,
    EmptyQueryError,
    NoRelevantDocumentsFoundError,
    RAGException,
)
from src.core.exceptions.repo_exceptions import CollectionNotFoundError
from src.core.prompts import RAG_USER_PROMPT, RAG_SYSTEM_PROMPT

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(
        self,
        ai_service: AIService,
        retriever: BaseRetriever,
        enricher: Optional[ContextEnricher] = None,
    ):
        self.ai_service = ai_service
        self.retriever = retriever
        self.enricher = enricher

    async def _full_step(
        self,
        query: str,
        collection_name: str,
        retrieve_limit: int = 50,
        merge_limit: int = 20,
        top_k: int = 5,
        only_context: bool = True,
        **kwargs,
    ) -> Tuple[Optional[str], List[RAGDocument]]:        
        try:
            docs = await self.retriever.retrieve(
                query,
                collection_name,
                retrieve_limit=retrieve_limit,
                merge_limit=merge_limit,
            )
        except BaseAppException:
            raise
        except Exception as exc:
            logger.error("Ошибка ретрива: collection=%s, ошибка=%s", collection_name, exc, exc_info=True)
            raise RAGException(
                message=f"Ошибка при поиске документов по коллекции '{collection_name}': {exc}"
            ) from exc

        logger.info("Ретрив завершён: collection=%s, документов=%d", collection_name, len(docs))

        if not docs:
            logger.warning("Ретривер не вернул документов: collection=%s", collection_name)
            raise NoRelevantDocumentsFoundError(query=query, collection_name=collection_name)

        if self.ai_service.reranker:
            try:
                docs = await self.ai_service.reranker.compress_documents(
                    query=query,
                    documents=docs,
                    top_k=top_k,
                )
                logger.info("Реранкинг завершён: документов=%d, top_k=%d", len(docs), top_k)
            except BaseAppException:
                raise
            except Exception as exc:
                logger.error("Ошибка реранкинга: ошибка=%s", exc, exc_info=True)
                if not docs:
                    raise RAGException(message=f"Сбой реранкинга: {exc}") from exc

        if not docs:
            logger.warning(f"После реранкинга не осталось подходящих документов для запроса: collection='%s'", collection_name)
            raise NoRelevantDocumentsFoundError(query=query, collection_name=collection_name)

        if self.enricher:
            try:
                docs = await self.enricher.enrich(docs, collection_name)
                logger.info("Обогащение контекста завершено: документов=%d", len(docs))
            except BaseAppException:
                raise
            except Exception as exc:
                logger.error("Ошибка обогащения контекста: ошибка=%s", exc, exc_info=True)
                raise ContextEnrichmentError(details=str(exc)) from exc

        final_docs = docs[:top_k]
        if only_context:
            logger.info("RAG завершён без LLM: документов=%d", len(final_docs))
            return None, final_docs

        if not self.ai_service.llm:
            logger.info("LLM отключен: возвращаем найденные документы (%d) без генерации", len(final_docs))
            return None, final_docs

        context_text = "\n\n---\n\n".join([doc.content for doc in final_docs])
        
        prompt = RAG_USER_PROMPT.format(
            query=query.strip(),
            context=context_text if context_text else 'Нет информации'
        )

        system_prompt = RAG_SYSTEM_PROMPT

        try:
            answer = await self.ai_service.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                **kwargs,
            )
            logger.info("Генерация ответа LLM завершена: документов в контексте=%d", len(final_docs))
        except BaseAppException:
            raise
        except Exception as exc:
            logger.error("Ошибка генерации ответа LLM: ошибка=%s", exc, exc_info=True)
            raise RAGException(message=f"Ошибка при генерации ответа LLM: {exc}") from exc

        return answer, final_docs

    async def run(
        self,
        query: str,
        collection_id: UUID,
        repos: RepositoryContainer,
        retrieve_limit: int = 30,
        merge_limit: int = 10,
        top_k: int = 5,
        temperature: float = 0.3,
        max_tokens: int = 1024,
        only_context: bool = True        
    ) -> Dict[str, Any]:
        logger.info("Запуск RAG: collection_id=%s, only_context=%s", collection_id, only_context)
        if not query or not query.strip():
            raise EmptyQueryError()

        collection = await repos.collection_repo.get_by_id(collection_id)

        if collection is None:
            raise CollectionNotFoundError(str(collection_id))

        logger.info("Начат RAG-пайплайн: collection=%s, retrieve_limit=%d, merge_limit=%d, top_k=%d", collection.id, retrieve_limit, merge_limit, top_k)
        answer, documents = await self._full_step(
            query=query.strip(),
            collection_name=str(collection.id),
            retrieve_limit=retrieve_limit,
            merge_limit=merge_limit,
            top_k=top_k,
            temperature=temperature,
            max_tokens=max_tokens,
            only_context=only_context,
        )
        logger.info("RAG-пайплайн завершён: collection_id=%s, документов=%d, LLM=%s", collection_id, len(documents), not only_context)
        return {
            "answer": answer,
            "documents": documents,
            "count": len(documents),
            "only_context": only_context
        }