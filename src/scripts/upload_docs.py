import asyncio
from pathlib import Path
from src.core.logger import logger
from src.core.ai_config import AIServiceConfig
from src.rag.services import DocumentService, DocumentConverterService, AIService
from src.rag.schemas.document import RawDocumentSchema
from src.rag.repositories import QdrantRepository, ElasticRepository
from src.rag.components.converters import DoclingDocumentConverter, TextDocumentConverter, TesseractImageConverter, VLMImageConverter
from src.rag.components.splitters import MarkdownDocumentSplitter



async def main():
    logger.info("Начинаем загрузку документов в базы...")
    repo = QdrantRepository()
    keyword_repo = ElasticRepository()
    logger.info("Создаем AI конфиг и AI сервис...")
    ai_config = AIServiceConfig()
    ai_service = AIService(ai_config)
    logger.info("Инициализируем конвертеры...")
    docling_converter = DoclingDocumentConverter(ai_service)
    text_converter = TextDocumentConverter()
    image_converter = VLMImageConverter(ai_service)
    converter_service = DocumentConverterService([docling_converter, text_converter, image_converter])
    logger.info("Инициализируем сплиттер...")
    splitter = MarkdownDocumentSplitter()
    doc_service = DocumentService(repo, keyword_repo, converter_service, splitter, model="sentence-transformers/all-MiniLM-L6-v2")
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
    await doc_service.ingest_files("sber_docs", raw_docs)
    logger.info("Документы успешно загружены")
    await repo.close()
    await keyword_repo.close()


if __name__ == "__main__":
    asyncio.run(main())
