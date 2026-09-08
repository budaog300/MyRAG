import logging
import base64
from typing import List
from src.rag.ai.providers import BaseVLMProvider, BaseAIProvider
from src.core.exceptions.provider_exceptions import VLMError

logger = logging.getLogger(__name__)


class VLMProvider(BaseAIProvider, BaseVLMProvider):
    async def analyze_image(
        self, image_bytes: bytes, prompt: str, mime_type: str = "image/jpeg"
    ) -> str:
        try:
            b64_image = base64.b64encode(image_bytes).decode("utf-8")
        except Exception as e:
            logger.exception("VLM image encoding failed: model=%s", self.config.model_name)
            raise VLMError(f"Ошибка кодирования изображения в base64: {e}")

        payload = {
            "model": self.config.model_name,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:{mime_type};base64,{b64_image}"},
                        },
                    ],
                }
            ],
            **self.config.extra_params,
        }

        data = await self._post(payload)
        
        try:
            result = data["choices"][0]["message"]["content"]
            logger.info("VLM response: model=%s, response_length=%d", self.config.model_name, len(result))
            return result
        except (KeyError, IndexError, TypeError) as e:
            logger.error("VLM response parsing failed: model=%s, error=%s", self.config.model_name, e)
            raise VLMError(f"Не удалось извлечь ответ VLM: {e}")