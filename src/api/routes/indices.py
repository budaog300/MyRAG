from fastapi import APIRouter, Query
from typing import List

from src.api.deps import KeywordRepoDep
from src.api.schemas import AddIndexSchema

router = APIRouter(prefix="/keyword/indices", tags=["Keyword Repository"])


@router.post("/", summary="Создать индекс")
async def create_index(index: AddIndexSchema, repo: KeywordRepoDep):
    await repo.create_index(index.name)
    return {"message": f"Индекс '{index.name}' создан успешно"}


@router.get("/", summary="Получить все индексы")
async def get_indices(
    repo: KeywordRepoDep,
    include_parents: bool = Query(
        default=False, 
        description="Включать ли служебные родительские коллекции (*_parents)"
    )
):
    return await repo.get_indices(include_parents=include_parents)


@router.get("/{index}", summary="Получить данные об индексе")
async def get_index_details(index: str, repo: KeywordRepoDep):
    return await repo.get_index_details(index)


@router.delete("/{index}/documents", summary="Очистить индекс")
async def clear_index(index: str, repo: KeywordRepoDep):
    await repo.clear_index(index)


@router.delete("/{index}", summary="Удалить индекс")
async def delete_index(index: str, repo: KeywordRepoDep):
    await repo.delete_index(index)
