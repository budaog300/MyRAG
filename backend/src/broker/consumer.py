import logging
from typing import Awaitable, Callable, Type, TypeVar
import aio_pika
from pydantic import BaseModel, ValidationError
from src.broker.base import BaseRabbitMQ
from src.core.exceptions import BaseAppException
from src.core.config import settingsRabbitMQ

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class RabbitMQConsumer(BaseRabbitMQ):
    """Слушатель (Consumer) сообщений из RabbitMQ."""

    async def consume(
        self,
        obj: Type[T],
        func: Callable[[T], Awaitable[None]],
        queue_name: str = settingsRabbitMQ.DOCUMENTS_QUEUE,
    ) -> None:
        if not self.channel or self.channel.is_closed:
            raise RuntimeError("Канал RabbitMQ не инициализирован.")

        try:
            queue = await self.channel.declare_queue(queue_name, durable=True)
            logger.info("Consumer запущен: queue=%s, model=%s", queue_name, obj.__name__)

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    logger.info("Получено сообщение из RabbitMQ: message_id=%s, queue=%s", message.message_id, queue_name)

                    try:
                        in_obj = obj.model_validate_json(message.body.decode())
                    except (ValidationError, Exception) as exc:
                        logger.error("Ошибка валидации сообщения RabbitMQ: message_id=%s, queue=%s, ошибка=%s", message.message_id, queue_name, exc, exc_info=True)
                        await message.nack(requeue=False)
                        continue

                    try:
                        await func(in_obj)
                        await message.ack()
                        logger.info("Сообщение успешно обработано: message_id=%s, queue=%s", message.message_id, queue_name)

                    except BaseAppException as exc:
                        logger.error("Доменная ошибка при обработке сообщения: message_id=%s, queue=%s, ошибка=%s", message.message_id, queue_name, exc, exc_info=True)
                        await message.nack(requeue=False)
                    except Exception as exc:
                        logger.error( "Системная ошибка при обработке сообщения: message_id=%s, queue=%s, ошибка=%s", message.message_id, queue_name, exc, exc_info=True)
                        await message.nack(requeue=True)

        except aio_pika.exceptions.CONNECTION_EXCEPTIONS:
            logger.error("Потеряно соединение с RabbitMQ: queue=%s", queue_name, exc_info=True)
            raise
        except Exception as exc:
            logger.error("Критическая ошибка Consumer RabbitMQ: queue=%s, ошибка=%s", queue_name, exc, exc_info=True)
            raise