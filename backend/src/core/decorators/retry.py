import asyncio
import logging
import random
from functools import wraps
from typing import Callable

logger = logging.getLogger(__name__)


def retry(attempts: int = 3, delay: float = 1, backoff: float = 1.5, max_delay: float = 30, jitter: float = 0.2, retry_exceptions: tuple[type[Exception], ...] = (Exception,)):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_delay = delay
            for attempt in range(1, attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except retry_exceptions as exc:
                    if attempt == attempts:
                        raise
                    sleep_time = min(current_delay, max_delay) + random.uniform(0, jitter)
                    logger.warning("Ошибка выполнения %s, повторная попытка %d/%d через %.2f сек.: %s", func.__name__, attempt, attempts - 1, sleep_time, exc)
                    await asyncio.sleep(sleep_time)
                    current_delay *= backoff
        return wrapper
    return decorator