from fastapi import APIRouter
from typing import List

from src.core.deps import KeywordRepoDep
from src.schemas.schemas import AddIndexSchema, IndexSchema

router = APIRouter(prefix="/api/v1/indices", tags=["Keyword Repository"])


@router.post("/", summary="Создать индекс")
async def create_index(index: AddIndexSchema, repo: KeywordRepoDep):
    await repo.create_index(index.name)


@router.get("/", summary="Получить все индексы")
async def get_indices(repo: KeywordRepoDep) -> List[IndexSchema]:
    return await repo.get_indices()


@router.delete("/{index}/documents", summary="Очистить индекс")
async def clear_index(index: str, repo: KeywordRepoDep):
    await repo.clear_index(index)


@router.delete("/{index}", summary="Удалить индекс")
async def delete_index(index: str, repo: KeywordRepoDep):
    await repo.delete_index(index)
