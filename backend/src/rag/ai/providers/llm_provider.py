import base64
import httpx
from typing import List, Optional, Dict, Any
from src.rag.ai.providers import BaseLLMProvider, BaseAIProvider
from src.core.exceptions.provider_exceptions import LLMError


class LLMProvider(BaseAIProvider, BaseLLMProvider):
    async def generate(
        self, 
        prompt: str, 
        system_prompt: Optional[str] = None, 
        temperature: float = 0.3, 
        max_tokens: int = 4096
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **self.config.extra_params,
        }
        data = await self._post(payload)
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as e:
            raise LLMError(f"Не удалось извлечь ответ LLM: {e}")