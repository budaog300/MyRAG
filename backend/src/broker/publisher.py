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
            exchange = await self.channel.declare_exchange(
                exchange_name, aio_pika.ExchangeType.DIRECT, durable=True
            )
            
            message = aio_pika.Message(
                message_id=str(uuid4()),
                body=obj.model_dump_json().encode(),
                content_type="application/json",
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            )
            
            await exchange.publish(message, routing_key=routing_key, mandatory=True)
            logger.info(f"Данные {obj.__class__.__name__} успешно опубликованы по ключу: {routing_key}")

        except aio_pika.exceptions.AMQPException as e:
            logger.error(f"Ошибка AMQP при публикации в exchange '{exchange_name}': {e}")
            raise
        except Exception as e:
            logger.error(f"Ошибка при публикации в exchange '{exchange_name}': {e}")
            raise