import base64
from typing import List
from src.rag.ai.providers import BaseVLMProvider, BaseAIProvider


class VLMProvider(BaseAIProvider, BaseVLMProvider):
    async def analyze_image(
        self, image_bytes: bytes, prompt: str, mime_type: str = "image/jpeg"
    ) -> str:
        b64_image = base64.b64encode(image_bytes).decode("utf-8")
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
        return data["choices"][0]["message"]["content"]