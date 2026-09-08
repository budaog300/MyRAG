import asyncio
from pathlib import Path
from typing import Set, Optional

from docling.document_converter import DocumentConverter, PdfFormatOption, ImageFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, PictureDescriptionApiOptions, CodeFormulaVlmOptions
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
from src.core.ai_config import EngineMode
from src.core.exceptions import BaseAppException
from src.core.exceptions.converter_exceptions import (
    DocumentConversionError,
    DocumentFileNotFoundError,
    PipelineInitializationError,
    UnsupportedFileFormatError,
    VLMProviderServiceError,
)
from src.core.logger import logger


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
        ai_service: AIService
    ):        
        print("\n=== [DEBUG INIT START] ===")
        self.ai_service = ai_service
        
        try:
            self.converter = self._build_converter()
        except Exception as exc:
            logger.error(f"Не удалось собрать пайплайн Docling:{exc}", exc_info=True)
            raise PipelineInitializationError(reason=str(exc)) from exc

    def _build_converter(self) -> DocumentConverter:
        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = 2.0
        pipeline_options.enable_remote_services = True

        self._configure_vlm(pipeline_options)

        return DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
                InputFormat.IMAGE: ImageFormatOption(pipeline_options=pipeline_options),
            }
        )

    def _configure_vlm(
        self,
        pipeline_options: PdfPipelineOptions,
    ) -> None:
        vlm_config = self.ai_service.config.vlm

        if vlm_config is None or not vlm_config.enabled:
            logger.info("VLM enrichment отключен")

            pipeline_options.generate_picture_images = False
            pipeline_options.do_picture_description = False
            pipeline_options.do_formula_enrichment = False
            pipeline_options.do_code_enrichment = False

            return

        if vlm_config.mode != EngineMode.API:
            raise PipelineInitializationError(
                reason="Docling VLM enrichment поддерживает только API mode"
            )

        headers = {}

        if vlm_config.api_key:
            headers["Authorization"] = (
                f"Bearer {vlm_config.api_key}"
            )

        params = {
            "model": vlm_config.model_name,
        }

        if vlm_config.max_tokens is not None:
            params["max_tokens"] = vlm_config.max_tokens

        params.update(vlm_config.extra_params)

        # ============================================================
        # 1. PICTURE
        # ============================================================

        pipeline_options.generate_picture_images = True
        pipeline_options.do_picture_description = True

        pipeline_options.picture_description_options = (
            PictureDescriptionApiOptions(
                url=vlm_config.api_url,
                headers=headers or None,
                params=params,
                timeout=vlm_config.timeout,
                prompt=vlm_config.picture_prompt,
            )
        )

        # ============================================================
        # 2. CODE + FORMULAS
        # ============================================================

        pipeline_options.do_formula_enrichment = True
        pipeline_options.do_code_enrichment = True

        engine_options = ApiVlmEngineOptions(
            url=vlm_config.api_url,
            headers=headers or None,
        )

        api_config = ApiModelConfig(
            params=params,
        )

        model_spec = VlmModelSpec(
            name=vlm_config.model_name,
            default_repo_id="docling-project/CodeFormula",
            prompt=vlm_config.code_formula_prompt,
            response_format=ResponseFormat.MARKDOWN,
            api_overrides={
                VlmEngineType.API: api_config,
                VlmEngineType.API_OPENAI: api_config,
            },
        )
        pipeline_options.code_formula_options = (
            CodeFormulaVlmOptions(
                engine_type=VlmEngineType.API_OPENAI,                
                model_spec=model_spec,
                engine_options=engine_options,
                extract_code=True,
                extract_formulas=True,
            )
        )

    async def _convert(self, file_path: Path) -> str:
        if not file_path.exists():
            raise DocumentFileNotFoundError(file_path=str(file_path))

        if not self.supports(file_path):
            raise UnsupportedFileFormatError(extension=file_path.suffix)
        try:
            result = await asyncio.to_thread(self.converter.convert, str(file_path))
            markdown = result.document.export_to_markdown()
            return markdown

        except BaseAppException:
            raise
        except Exception as exc:
            logger.exception(
                "Ошибка конвертации файла '%s' через %s",
                file_path.name,
                self.__class__.__name__,
            )
            exc_str = str(exc).lower()
            if "http" in exc_str or "connection" in exc_str or "api" in exc_str:
                raise VLMProviderServiceError(details=str(exc)) from exc

            raise DocumentConversionError(
                message=f"Ошибка обработки файла '{file_path.name}': {exc}"
            ) from exc