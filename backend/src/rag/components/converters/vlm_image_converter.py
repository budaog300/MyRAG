import time
import logging
import base64
import asyncio
from pathlib import Path
from typing import Set
import httpx

from src.rag.components.converters.base import BaseDocumentConverter
from src.services import AIService
from src.core.exceptions.provider_exceptions import (
    AIProviderResponseParseError,    
    VLMError
)
from src.core.exceptions.converter_exceptions import (
    DocumentConversionError,
    DocumentFileNotFoundError,
    UnsupportedFileFormatError
)
from src.rag.prompts import PICTURE_DESCRIPTION_PROMPT

logger = logging.getLogger(__name__)


class VLMImageConverter(BaseDocumentConverter):
    """
    Конвертер изображений (.png, .jpg, .jpeg, .webp), использующий
    прямой вызов Vision LLM (OpenAI / Ollama / Qwen-VL) для распознавания
    и структурирования текста в один проход.
    """

    SUPPORTED_EXTENSIONS: Set[str] = {".png", ".jpg", ".jpeg", ".webp"}

    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service

    def _encode_image(self, file_path: Path) -> str:
        """Кодирует локальный файл картинки в base64."""
        with open(file_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    async def convert(self, file_path: Path) -> str:
        if not file_path.exists():
            raise DocumentFileNotFoundError(file_path=str(file_path))

        if not self.supports(file_path):
            raise UnsupportedFileFormatError(extension=file_path.suffix)

        if self.ai_service.vlm is None:
            logger.warning(f"VLM отключен (enabled=False). Пропуск обработки изображения: {file_path.name}")
            return f"<!-- Обработка изображения {file_path.name} пропущена (VLM отключен) -->"

        vlm_config = self.ai_service.config.vlm
        start_time = time.perf_counter()

        try:
            base64_image = await asyncio.to_thread(self._encode_image, file_path)
        except Exception as exc:
            logger.error(f"Ошибка при чтении/кодировании изображения '{file_path.name}': {exc}")
            raise DocumentConversionError(
                message=f"Не удалось прочитать файл изображения '{file_path.name}': {exc}"
            ) from exc

        ext = file_path.suffix.lower().replace(".", "")
        mime_type = "image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext}"

        payload = {
            "model": vlm_config.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PICTURE_DESCRIPTION_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            "max_tokens": vlm_config.max_tokens,
            **vlm_config.extra_params,
        }

        headers = {"Content-Type": "application/json"}
        if vlm_config.api_key:
            headers["Authorization"] = f"Bearer {vlm_config.api_key}"

        try:
            async with httpx.AsyncClient(timeout=vlm_config.timeout) as client:
                response = await client.post(
                    vlm_config.api_url,
                    json=payload,
                    headers=headers,
                )
                response.raise_for_status()
                data = response.json()

        except httpx.TimeoutException as exc:
            logger.error(f"Таймаут VLM API ({vlm_config.timeout} {exc}): %s")
            raise VLMError(
                message=f"Превышено время ожидания ответа от VLM API ({vlm_config.timeout}s)"
            ) from exc

        except httpx.HTTPStatusError as exc:
            logger.error(
                "VLM API returned HTTP %s: %s",
                exc.response.status_code,
                exc.response.text,
            )
            raise VLMError(
                message=f"VLM провайдер вернул ошибку {exc.response.status_code}: {exc.response.text}"
            ) from exc

        except httpx.RequestError as exc:
            logger.error(f"Сетевая ошибка при обращении к VLM API: {exc}")
            raise VLMError(
                message=f"Сетевая ошибка при связи с VLM провайдером: {exc}"
            ) from exc

        try:
            extracted_text = data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            logger.error(f"Некорректная структура JSON от VLM: {exc} | Data: {data}", exc, data)
            raise AIProviderResponseParseError() from exc

        elapsed = time.perf_counter() - start_time
        logger.info(f"Изображение {file_path.name} успешно обработано VLM за {elapsed:.2f} c")

        return f"## Содержимое изображения: {file_path.name}\n\n{extracted_text}"