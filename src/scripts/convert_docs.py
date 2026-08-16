from pathlib import Path
from src.rag.services.converter_service import DocumentConverterService


if __name__ == "__main__":
    converter = DocumentConverterService()
    num = 3
    result = converter.convert(source=f"./docs/test{num}.pdf")
    Path(f"./docs/test{num}.md").write_text(result, encoding="utf-8")