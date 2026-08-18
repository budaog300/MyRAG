import asyncio
from pathlib import Path
from typing import Set
from PIL import Image
import pytesseract

from src.rag.components.converters import BaseDocumentConverter


class TesseractImageConverter(BaseDocumentConverter):
    SUPPORTED_EXTENSIONS: Set[str] = {".png", ".jpg", ".jpeg", ".webp"}

    def __init__(self, tesseract_cmd: str = r"C:\Program Files\Tesseract-OCR\tesseract.exe"):
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    async def convert(self, file_path: Path) -> str:
        def _ocr():
            with Image.open(file_path) as img:
                return pytesseract.image_to_string(img, lang="rus+eng", config="--psm 6")

        text = await asyncio.to_thread(_ocr)
        text = text.strip()

        if not text:
            return f"<!-- Изображение {file_path.name}: текст не найден -->"

        return f"## Текст с изображения: {file_path.name}\n\n{text}"