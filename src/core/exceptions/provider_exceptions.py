from src.core.exceptions import BaseAppException


class AIProviderError(BaseAppException):
    """Базовое исключение для всех AI провайдеров"""
    def __init__(self, message: str = "Ошибка при обращении к AI-сервису", status_code: int = 502):
        super().__init__(message=message, status_code=status_code)


class AIProviderAuthError(AIProviderError):
    """Неверный API ключ или проблема с доступом"""
    def __init__(self, details: str = ""):
        super().__init__(message=f"Ошибка авторизации AI-провайдера: {details}", status_code=401)


class AIProviderNotConfiguredError(AIProviderError):
    """Запрос к компоненту AI, который не был сконфигурирован/включен."""

    def __init__(self, service_name: str):
        super().__init__(
            message=f"Сервис AI '{service_name}' не сконфигурирован или отключен.",
            status_code=503,
        )


class AIProviderRateLimitError(AIProviderError):
    """Превышен лимит запросов (Rate Limit / Quota Exceeded)"""
    def __init__(self, details: str = ""):
        super().__init__(message=f"Превышен лимит запросов к AI-сервису: {details}", status_code=429)


class AIProviderTimeoutError(AIProviderError):
    """Таймаут ожидания ответа от сервера"""
    def __init__(self, details: str = ""):
        super().__init__(message=f"Таймаут ответа от AI-сервиса: {details}", status_code=504)


class AIProviderResponseParseError(AIProviderError):
    """Ошибка разбора ответа (например, изменилась структура JSON)"""
    def __init__(self, details: str = ""):
        super().__init__(message=f"Некорректный формат ответа AI-провайдера: {details}", status_code=502)


class EmbedderError(AIProviderError):
    """Специфичная ошибка при создании эмбеддингов"""
    pass


class LLMError(AIProviderError):
    """Специфичная ошибка генерации текста"""
    pass


class RerankerError(AIProviderError):
    """Специфичная ошибка реранкинга"""
    pass


class VLMError(AIProviderError):
    """Специфичная ошибка мультимодальной модели"""
    pass