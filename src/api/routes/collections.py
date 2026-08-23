from fastapi import APIRouter, Request, Depends, Query
from typing import Annotated, List

from src.api.deps import RepoDep
from src.api.schemas import AddCollectionSchema, CollectionSchema

router = APIRouter(prefix="/api/v1/collections", tags=["Vector Repository"])


@router.post("/", summary="Создать коллекцию")
async def create_collection(collection: AddCollectionSchema, repo: RepoDep):
    await repo.create_collection(collection.name, collection.size, collection.distance)
    return {"message": f"Коллекция '{collection.name}' создана успешно"}


@router.get("/", summary="Получить список коллекций")
async def get_collections(
    repo: RepoDep, 
    include_parents: bool = Query(
        default=False, 
        description="Включать ли служебные родительские коллекции (*_parents)"
    )
) -> List[CollectionSchema]:
    return await repo.get_collections(include_parents=include_parents)


@router.get("/{collection_name}", summary="Получить данные о коллекции")
async def get_collection_details(collection_name: str, repo: RepoDep):
    return await repo.get_collection_details(collection_name)


@router.delete("/{collection_name}/points", summary="Очистить коллекцию")
async def clear_collection(collection_name: str, repo: RepoDep):
    await repo.clear_collection(collection_name)


@router.delete("/{collection_name}", summary="Удалить коллекцию")
async def delete_collection(collection_name: str, repo: RepoDep):
    await repo.delete_collection(collection_name)
