import os

os.environ["TORCH_COMPILE_DISABLE"] = "1"
os.environ["TORCHDYNAMO_DISABLE"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"
import time
from pathlib import Path
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.pipeline_options import PdfPipelineOptions, granite_picture_description
from docling.datamodel.base_models import InputFormat
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logging.getLogger("docling").setLevel(logging.DEBUG)


class DocumentConverterService:
    def __init__(self):
        pipeline_options = PdfPipelineOptions()

        pipeline_options.do_picture_description = True
        pipeline_options.do_formula_enrichment = True
        pipeline_options.do_code_enrichment = True
        pipeline_options.picture_description_options = granite_picture_description

        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(
                    pipeline_options=pipeline_options
                )
            }
        )

    def convert(self, source: str | Path) -> str:
        start = time.perf_counter()

        result = self.converter.convert(source)

        markdown = result.document.export_to_markdown()

        print(f"Elapsed time: {time.perf_counter() - start:.2f}s")

        return markdown