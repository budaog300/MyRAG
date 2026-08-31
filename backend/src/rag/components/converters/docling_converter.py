import logging
import sys
import os
os.environ["TORCH_COMPILE_DISABLE"] = "1"
os.environ["TORCHDYNAMO_DISABLE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import asyncio
import time
from pathlib import Path
from typing import Set, Optional

from docling.document_converter import DocumentConverter, PdfFormatOption, ImageFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, PictureDescriptionApiOptions, TesseractOcrOptions, CodeFormulaVlmOptions
from docling.datamodel.stage_model_specs import (
    VlmModelSpec,
    ApiModelConfig,
    ResponseFormat,
    VlmEngineType
)
from docling.datamodel.vlm_engine_options import ApiVlmEngineOptions
from docling.datamodel.base_models import InputFormat

from src.rag.components.converters import BaseDocumentConverter
from src.services import AIService
from src.core.ai_config import CodeFormulaConfig, EngineMode
from src.core.exceptions import BaseAppException
from src.core.exceptions.converter_exceptions import (
    DocumentConversionError,
    DocumentFileNotFoundError,
    PipelineInitializationError,
    UnsupportedFileFormatError,
    VLMProviderServiceError,
)

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.getLogger("docling").setLevel(logging.DEBUG)

logger = logging.getLogger("DoclingDebug")

PICTURE_DESCRIPTION_PROMPT = """
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


class DoclingDocumentConverter(BaseDocumentConverter):
    """
    Универсальный конвертер документов на базе Docling.
    """

    SUPPORTED_EXTENSIONS: Set[str] = {
        ".pdf", ".docx", ".pptx",
        ".html", ".htm",
    }

    def __init__(
        self,
        ai_service: AIService,
        code_formula_config: Optional[CodeFormulaConfig] = None,
    ):        
        print("\n=== [DEBUG INIT START] ===")
        self.ai_service = ai_service
        self.code_formula_config = code_formula_config or CodeFormulaConfig(enabled=True, mode=EngineMode.LOCAL)
        
        try:
            self.converter = self._build_converter()
        except Exception as exc:
            logger.error(f"Не удалось собрать пайплайн Docling:{exc}", exc_info=True)
            raise PipelineInitializationError(reason=str(exc)) from exc

    def _build_converter(self) -> DocumentConverter:
        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = 2.0
        pipeline_options.enable_remote_services = True

        self._configure_code_and_formulas(pipeline_options)
        self._configure_picture_description(pipeline_options)

        return DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
                InputFormat.IMAGE: ImageFormatOption(pipeline_options=pipeline_options),
            }
        )

    def _configure_code_and_formulas(self, pipeline_options: PdfPipelineOptions) -> None:
        """Настройка распознавания кода и формул."""
        if not self.code_formula_config.enabled:
            pipeline_options.do_formula_enrichment = False
            pipeline_options.do_code_enrichment = False
            return

        pipeline_options.do_formula_enrichment = True
        pipeline_options.do_code_enrichment = True

        if self.code_formula_config.mode == EngineMode.API:
            headers = {}
            if self.code_formula_config.api_key:
                headers["Authorization"] = f"Bearer {self.code_formula_config.api_key}"

            engine_options = ApiVlmEngineOptions(
                url=self.code_formula_config.api_url,
                headers=headers or None,
            )

            api_config = ApiModelConfig(
                params={
                    "model": self.code_formula_config.model_name,
                    "temperature": self.code_formula_config.temperature,
                    "max_tokens": self.code_formula_config.max_tokens,
                }
            )

            vlm_spec = VlmModelSpec(
                name=self.code_formula_config.model_name,
                default_repo_id="docling-project/CodeFormula",
                prompt=self.code_formula_config.prompt,
                response_format=ResponseFormat.MARKDOWN,
                api_overrides={
                    VlmEngineType.API: api_config,
                    VlmEngineType.API_OPENAI: api_config,
                },
            )

            pipeline_options.code_formula_options = CodeFormulaVlmOptions(
                engine_type=VlmEngineType.API_OPENAI,
                model_spec=vlm_spec,
                engine_options=engine_options,
                extract_code=True,
                extract_formulas=True,
            )

    def _configure_picture_description(self, pipeline_options: PdfPipelineOptions) -> None:
        """Настройка генерации описаний для изображений через VLM."""
        if self.ai_service.vlm is None:
            pipeline_options.generate_picture_images = False
            pipeline_options.do_picture_description = False
            return

        vlm_config = self.ai_service.config.vlm
        pipeline_options.generate_picture_images = True
        pipeline_options.do_picture_description = True

        if vlm_config.mode == EngineMode.API:
            headers = {}
            if vlm_config.api_key:
                headers["Authorization"] = f"Bearer {vlm_config.api_key}"

            params = {
                "model": vlm_config.model_name,
                "max_completion_tokens": vlm_config.max_tokens,
                **vlm_config.extra_params,
            }

            pipeline_options.picture_description_options = PictureDescriptionApiOptions(
                url=vlm_config.api_url,
                headers=headers or None,
                params=params,
                timeout=vlm_config.timeout,
                prompt=PICTURE_DESCRIPTION_PROMPT,
            )

    async def convert(self, file_path: Path) -> str:
        if not file_path.exists():
            raise DocumentFileNotFoundError(file_path=str(file_path))

        if not self.supports(file_path):
            raise UnsupportedFileFormatError(extension=file_path.suffix)

        start_time = time.perf_counter()
        logger.info(f"Старт конвертации документа: {file_path.name}")

        try:
            result = await asyncio.to_thread(self.converter.convert, str(file_path))
            markdown = result.document.export_to_markdown()

            elapsed = time.perf_counter() - start_time
            logger.info(f"Файл {file_path.name} успешно конвертирован за {elapsed:.2f} c")
            return markdown

        except BaseAppException:
            raise
        except Exception as exc:
            exc_str = str(exc).lower()
            if "http" in exc_str or "connection" in exc_str or "api" in exc_str:
                raise VLMProviderServiceError(details=str(exc)) from exc

            raise DocumentConversionError(
                message=f"Ошибка обработки файла '{file_path.name}': {exc}"
            ) from exc