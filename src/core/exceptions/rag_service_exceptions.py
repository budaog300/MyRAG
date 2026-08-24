from src.core.exceptions import BaseAppException


class RAGException(BaseAppException):
    """Базовое исключение для ошибок в RAG пайплайне."""

    def __init__(self, message: str, status_code: int = 500):
        super().__init__(message=message, status_code=status_code)


class EmptyQueryError(RAGException):
    """Передан пустой поисковый запрос."""

    def __init__(self):
        super().__init__(message="Поисковый запрос не может быть пустым.", status_code=400)


class NoRelevantDocumentsFoundError(RAGException):
    """Не найдено релевантных документов для ответа на вопрос."""

    def __init__(self, query: str, collection_name: str):
        super().__init__(
            message=f"Не найдены релевантные документы по запросу '{query}' в коллекции '{collection_name}'.",
            status_code=404,
        )


class ContextEnrichmentError(RAGException):
    """Ошибка при обогащении найденных документов (ContextEnricher)."""

    def __init__(self, details: str):
        super().__init__(
            message=f"Ошибка при обогащении контекста документов: {details}",
            status_code=500,
        )