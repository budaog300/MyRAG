from src.core.exceptions import BaseAppException


class RetrieverError(BaseAppException):
    """Базовое исключение для всех ретриверов"""
    def __init__(self, message: str = "Ошибка при поиске документов", status_code: int = 500):
        super().__init__(message=message, status_code=status_code)


class HybridRetrieverError(RetrieverError):
    """Сбой при проведении гибридного поиска (падение всех источников)"""
    def __init__(self, details: str = ""):
        super().__init__(message=f"Ошибка гибридного поиска: {details}", status_code=500)


class EmptySearchResultError(RetrieverError):
    """Исключение, если поиск вернул пустой результат (опционально, для строгой логики)"""
    def __init__(self, query: str):
        super().__init__(message=f"По запросу '{query}' ничего не найдено", status_code=404)