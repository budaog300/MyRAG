from fastapi import Request, Depends
from typing import Annotated

from src.repository import VectorBaseRepository
from src.services.rag_service import RAGService


async def get_repo(request: Request) -> VectorBaseRepository:
    return request.app.state.repo


async def get_rag_service(request: Request) -> RAGService:
    return request.app.state.rag_service


RepoDep = Annotated[VectorBaseRepository, Depends(get_repo)]
RAGDep = Annotated[RAGService, Depends(get_rag_service)]
