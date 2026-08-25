from fastapi import Request, Depends
from typing import Annotated

from src.rag.repositories import BaseVectorRepository, BaseKeywordRepository
from src.rag.services import RAGService, DocumentService, CollectionService, S3Service, DocumentIngestionService
from src.broker.publisher import RabbitMQPublisher


async def get_repo(request: Request) -> BaseVectorRepository:
    return request.app.state.repo


async def get_keyword_repo(request: Request) -> BaseKeywordRepository:
    return request.app.state.keyword_repo


async def get_rag_service(request: Request) -> RAGService:
    return request.app.state.rag_service


async def get_document_service(request: Request) -> DocumentService:
    return request.app.state.document_service


async def get_collection_service(request: Request) -> CollectionService:
    return request.app.state.collection_service


async def get_rabbitmq_publisher(request: Request) -> RabbitMQPublisher:
    return request.app.state.publisher


async def get_s3_service(request: Request) -> S3Service:
    return request.app.state.s3_service


RepoDep = Annotated[BaseVectorRepository, Depends(get_repo)]
KeywordRepoDep = Annotated[BaseKeywordRepository, Depends(get_keyword_repo)]
RAGDep = Annotated[RAGService, Depends(get_rag_service)]
DocumentDep = Annotated[DocumentService, Depends(get_document_service)]
CollectionDep = Annotated[CollectionService, Depends(get_collection_service)]
RabbitMQPublisherDep = Annotated[RabbitMQPublisher, Depends(get_rabbitmq_publisher)]
S3ServiceDep = Annotated[S3Service, Depends(get_s3_service)]


def get_ingestion_service(
    s3_service: S3ServiceDep,
    broker: RabbitMQPublisherDep,
) -> DocumentIngestionService:
    return DocumentIngestionService(s3_service=s3_service, broker=broker)


IngestionServiceDep = Annotated[DocumentIngestionService, Depends(get_ingestion_service)]