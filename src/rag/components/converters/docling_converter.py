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
from src.rag.schemas.converter_config import VLMConfig, CodeFormulaConfig, EngineMode

logging.basicConfig(level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)
logging.getLogger("docling").setLevel(logging.DEBUG)

logger = logging.getLogger("DoclingDebug")


class DoclingDocumentConverter(BaseDocumentConverter):
    """
    Универсальный конвертер документов на базе Docling.
    """

    SUPPORTED_EXTENSIONS: Set[str] = {
        ".pdf", ".docx", ".pptx", ".xlsx",
        ".html", ".htm",
    }

    def __init__(
        self,
        vlm_config: Optional[VLMConfig] = None,
        code_formula_config: Optional[CodeFormulaConfig] = None,
    ):        
        print("\n=== [DEBUG INIT START] ===")
        self.vlm_config = vlm_config or VLMConfig(enabled=False)
        self.code_formula_config = code_formula_config or CodeFormulaConfig(enabled=True, mode=EngineMode.LOCAL)
        
        print(f"[DEBUG] VLMConfig Enabled: {self.vlm_config.enabled}, Mode: {getattr(self.vlm_config, 'mode', None)}, URL: {getattr(self.vlm_config, 'api_url', None)}")
        print(f"[DEBUG] CodeFormulaConfig Enabled: {self.code_formula_config.enabled}, Mode: {self.code_formula_config.mode}, URL: {self.code_formula_config.api_url}")
        
        self.converter = self._build_converter()
        print("=== [DEBUG INIT END] ===\n")

    def _build_converter(self) -> DocumentConverter:
        pipeline_options = PdfPipelineOptions()
        pipeline_options.images_scale = 2.0

        # ----------------------------------------------------
        # 1. Настройка формул и кода (Code & Formulas)
        # ----------------------------------------------------
        if self.code_formula_config.enabled:
            pipeline_options.do_formula_enrichment = True
            pipeline_options.do_code_enrichment = True

            if self.code_formula_config.mode == EngineMode.API:
                print(f"[DEBUG BUILD] Code/Formula -> Настройка API: {self.code_formula_config.api_url}")
                headers = {}
                if self.code_formula_config.api_key:
                    headers["Authorization"] = f"Bearer {self.code_formula_config.api_key}"

                engine_options = ApiVlmEngineOptions(
                    url=self.code_formula_config.api_url,
                    headers=headers if headers else None,
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

                print(f"[DEBUG BUILD] Создаем CodeFormulaVlmOptions с engine_type={VlmEngineType.API_OPENAI}...")
                pipeline_options.code_formula_options = CodeFormulaVlmOptions(
                    engine_type=VlmEngineType.API_OPENAI,
                    model_spec=vlm_spec,
                    engine_options=engine_options,
                    extract_code=True,
                    extract_formulas=True,
                )
                print(f"[DEBUG BUILD] CodeFormulaVlmOptions успешно привязан.")
            else:
                print("[DEBUG BUILD] Code/Formula -> Режим LOCAL")

        else:
            print("[DEBUG BUILD] Code/Formula -> ОТКЛЮЧЕНО")
            pipeline_options.do_formula_enrichment = False
            pipeline_options.do_code_enrichment = False

        # ----------------------------------------------------
        # 2. Настройка описания картинок (Picture Description)
        # ----------------------------------------------------
        if self.vlm_config.enabled:
            pipeline_options.generate_picture_images = True
            pipeline_options.do_picture_description = True
            
            if self.vlm_config.mode == EngineMode.API:
                print(f"[DEBUG BUILD] Picture Description -> Настройка API: {self.vlm_config.api_url}")
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
                    prompt=self.vlm_config.prompt,
                )
            else:
                print(f"[DEBUG BUILD] Picture Description -> Режим LOCAL ({self.vlm_config.model_name})")
        else:
            print("[DEBUG BUILD] Picture Description -> ОТКЛЮЧЕНО (do_picture_description=False)")
            pipeline_options.generate_picture_images = False
            pipeline_options.do_picture_description = False

        pipeline_options.enable_remote_services = True

        print("[DEBUG BUILD] Инициализируем DocumentConverter...")
        converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options),
                InputFormat.IMAGE: ImageFormatOption(pipeline_options=pipeline_options),
            }
        )
        print("[DEBUG BUILD] DocumentConverter успешно создан.")
        return converter

    async def convert(self, file_path: Path) -> str:
        start = time.perf_counter()
        print(f"\n=== [DEBUG CONVERT START] Файл: {file_path} ===")
        
        try:
            print("[DEBUG CONVERT] Вызываем self.converter.convert в отдельном потоке...")
            result = await asyncio.to_thread(self.converter.convert, str(file_path))
            print("[DEBUG CONVERT] Успешно конвертировано! Экспортируем в Markdown...")
            markdown = result.document.export_to_markdown()
            print(f"[{file_path.suffix.upper()}] Converted in: {time.perf_counter() - start:.2f}s")
            return markdown
        except Exception as e:
            print(f"!!! [DEBUG CONVERT ERROR] Ошибка во время конвертации: {e}")
            raise