import asyncio
from pathlib import Path
from src.rag.schemas.converter_config import VLMConfig
from src.rag.components.converters import DoclingDocumentConverter, TextDocumentConverter
from src.rag.services.convert_service import DocumentConverterService
import torch

async def main():
    print(torch.__version__)
    print(torch.cuda.is_available())
    print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else None)
    vlm_config = VLMConfig(enabled=False)
    docling_converter = DoclingDocumentConverter(vlm_config=vlm_config)
    text_converter = TextDocumentConverter()
    converter_service = DocumentConverterService([docling_converter, text_converter])
    num = 2
    result = await converter_service.convert_to_markdown(source=f"./docs/test{num}.pdf")
    Path(f"./docs/test{num}.md").write_text(result, encoding="utf-8")


if __name__ == "__main__":
   asyncio.run((main()))