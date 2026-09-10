import base64
import logging
import asyncio
from pathlib import Path
from typing import Set
import httpx

from src.rag.components.converters.base import BaseDocumentConverter
from src.services import AIService
from src.core.exceptions import BaseAppException
from src.core.exceptions.provider_exceptions import (
    AIProviderResponseParseError,    
    VLMError
)
from src.core.exceptions.converter_exceptions import (
    DocumentConversionError,
    DocumentFileNotFoundError,
    UnsupportedFileFormatError
)

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

    async def _convert(self, file_bytes: bytes, filename: str) -> str:
        if not self.supports(filename):
            raise UnsupportedFileFormatError(extension=Path(filename).suffix)

        if self.ai_service.vlm is None:
            logger.warning("VLM отключен (enabled=False). Пропуск обработки изображения: %s", filename)
            return f"<!-- Обработка изображения {filename} пропущена (VLM отключен) -->"

        vlm_config = self.ai_service.config.vlm
        if vlm_config is None or vlm_config.primary is None:
            raise VLMError(message="Конфигурация VLM не настроена")

        try:
            ext = Path(filename).suffix.lower().replace(".", "")
            mime_type = "image/jpeg" if ext in ("jpg", "jpeg") else f"image/{ext}"

            extracted_text = await self.ai_service.vlm.analyze_image(
                image_bytes=file_bytes,
                prompt=vlm_config.primary.picture_prompt,
                mime_type=mime_type,
            )
        except BaseAppException:
            raise
        except Exception as exc:
            logger.exception("Ошибка обработки изображения '%s' через VLM", filename)
            raise DocumentConversionError(message=f"Ошибка обработки изображения '{filename}': {exc}") from exc

        return f"## Содержимое изображения: {filename}\n\n{extracted_text}"