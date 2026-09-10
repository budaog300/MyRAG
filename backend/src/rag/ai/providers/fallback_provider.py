import logging
from src.core.exceptions.provider_exceptions import AIProviderUnavailableError


logger = logging.getLogger(__name__)


class FallbackProvider:
    def __init__(self, primary, fallback):
        self.primary = primary
        self.fallback = fallback
        self.config = primary.config

    def __getattr__(self, name):
        primary_method = getattr(self.primary, name)

        if not callable(primary_method):
            return primary_method

        async def wrapper(*args, **kwargs):
            try:
                return await primary_method(*args, **kwargs)
            except AIProviderUnavailableError:
                if self.fallback is None:
                    raise

                logger.warning("Основной AI-провайдер недоступен, переключаемся на fallback: %s", name)

                fallback_method = getattr(self.fallback, name)
                return await fallback_method(*args, **kwargs)

        return wrapper