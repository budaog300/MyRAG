# src/rag/components/converters/image_converter.py
import asyncio
from pathlib import Path
from typing import Set
from rapidocr_onnxruntime import RapidOCR

from src.rag.components.converters import BaseDocumentConverter


class RapidOCRImageConverter(BaseDocumentConverter):
    """
    Конвертер для изображений (.png, .jpg, .jpeg), использующий RapidOCR
    для извлечения печатного текста (включая русский и английский).
    """

    SUPPORTED_EXTENSIONS: Set[str] = {".png", ".jpg", ".jpeg", ".webp"}

    def __init__(self):
        self.engine = RapidOCR(
            use_angle_cls=True,
            box_thresh=0.5,
            unclip_ratio=1.6,
        )

    async def convert(self, file_path: Path) -> str:
        # Запускаем синхронный OCR в отдельном потоке, чтобы не блокировать event loop
        result, _ = await asyncio.to_thread(self.engine, str(file_path))

        if not result:
            return f"<!-- Изображение {file_path.name}: текст не найден -->"

        # Извлекаем распознанные строки
        # result имеет структуру: [[box, text, score], ...]
        lines = [item[1] for item in result if item[1].strip()]

        if not lines:
            return f"<!-- Изображение {file_path.name}: текст не найден -->"

        formatted_text = "\n".join(lines)
        return f"## Текст с изображения: {file_path.name}\n\n{formatted_text}"