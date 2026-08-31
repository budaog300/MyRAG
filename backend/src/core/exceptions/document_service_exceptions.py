from src.core.exceptions import BaseAppException


class DocumentIngestionError(BaseAppException):
    """Базовая ошибка процесса индексации/загрузки документов."""

    def __init__(self, collection_name: str, details: str):
        super().__init__(
            message=f"Ошибка индексации документов в коллекцию '{collection_name}': {details}",
            status_code=500,
        )


class EmptyDocumentListError(DocumentIngestionError):
    """Передан пустой список документов для индексации."""

    def __init__(self, collection_name: str):
        super().__init__(
            collection_name=collection_name,
            details="Список документов для загрузки пуст.",
        )