import logging
from typing import AsyncGenerator
import aioboto3
import asyncio
from botocore.exceptions import ClientError
from src.core.config import settingsS3
from src.core.exceptions import BaseAppException

logger = logging.getLogger(__name__)


class S3ServiceError(BaseAppException):
    """Ошибка работы с S3 хранилищем."""
    def __init__(self, message: str = "Ошибка хранилища S3", status_code: int = 500):
        super().__init__(message=message, status_code=status_code)        


class S3Service:
    def __init__(self):
        self.session = aioboto3.Session()
        self.endpoint_url = settingsS3.ENDPOINT_URL
        self.access_key = settingsS3.ACCESS_KEY
        self.secret_key = settingsS3.SECRET_KEY
        self.bucket_name = settingsS3.BUCKET_NAME
        self._delete_semaphore = asyncio.Semaphore(20)

    def _get_client(self):
        return self.session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=settingsS3.REGION,
        )

    async def ensure_bucket_exists(self) -> None:
        """Создает бакет, если он не существует."""
        async with self._get_client() as s3:
            try:
                await s3.head_bucket(Bucket=self.bucket_name)
            except ClientError:
                logger.info("Бакет '%s' не найден. Создаем...", self.bucket_name)
                await s3.create_bucket(Bucket=self.bucket_name)

    async def upload_file(self, file_data: bytes, object_key: str, content_type: str = "application/octet-stream") -> str:
        """Загружает файл в S3 и возвращает S3-ключ (object_key)."""
        async with self._get_client() as s3:
            try:
                await s3.put_object(
                    Bucket=self.bucket_name,
                    Key=object_key,
                    Body=file_data,
                    ContentType=content_type,
                )
                logger.info("Файл %s успешно загружен в S3 бакет %s", object_key, self.bucket_name)
                return object_key
            except Exception as e:
                logger.error("Ошибка загрузки файла %s в S3: %s", object_key, e, exc_info=True)
                raise S3ServiceError(f"Не удалось сохранить файл в хранилище: {e}")

    async def download_file(self, object_key: str) -> bytes:
        """Скачивает файл из S3 в виде байтов."""
        async with self._get_client() as s3:
            try:
                response = await s3.get_object(Bucket=self.bucket_name, Key=object_key)
                async with response["Body"] as stream:
                    return await stream.read()
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchKey":
                    raise S3ServiceError(f"Файл '{object_key}' не найден в хранилище", status_code=404)
                raise S3ServiceError(f"Ошибка при скачивании файла из S3: {e}")
            except Exception as e:
                logger.error("Ошибка скачивания файла %s из S3: %s", object_key, e, exc_info=True)
                raise S3ServiceError(f"Не удалось прочитать файл из хранилища: {e}")

    async def _delete_file(self, object_key: str) -> None:
        """Удаляет файл из S3."""
        async with self._get_client() as s3:
            try:
                await s3.delete_object(Bucket=self.bucket_name, Key=object_key)
                logger.info("Файл %s успешно удален из S3", object_key)
            except Exception as e:
                logger.error("Ошибка удаления файла %s из S3: %s", object_key, e, exc_info=True)
                raise S3ServiceError(f"Не удалось удалить файл из хранилища: {e}")

    async def delete_file(self, object_key: str) -> None:
        async with self._delete_semaphore:
            await self._delete_file(object_key)

    async def ping(self) -> bool:
        try:
            async with self._get_client() as s3:
                await s3.head_bucket(Bucket=self.bucket_name)
                return True
        except Exception as e:
            logger.error("S3 ping failed: %s", e)
            return False