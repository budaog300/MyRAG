import logging
from typing import Optional, Dict, Any, List, Union

from src.rag.retrievers import BaseRetriever
from src.services.ai_service import AIService
from src.rag.repositories.context_enricher import ContextEnricher
from src.core.exceptions import BaseAppException
from src.core.exceptions.rag_service_exceptions import (
    ContextEnrichmentError,
    EmptyQueryError,
    NoRelevantDocumentsFoundError,
    RAGException,
)
from src.core.exceptions.ai_service_exceptions import AIServiceInitializationError
from src.core.exceptions.repo_exceptions import InvalidCollectionNameError

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
        system_prompt: Optional[str] = None,
        only_context: bool = True,
        **kwargs,
    ) -> Union[str | List[Any]]:
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
            logger.error(f"Ошибка при выполнении ретрива для коллекции '{collection_name}': {exc}", exc_info=True)
            raise RAGException(
                message=f"Ошибка при поиске документов по коллекции '{collection_name}': {exc}"
            ) from exc

        logger.info(f"Получено документов после ретрива: {len(docs)}")

        if not docs:
            logger.warning(f"Ретривер не вернул документов по запросу: '{query}'")
            raise NoRelevantDocumentsFoundError(query=query, collection_name=collection_name)

        if self.ai_service.reranker:
            try:
                docs = await self.ai_service.reranker.compress_documents(
                    query=query,
                    documents=docs,
                    top_K=top_k,
                )
                logger.info(f"Получено документов после реранкинга: {len(docs)}")
            except BaseAppException:
                raise
            except Exception as exc:
                logger.error(f"Ошибка при реранкинге документов: {exc}", exc_info=True)
                if not docs:
                    raise RAGException(message=f"Сбой реранкинга: {exc}") from exc

        if not docs:
            logger.warning(f"После реранкинга не осталось подходящих документов для запроса: '{query}'")
            raise NoRelevantDocumentsFoundError(query=query, collection_name=collection_name)

        if self.enricher:
            try:
                docs = await self.enricher.enrich(docs, collection_name)
                logger.info(f"Получено документов после обогащения контекста: {len(docs)}")
            except BaseAppException:
                raise
            except Exception as exc:
                logger.error(f"Ошибка при обогащении контекста: {exc}", exc_info=True)
                raise ContextEnrichmentError(details=str(exc)) from exc

        final_docs = docs[:top_k]
        if only_context:
            logger.info(f"Возврат найденных чанков без вызова LLM (only_context={only_context})")
            return final_docs

        context_text = "\n\n---\n\n".join([doc.content for doc in docs[:top_k]])

        prompt = (
            f"Используй следующий контекст для ответа на вопрос.\n\n"
            f"КОНТЕКСТ:\n{context_text if context_text else 'Нет информации'}\n\n"
            f"ВОПРОС: {query}"
        )

        system_prompt = system_prompt or self.ai_service.config.llm.prompt

        try:
            answer = await self.ai_service.llm.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                **kwargs,
            )
        except BaseAppException:
            raise
        except Exception as exc:
            logger.error(f"Ошибка генерации ответа через LLM: {exc}", exc_info=True)
            raise RAGException(message=f"Ошибка при генерации ответа LLM: {exc}") from exc

        return answer

    async def run(
        self,
        query: str,
        collection_name: str,
        retrieve_limit: int = 30,
        merge_limit: int = 10,
        top_k: int = 5,
        temperature: float = 0.3,
        max_tokens: int = 1024,
        only_context: bool = True,
    ) -> Dict[str, Any]:
        if not query or not query.strip():
            raise EmptyQueryError()

        if not collection_name or not collection_name.strip():
            raise InvalidCollectionNameError(collection_name=collection_name)

        logger.info(f"Запуск RAG пайплайна для коллекции '{collection_name}'")

        result = await self._full_step(
            query=query.strip(),
            collection_name=collection_name.strip(),
            retrieve_limit=retrieve_limit,
            merge_limit=merge_limit,
            top_K=top_k,
            temperature=temperature,
            max_tokens=max_tokens,
            only_context=only_context,
        )

        return {
            "answer": result if not only_context else None,
            "documents": result if only_context else [],
            "count": len(result) if only_context else 0,
            "only_context": only_context
        }