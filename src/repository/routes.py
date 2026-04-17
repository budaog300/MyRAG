from fastapi import APIRouter, Request, Depends
from typing import Annotated, List

from src.core.deps import RepoDep
from src.schemas.schemas import AddCollectionSchema, CollectionSchema

router = APIRouter(prefix="/api/v1/collections", tags=["Repository"])


@router.post("/", summary="Создать коллекцию")
async def create_collection(collection: AddCollectionSchema, repo: RepoDep):
    await repo.create_collection(collection.name, size=384)


@router.get("/", summary="Получить все коллекции")
async def get_collections(repo: RepoDep) -> List[CollectionSchema]:
    return await repo.get_collections()


@router.get("/{collection_name}", summary="Получить данные о коллекции")
async def get_collection_details(collection_name: str, repo: RepoDep):
    return await repo.get_collection_details(collection_name)


@router.delete("/{collection_name}", summary="Удалить коллекцию")
async def delete_collection(collection_name: str, repo: RepoDep):
    await repo.delete_collection(collection_name)
