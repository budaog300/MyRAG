from fastapi import Request, Depends
from typing import Annotated

from src.rag.repositories import BaseVectorRepository, BaseKeywordRepository
from src.rag.services import RAGService, DocumentService


async def get_repo(request: Request) -> BaseVectorRepository:
    return request.app.state.repo


async def get_keyword_repo(request: Request) -> BaseKeywordRepository:
    return request.app.state.keyword_repo


async def get_rag_service(request: Request) -> RAGService:
    return request.app.state.rag_service


async def get_document_service(request: Request) -> DocumentService:
    return request.app.state.document_service


RepoDep = Annotated[BaseVectorRepository, Depends(get_repo)]
KeywordRepoDep = Annotated[BaseKeywordRepository, Depends(get_keyword_repo)]
RAGDep = Annotated[RAGService, Depends(get_rag_service)]
DocumentDep = Annotated[DocumentService, Depends(get_document_service)]
