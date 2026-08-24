from typing import Any, Dict, Optional


class BaseAppException(Exception):
    """
    Базовый класс для всех предсказуемых ошибок приложения.
    """
    def __init__(
        self, 
        message: str, 
        status_code: int = 400, 
        extra: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.extra = extra or {}
        super().__init__(message)

