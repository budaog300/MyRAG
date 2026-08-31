from src.core.exceptions import BaseAppException


class CollectionNotFoundError(BaseAppException):
    def __init__(self, collection_name: str):
        super().__init__(
            message=f"Коллекция или индекс '{collection_name}' не найдены.",
            status_code=404
        )


class CollectionAlreadyExistsError(BaseAppException):
    def __init__(self, collection_name: str):
        super().__init__(
            message=f"Коллекция или индекс '{collection_name}' уже существуют.",
            status_code=409
        )


class InvalidCollectionNameError(BaseAppException):
    """Некорректное имя коллекции."""

    def __init__(self, collection_name: str):
        super().__init__(
            message=f"Имя коллекции '{collection_name}' не должно быть пустым и должно содержать только допустимые символы.",
            status_code=400,
        )


class CollectionOperationError(BaseAppException):
    """Ошибка выполнения операции над коллекциями (создание, очистка, удаление)."""

    def __init__(self, operation: str, collection_name: str, details: str):
        super().__init__(
            message=f"Не удалось выполнить операцию '{operation}' для коллекции '{collection_name}': {details}",
            status_code=500,
        )


class DocumentNotFoundError(BaseAppException):
    def __init__(self, file_id: str, collection_name: str):
        super().__init__(
            message=f"Документ '{file_id}' не найден в коллекции '{collection_name}'.",
            status_code=404
        )


class VectorDatabaseError(BaseAppException):
    def __init__(self, detail: str):
        super().__init__(
            message=f"Ошибка при работе с векторной БД: {detail}",
            status_code=500
        )


class KeywordDatabaseError(BaseAppException):
    def __init__(self, detail: str):
        super().__init__(
            message=f"Ошибка при работе с Keyword БД: {detail}",
            status_code=500
        )


class EmbedderError(BaseAppException):
    def __init__(self, detail: str):
        super().__init__(
            message=f"Ошибка генерации эмбеддингов: {detail}",
            status_code=502
        )


class ParentDocumentNotFoundError(BaseAppException):
    """Родительский документ не найден в коллекции родителей"""
    def __init__(self, parent_id: str, collection_name: str):
        super().__init__(
            message=f"Родительский документ с ID '{parent_id}' не найден в коллекции '{collection_name}_parents'",
            status_code=404
        )
