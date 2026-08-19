import base64
import asyncio
from pathlib import Path
from typing import Set
import httpx

from src.rag.components.converters.base import BaseDocumentConverter
from src.rag.services import AIService


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
        if self.ai_service.vlm is None:
            print(f"[VLMImageConverter] VLM отключен (enabled=False). Пропуск обработки изображения: {file_path.name}")
            return f"<!-- Обработка изображения {file_path.name} пропущена (VLM отключен) -->"
        vlm_config = self.ai_service.config.vlm
        base64_image = await asyncio.to_thread(self._encode_image, file_path)
        
        ext = file_path.suffix.lower().replace(".", "")
        mime_type = "image/jpeg" if ext in ["jpg", "jpeg"] else f"image/{ext}"

        payload = {
            "model": vlm_config.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": vlm_config.prompt},
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
            **vlm_config.extra_params
        }

        headers = {"Content-Type": "application/json"}
        if vlm_config.api_key:
            headers["Authorization"] = f"Bearer {vlm_config.api_key}"

        async with httpx.AsyncClient(timeout=vlm_config.timeout) as client:
            response = await client.post(
                vlm_config.api_url,
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            extracted_text = data["choices"][0]["message"]["content"].strip()
            return f"## Содержимое изображения: {file_path.name}\n\n{extracted_text}"