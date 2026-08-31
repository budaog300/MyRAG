import time
import asyncio
from pathlib import Path
from src.core.logger import logger
from src.core.config import settingsAI
from src.services import DocumentService, DocumentConverterService, AIService
from src.rag.schemas.document import RawDocumentSchema
from src.rag.repositories import QdrantRepository, ElasticRepository
from src.rag.components.converters import DoclingDocumentConverter, TextDocumentConverter, VLMImageConverter, ExcelConverter
from src.rag.components.splitters import MarkdownDocumentSplitter, HierarchicalMarkdownSplitter



async def main():
    logger.info("Начинаем загрузку документов в базы...")
    ai_config = settingsAI.build_ai_config()
    ai_service = AIService(ai_config)
    print(ai_service.__dict__)
    repo = QdrantRepository(ai_service.embedder)
    keyword_repo = ElasticRepository()
    logger.info("Создаем AI конфиг и AI сервис...")   
    logger.info("Инициализируем конвертеры...")
    docling_converter = DoclingDocumentConverter(ai_service)
    text_converter = TextDocumentConverter()
    excel_converter = ExcelConverter()
    image_converter = VLMImageConverter(ai_service)
    converter_service = DocumentConverterService([docling_converter, text_converter, image_converter, excel_converter])
    logger.info("Инициализируем сплиттер...")
    splitter = HierarchicalMarkdownSplitter()
    doc_service = DocumentService(repo, keyword_repo, converter_service, splitter)
    logger.info("Парсим файлы...")
    raw_docs = [
        RawDocumentSchema(
            source=str(path),
            metadata={"filename": path.name}
        )
        for path in Path("./docs").glob("**/*") 
        if path.is_file()
    ]
    logger.info(f"Считано документов: {len(raw_docs)}")
    start = time.perf_counter()
    await doc_service.ingest_files("sber_docs", raw_docs)
    elapsed_time = time.perf_counter() - start
    logger.info(f"Документы успешно загружены (потраченное время: {elapsed_time})")
    await repo.close()
    await keyword_repo.close()


if __name__ == "__main__":
    asyncio.run(main())
