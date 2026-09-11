import logging
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
        self.endpoint_url = settingsS3.S3_ENDPOINT_URL
        self.access_key = settingsS3.S3_ACCESS_KEY
        self.secret_key = settingsS3.S3_SECRET_KEY
        self.bucket_name = settingsS3.S3_BUCKET_NAME
        self._delete_semaphore = asyncio.Semaphore(20)

    def _get_client(self):
        return self.session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=settingsS3.S3_REGION,
        )

    async def ensure_bucket_exists(self) -> None:
        """Создает бакет, если он не существует."""
        async with self._get_client() as s3:
            try:
                await s3.head_bucket(Bucket=self.bucket_name)
                logger.info("S3 бакет найден: bucket=%s", self.bucket_name)
            except ClientError as exc:
                logger.info("S3 бакет не найден, создание: bucket=%s", self.bucket_name)
                try:
                    await s3.create_bucket(Bucket=self.bucket_name)
                    logger.info("S3 бакет успешно создан: bucket=%s", self.bucket_name)
                except Exception as exc:
                    logger.error("Ошибка создания S3 бакета: bucket=%s, ошибка=%s", self.bucket_name, exc, exc_info=True)
                    raise S3ServiceError(f"Не удалось создать бакет: {exc}") from exc

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
                logger.info("Файл успешно загружен в S3: bucket=%s, key=%s", self.bucket_name, object_key)
                return object_key
            except Exception as e:
                logger.error("Ошибка загрузки файла в S3: bucket=%s, key=%s, ошибка=%s", self.bucket_name, object_key, e, exc_info=True)
                raise S3ServiceError(f"Не удалось сохранить файл в хранилище: {e}")

    async def download_file(self, object_key: str) -> bytes:
        """Скачивает файл из S3 в виде байтов."""
        async with self._get_client() as s3:
            try:
                response = await s3.get_object(Bucket=self.bucket_name, Key=object_key)
                async with response["Body"] as stream:
                    logger.info("Файл успешно скачан из S3: bucket=%s, key=%s", self.bucket_name, object_key)
                    return await stream.read()
            except ClientError as e:
                if e.response["Error"]["Code"] == "NoSuchKey":
                    logger.warning("Файл не найден в S3: bucket=%s, key=%s", self.bucket_name, object_key)
                    raise S3ServiceError(f"Файл '{object_key}' не найден в хранилище", status_code=404)
                raise S3ServiceError(f"Ошибка при скачивании файла из S3: {e}")
            except Exception as e:
                logger.error("Ошибка скачивания файла из S3: bucket=%s, key=%s, ошибка=%s", self.bucket_name, object_key, e, exc_info=True)
                raise S3ServiceError(f"Не удалось прочитать файл из хранилища: {e}")

    async def _delete_file(self, object_key: str) -> None:
        """Удаляет файл из S3."""
        
        async with self._get_client() as s3:
            try:
                await s3.delete_object(Bucket=self.bucket_name, Key=object_key)
                logger.info("Файл успешно удалён из S3: bucket=%s, key=%s", self.bucket_name, object_key)
            except Exception as e:
                logger.error("Ошибка удаления файла из S3: bucket=%s, key=%s, ошибка=%s", self.bucket_name, object_key, e, exc_info=True)
                raise S3ServiceError(f"Не удалось удалить файл из хранилища: {e}")

    async def delete_file(self, object_key: str) -> None:
        async with self._delete_semaphore:
            await self._delete_file(object_key)

    async def ping(self) -> bool:
        try:
            async with self._get_client() as s3:
                await s3.head_bucket(Bucket=self.bucket_name)
                logger.info("S3 доступен: bucket=%s", self.bucket_name)
                return True
        except Exception as e:
            logger.error("Проверка подключения к S3 завершилась ошибкой: bucket=%s, ошибка=%s", self.bucket_name, e)
            return False