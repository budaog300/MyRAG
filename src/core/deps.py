from fastapi import Request, Depends
from typing import Annotated

from src.repository import VectorBaseRepository, KeywordBaseRepository
from src.services.rag_service import RAGService


async def get_repo(request: Request) -> VectorBaseRepository:
    return request.app.state.repo


async def get_keyword_repo(request: Request) -> KeywordBaseRepository:
    return request.app.state.keyword_repo


async def get_rag_service(request: Request) -> RAGService:
    return request.app.state.rag_service


RepoDep = Annotated[VectorBaseRepository, Depends(get_repo)]
KeywordRepoDep = Annotated[KeywordBaseRepository, Depends(get_keyword_repo)]
RAGDep = Annotated[RAGService, Depends(get_rag_service)]
