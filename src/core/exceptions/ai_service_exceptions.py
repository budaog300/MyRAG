from src.core.exceptions import BaseAppException


class AIServiceInitializationError(BaseAppException):
    """Ошибка при инициализации сервиса AI-компонентов."""

    def __init__(self, service_name: str, details: str):
        super().__init__(
            message=f"Не удалось инициализировать компонент '{service_name}': {details}",
            status_code=500,
        )


class UnsupportedEngineModeError(AIServiceInitializationError):
    """Передан неверный режим работы (EngineMode) для провайдера."""

    def __init__(self, service_name: str, mode: str):
        super().__init__(
            service_name=service_name,
            details=f"Неподдерживаемый режим работы engine mode: '{mode}'",
        )