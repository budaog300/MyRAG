import os
os.environ["TORCH_COMPILE_DISABLE"] = "1"
os.environ["TORCHDYNAMO_DISABLE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import asyncio
import time
from pathlib import Path
from typing import Set

from docling.document_converter import DocumentConverter, PdfFormatOption, ImageFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, PictureDescriptionApiOptions, TesseractOcrOptions
from docling.datamodel.base_models import InputFormat

from src.rag.components.converters import BaseDocumentConverter
from src.rag.schemas.converter_config import VLMConfig


class DoclingDocumentConverter(BaseDocumentConverter):
    """
    Универсальный конвертер документов на базе Docling.
    Поддерживает PDF, DOCX, PPTX, XLSX, HTML, PNG/JPEG и др.
    """

    SUPPORTED_EXTENSIONS: Set[str] = {
        ".pdf", ".docx", ".pptx", ".xlsx",
        ".html", ".htm", #".png", ".jpg", ".jpeg"
    }

    def __init__(self, vlm_config: VLMConfig | None = None):
        self.vlm_config = vlm_config or VLMConfig(enabled=False)
        self.converter = self._build_converter()

    def _build_converter(self) -> DocumentConverter:
        pipeline_options = PdfPipelineOptions()
        
        # Базовые обогащения
        pipeline_options.do_formula_enrichment = True
        pipeline_options.do_code_enrichment = True
        pipeline_options.images_scale = 2.0

        # pipeline_options.do_ocr = True
        # pipeline_options.ocr_options = TesseractOcrOptions()

        # Динамическое управление VLM
        if self.vlm_config.enabled:
            print("vlm включен")
            pipeline_options.generate_picture_images = True
            pipeline_options.do_picture_description = True
            pipeline_options.enable_remote_services = True

            headers = {}
            if self.vlm_config.api_key:
                headers["Authorization"] = f"Bearer {self.vlm_config.api_key}"

            params = {
                "model": self.vlm_config.model_name,
                "max_completion_tokens": self.vlm_config.max_tokens,
                **self.vlm_config.extra_params,
            }

            pipeline_options.picture_description_options = PictureDescriptionApiOptions(
                url=self.vlm_config.api_url,
                headers=headers,
                params=params,
                timeout=self.vlm_config.timeout,
                prompt=self.vlm_config.prompt
            )
        else:
            # Отключаем обработку и генерацию картинок для ускорения
            pipeline_options.generate_picture_images = False
            pipeline_options.do_picture_description = False
            pipeline_options.enable_remote_services = False

        return DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
                InputFormat.IMAGE: ImageFormatOption(pipeline_options=pipeline_options),
            }
        )

    async def convert(self, file_path: Path) -> str:
        start = time.perf_counter()

        result = await asyncio.to_thread(self.converter.convert, str(file_path))
        markdown = result.document.export_to_markdown()

        print(f"[{file_path.suffix.upper()}] Converted in: {time.perf_counter() - start:.2f}s")
        return markdown