import logging
import aio_pika
from uuid import uuid4
from pydantic import BaseModel
from src.broker.base import BaseRabbitMQ
from src.core.config import settingsRabbitMQ

logger = logging.getLogger(__name__)


class RabbitMQPublisher(BaseRabbitMQ):
    """Издатель сообщений в RabbitMQ."""

    async def publish(
        self,
        obj: BaseModel,
        exchange_name: str = settingsRabbitMQ.documents_exchange,
        routing_key: str = settingsRabbitMQ.documents_routing_key,
    ) -> None:
        if not self.channel or self.channel.is_closed:
            raise RuntimeError("Канал RabbitMQ не инициализирован. Вызовите connect() перед публикацией.")

        try:
            message_id = str(uuid4())
            logger.info("Публикация сообщения в RabbitMQ: exchange=%s, routing_key=%s, message_id=%s, type=%s", exchange_name, routing_key, message_id, obj.__class__.__name__)
            exchange = await self.channel.declare_exchange(
                exchange_name, aio_pika.ExchangeType.DIRECT, durable=True
            )
            
            message = aio_pika.Message(
                message_id=message_id,
                body=obj.model_dump_json().encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )
            
            await exchange.publish(message, routing_key=routing_key, mandatory=True)
            logger.info("Сообщение успешно опубликовано: exchange=%s, routing_key=%s, message_id=%s", exchange_name, routing_key, message_id)
        except aio_pika.exceptions.AMQPException as exc:
            logger.error("AMQP ошибка при публикации сообщения: exchange=%s, routing_key=%s, message_id=%s, ошибка=%s", exchange_name, routing_key, message_id, exc, exc_info=True)
            raise
        except Exception as exc:
            logger.error("Ошибка публикации сообщения в RabbitMQ: exchange=%s, routing_key=%s, message_id=%s, ошибка=%s", exchange_name, routing_key, message_id, exc, exc_info=True)
            raise