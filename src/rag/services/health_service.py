import asyncio
import logging
from typing import Any, Dict
from src.broker.publisher import RabbitMQPublisher
from src.rag.repositories import BaseKeywordRepository, BaseVectorRepository
from src.rag.services.s3_service import S3Service

logger = logging.getLogger(__name__)


class HealthCheckService:
    def __init__(
        self,
        repo: BaseVectorRepository,
        keyword_repo: BaseKeywordRepository,
        broker: RabbitMQPublisher,
        s3_service: S3Service,

    ):
        self.repo = repo
        self.keyword_repo = keyword_repo
        self.broker = broker
        self.s3_service = s3_service

    async def check_repo(self) -> bool:
        """Векторная БД."""
        try:
            await self.repo.ping()
            return True
        except Exception as e:
            logger.error("Healthcheck failed for Vector repository: %s", e)
            return False

    async def check_keyword_repo(self) -> bool:
        """Кейворд БД."""
        try:
            return await self.keyword_repo.ping()
        except Exception as e:
            logger.error("Healthcheck failed for Elasticsearch: %s", e)
            return False
    
    async def check_broker(self) -> bool:
        """Брокер сообщений"""
        try:
            await self.broker.ping()
            return True
        except Exception as e:
            logger.error("Healthcheck failed for RabbitMQ: %s", e)
            return False

    async def check_s3(self) -> bool:
        """S3 Хранилище."""
        try:
            await self.s3_service.ping()
            return True
        except Exception as e:
            logger.error("Healthcheck failed for S3 storage: %s", e)
            return False
    
    async def check_postgres(self) -> bool:
        """Заглушка для Реляционной БД."""
        # TODO: Заменить на реальный `SELECT 1` при подключении БД
        try:
            return True
        except Exception as e:
            logger.error("Healthcheck failed for Postgres storage: %s", e)
            return False

    async def check_redis(self) -> bool:
        """Заглушка для Redis."""
        # TODO: Заменить на реальный `redis.ping()` при подключении Redis
        try:
            return True
        except Exception as e:
            logger.error("Healthcheck failed for Redis: %s", e)
            return False

    async def run_all_checks(self) -> Dict[str, Any]:
        checks = {
            "vector_db": self.check_repo(),
            "keyword_db": self.check_keyword_repo(),
            "broker": self.check_broker(),
            "s3_storage": self.check_s3(),            
            "database": self.check_postgres(),
            "redis": self.check_redis(),
        }

        results = await asyncio.gather(
            *checks.values(),
            return_exceptions=True,
        )

        services_status = {
            name: result is True
            for name, result in zip(checks, results)
        }

        is_healthy = all(services_status.values())

        return {
            "status": "healthy" if is_healthy else "unhealthy",
            "services": services_status,
        }