import asyncio
from pathlib import Path
from src.core.ai_config import ModelConfig, CodeFormulaConfig, EngineMode, AIServiceConfig
from src.rag.components.converters import DoclingDocumentConverter, TextDocumentConverter, VLMImageConverter, ExcelConverter
from src.rag.services.convert_service import DocumentConverterService
from src.rag.services.ai_service import AIService
from src.core.config import settingsAI
import torch

ai_config = settingsAI.build_ai_config()


async def main():
    print(torch.__version__)
    print(torch.cuda.is_available())
    print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else None)
    ai_service = AIService(ai_config)
    # vis-openai/gpt-5-nano
    # code_formula_config = CodeFormulaConfig(enabled=True, mode="api", api_key=auth_data["API_KEY"], api_url=auth_data["API_URL"], model_name="qwen/qwen3.7-plus")
    docling_converter = DoclingDocumentConverter(ai_service)
    text_converter = TextDocumentConverter()
    excel_converter = ExcelConverter()
    image_converter = VLMImageConverter(ai_service)
    converter_service = DocumentConverterService([docling_converter, text_converter, image_converter, excel_converter])
    num = 10
    format = "xlsx"
    result = await converter_service.convert_to_markdown(source=f"./docs/test{num}.{format}")
    Path(f"./docs/test{num}.md").write_text(result, encoding="utf-8")


if __name__ == "__main__":
   asyncio.run((main()))