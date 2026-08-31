from fastapi import Request, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from src.rag.repositories import BaseVectorRepository, BaseKeywordRepository
from src.services import RAGService, DocumentService, CollectionService, S3Service, DocumentIngestionService, HealthCheckService
from src.db.repositories import RepositoryContainer, CollectionRepository, DocumentRepository
from src.broker.publisher import RabbitMQPublisher
from src.db.database import get_db


class Pagination:
    def __init__(
        self,
        page: int = Query(default=1, ge=1),
        size: int = Query(default=5, ge=1, le=100)
    ):
        self.page = page
        self.size = size
    
    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


async def get_repo(request: Request) -> BaseVectorRepository:
    return request.app.state.repo


async def get_keyword_repo(request: Request) -> BaseKeywordRepository:
    return request.app.state.keyword_repo


async def get_document_service(request: Request) -> DocumentService:
    return request.app.state.document_service


async def get_rabbitmq_publisher(request: Request) -> RabbitMQPublisher:
    return request.app.state.publisher


async def get_s3_service(request: Request) -> S3Service:
    return request.app.state.s3_service


async def get_repositories(
    session: AsyncSession = Depends(get_db),
) -> RepositoryContainer:
    return RepositoryContainer(
        collection_repo=CollectionRepository(session),
        document_repo=DocumentRepository(session),
    )


async def get_rag_service(
    request: Request,
) -> RAGService:
    return request.app.state.rag_service


PaginationDep = Annotated[Pagination, Depends(Pagination)]
RepoDep = Annotated[BaseVectorRepository, Depends(get_repo)]
KeywordRepoDep = Annotated[BaseKeywordRepository, Depends(get_keyword_repo)]
DatabaseDep = Annotated[RepositoryContainer, Depends(get_repositories)]
DocumentDep = Annotated[DocumentService, Depends(get_document_service)]
RabbitMQPublisherDep = Annotated[RabbitMQPublisher, Depends(get_rabbitmq_publisher)]
S3ServiceDep = Annotated[S3Service, Depends(get_s3_service)]
RAGDep = Annotated[RAGService, Depends(get_rag_service)]


def get_ingestion_service(
    s3_service: S3ServiceDep,
    broker: RabbitMQPublisherDep,
    db_repo: DatabaseDep
) -> DocumentIngestionService:
    return DocumentIngestionService(s3_service=s3_service, broker=broker, db_repo=db_repo)


def get_health_service(
    repo: RepoDep,
    keyword_repo: KeywordRepoDep,
    s3_service: S3ServiceDep,
    broker: RabbitMQPublisherDep,
    db_repo: DatabaseDep
) -> HealthCheckService:
    return HealthCheckService(
        repo=repo,        
        keyword_repo=keyword_repo,
        s3_service=s3_service,
        broker=broker,
        db_repo=db_repo
    )


async def get_collection_service(
    db_repo: DatabaseDep,
    vector_repo: RepoDep,
    keyword_repo: KeywordRepoDep,
    s3_service: S3ServiceDep,
) -> CollectionService:
    return CollectionService(
        db_repo=db_repo,
        vector_repo=vector_repo,
        keyword_repo=keyword_repo,
        s3_service=s3_service
    )


IngestionServiceDep = Annotated[DocumentIngestionService, Depends(get_ingestion_service)]
HealthCheckDep = Annotated[HealthCheckService, Depends(get_health_service)]
CollectionDep = Annotated[CollectionService, Depends(get_collection_service)]