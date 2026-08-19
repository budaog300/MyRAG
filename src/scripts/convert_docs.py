import asyncio
from pathlib import Path
from src.core.ai_config import ModelConfig, CodeFormulaConfig, EngineMode
from src.rag.components.converters import DoclingDocumentConverter, TextDocumentConverter, TesseractImageConverter, VLMImageConverter
from src.rag.services.convert_service import DocumentConverterService
from src.core.config import settingsAI
import torch

vlm_auth_data = settingsAI.get_vlm_config


async def main():
    print(torch.__version__)
    print(torch.cuda.is_available())
    print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else None)
    # vis-openai/gpt-5-nano
    vlm_config = ModelConfig(enabled=False)
    code_formula_config = CodeFormulaConfig(enabled=True, mode="api", api_key=vlm_auth_data["API_KEY"], api_url=vlm_auth_data["API_URL"], model_name="qwen/qwen3.7-plus")
    docling_converter = DoclingDocumentConverter(vlm_config=vlm_config, code_formula_config=code_formula_config)
    text_converter = TextDocumentConverter()
    image_converter = VLMImageConverter(vlm_config)
    converter_service = DocumentConverterService([docling_converter, text_converter, image_converter])
    num = 2
    format = "pdf"
    result = await converter_service.convert_to_markdown(source=f"./docs/test{num}.{format}")
    Path(f"./docs/test{num}.md").write_text(result, encoding="utf-8")


if __name__ == "__main__":
   asyncio.run((main()))