import logging
from typing import Awaitable, Callable, Type, TypeVar
import aio_pika
from pydantic import BaseModel, ValidationError
from src.broker.base import BaseRabbitMQ
from src.core.exceptions import BaseAppException

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class RabbitMQConsumer(BaseRabbitMQ):
    """Слушатель (Consumer) сообщений из RabbitMQ."""

    async def consume(
        self,
        queue_name: str,
        obj: Type[T],
        func: Callable[[T], Awaitable[None]],
    ) -> None:
        if not self.channel or self.channel.is_closed:
            raise RuntimeError("Канал RabbitMQ не инициализирован.")

        try:
            queue = await self.channel.declare_queue(queue_name, durable=True)
            logger.info(f"Запускаю чтение из очереди: {queue_name}")

            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    logger.info(f"Прочитано сообщение [{message.id}] из очереди {queue_name}")

                    try:
                        in_obj = obj.model_validate_json(message.body.decode())
                    except (ValidationError, Exception) as e:
                        logger.error(f"Ошибка валидации/декодирования сообщения {message.id}: {e}")
                        await message.nack(requeue=False)
                        continue

                    try:
                        await func(in_obj)
                        await message.ack()
                    except BaseAppException as e:
                        logger.error(f"Доменная ошибка при обработке сообщения {message.id}: {e}")
                        await message.nack(requeue=False)
                    except Exception as e:
                        logger.error(f"Системная ошибка при обработке сообщения {message.id}: {e}")
                        await message.nack(requeue=True)

        except aio_pika.exceptions.CONNECTION_EXCEPTIONS:
            logger.warning(f"Потеряно соединение с RabbitMQ при чтении из очереди {queue_name}")
            raise
        except Exception as e:
            logger.error(f"Критическая ошибка в consumer для очереди {queue_name}: {e}")
            raise