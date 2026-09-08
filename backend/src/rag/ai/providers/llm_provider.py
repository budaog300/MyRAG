import logging
from typing import List, Optional, Dict, Any
from src.rag.ai.providers import BaseLLMProvider, BaseAIProvider
from src.core.exceptions.provider_exceptions import LLMError

logger = logging.getLogger(__name__)


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
            result = data["choices"][0]["message"]["content"]
            logger.info("LLM response: model=%s, response_length=%d", self.config.model_name, len(result))
            return result
        except (KeyError, IndexError, TypeError) as e:
            logger.error("LLM response parsing failed: model=%s, error=%s", self.config.model_name, e)
            raise LLMError(f"Не удалось извлечь ответ LLM: {e}")