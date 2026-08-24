from src.core.exceptions import BaseAppException


class TextSplittingError(BaseAppException):
    """Базовая ошибка при разбиении документа на чанки."""

    def __init__(self, message: str = "Ошибка при разбиении текста"):
        super().__init__(message=message, status_code=500)


class InvalidSplitterConfigError(TextSplittingError):
    """Некорректная конфигурация параметров сплиттера."""

    def __init__(self, details: str):
        super().__init__(message=f"Некорректная конфигурация сплиттера: {details}")


class EmptyTextToSplitError(TextSplittingError):
    """Передан пустой текст для нарезки."""

    def __init__(self, doc_id: str):
        super().__init__(message=f"Невозможно разбить пустой документ (doc_id: {doc_id})")