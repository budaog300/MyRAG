from typing import Dict, Any, Optional
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class EngineMode(str, Enum):
    LOCAL = "local"
    API = "api"


class VLMConfig(BaseModel):
    """Конфигурация распознавания изображений в pdf"""
    model_config = ConfigDict(extra="allow")

    enabled: bool = True
    mode: EngineMode = EngineMode.LOCAL

    api_url: str = "http://localhost:11434/v1/chat/completions" 
    api_key: Optional[str] = None
    model_name: str = "qwen3-vl:2b"
    max_tokens: int = 8192
    timeout: int = 90
    prompt: str = """
        Ты — OCR и VLM-аналитик для базы знаний. Внимательно изучи ВСЁ ИЗОБРАЖЕНИЕ от верхнего до нижнего края.

        Сделай следующее:
        1. ВЫПИШИ ВЕСЬ ТЕКСТ: Найди и дословно перепиши абсолютно все заголовки, подзаголовки, списки и подписи к иконкам, весь текст.
        2. СМЫСЛ И СТРУКТУРА: В 2-3 предложениях описать главный смысл инфографики или схемы.
        3. НЕ ОПИСЫВАЙ ВИЗУАЛЬНЫЙ СТИЛЬ (цвета, фон, градиенты): фокус только на данных и тексте.

        Формат ответа:
        **Текст на картинке:**
        - [Заголовок]
        - [Пункт 1]
        - [Пункт 2] ...

        **Описание картинки:**
        [Краткое описание]
    """.strip()

    @property
    def extra_params(self) -> Dict[str, Any]:
        """Возвращает все доп. аргументы, переданные через kwargs"""
        return self.model_extra or {}


class CodeFormulaConfig(BaseModel):
    """Конфигурация распознавания кода и формул"""
    enabled: bool = True
    mode: EngineMode = EngineMode.LOCAL

    api_url: str = "http://localhost:11434/v1/chat/completions"
    model_name: str = "qwen3-vl:2b"
    api_key: Optional[str] = None
    prompt: str = "Extract all formulas in LaTeX and code blocks cleanly."
    max_tokens: int = 8192
    temperature: float = 0.0