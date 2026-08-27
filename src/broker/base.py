import logging
import aio_pika

from src.core.config import settingsRabbitMQ

logger = logging.getLogger(__name__)


class BaseRabbitMQ:
    """Базовый класс для работы с RabbitMQ."""

    def __init__(self):
        self.url = settingsRabbitMQ.get_auth_data
        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.RobustChannel | None = None

    async def connect(self, prefetch_count: int = 10) -> None:
        try:
            logger.info("Подключаюсь к RabbitMQ...")
            self.connection = await aio_pika.connect_robust(self.url)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=prefetch_count)
            logger.info("Соединение с RabbitMQ успешно установлено")
        except aio_pika.exceptions.CONNECTION_EXCEPTIONS:
            logger.warning("Ошибка при подключении к RabbitMQ")
            raise
        except Exception as e:
            logger.error(f"Ошибка при установке соединения с RabbitMQ -> {e}")
            raise

    async def close(self) -> None:
        if self.connection and not self.connection.is_closed:
            logger.info("Закрываю соединение с RabbitMQ...")
            await self.connection.close()
            logger.info("Соединение с RabbitMQ закрыто")

    async def setup_topology(
        self,
        exchange_name: str = settingsRabbitMQ.documents_exchange,
        queue_name: str = settingsRabbitMQ.documents_queue,
        routing_key: str = settingsRabbitMQ.documents_routing_key,
    ) -> None:
        if not self.channel or self.channel.is_closed:
            raise RuntimeError("Канал RabbitMQ не инициализирован. Вызовите connect() перед настройкой топологии.")

        try:
            logger.info("Настройка топологии: exchange=%s, queue=%s, routing_key=%s", exchange_name, queue_name, routing_key)
            exchange = await self.channel.declare_exchange(
                exchange_name,
                aio_pika.ExchangeType.DIRECT,
                durable=True,
            )
            queue = await self.channel.declare_queue(name=queue_name, durable=True)
            await queue.bind(exchange=exchange, routing_key=routing_key)
        except Exception as e:
            logger.error("Ошибка при настройке топологии RabbitMQ: %s", e)
            raise

    async def ping(self) -> bool:
        try:
            if self.channel.is_closed:
                return False
            await self.channel.queue_declare(queue='', passive=True)
            return True
        except Exception:
            return False