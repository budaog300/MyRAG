import asyncio
import logging
from src.core.config import settingsRabbitMQ, settingsAI
from src.broker.consumer import RabbitMQConsumer
from src.rag.schemas.ingest import IngestDataSchema
from src.rag.repositories import QdrantRepository, ElasticRepository
from src.services import DocumentService, DocumentConverterService, AIService, S3Service
from src.rag.components.converters import DoclingDocumentConverter, TextDocumentConverter, VLMImageConverter, ExcelConverter
from src.rag.components.splitters import HierarchicalMarkdownSplitter
from src.worker_handler import process_document_task

logger = logging.getLogger(__name__)


async def main():
    logger.info("Создаем AI конфиг и AI сервис...")
    ai_config = settingsAI.build_ai_config()
    ai_service = AIService(ai_config)
    
    repo = QdrantRepository(ai_service.embedder)
    keyword_repo = ElasticRepository()

    logger.info("Инициализируем конвертеры...")
    docling_converter = DoclingDocumentConverter(ai_service)
    text_converter = TextDocumentConverter()
    excel_converter = ExcelConverter()
    image_converter = VLMImageConverter(ai_service)
    
    converter_service = DocumentConverterService([
        docling_converter, 
        text_converter, 
        image_converter, 
        excel_converter
    ])

    logger.info("Инициализируем сплиттер...")
    splitter = HierarchicalMarkdownSplitter()

    logger.info("Инициализируем DocumentService и S3Service...")
    doc_service = DocumentService(repo, keyword_repo, converter_service, splitter)
    s3_service = S3Service()

    consumer = RabbitMQConsumer()
    await consumer.connect()
    await consumer.setup_topology()

    async def handle_message(task: IngestDataSchema):
        await process_document_task(
            task=task, 
            document_service=doc_service, 
            s3_service=s3_service
        )

    logger.info("Запуск воркера обработки документов...")
    
    try:
        await consumer.consume(
            queue_name=settingsRabbitMQ.documents_queue,
            obj=IngestDataSchema,
            func=handle_message,
        )
    finally:
        logger.info("Закрываем соединения...")
        await consumer.close()
        await repo.close()
        await keyword_repo.close()
        logger.info("Воркер остановлен...")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())