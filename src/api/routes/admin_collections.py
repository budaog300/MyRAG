from typing import List, Any, Optional
from fastapi import APIRouter, Depends, Query, status
from src.api.schemas.request_schemas import AddCollectionSchema
from src.api.schemas.response_schemas import CollectionSchema
from src.api.deps import CollectionDep

router = APIRouter(prefix="/collections", tags=["Admin Collections"])


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Создать коллекцию во всех БД")
async def admin_create_collection(
    collection: AddCollectionSchema, 
    service: CollectionDep
):
    await service.create_collection(collection.name, collection.size, collection.distance)
    return {"message": f"Коллекция и индексы для '{collection.name}' успешно созданы"}


@router.get("/", response_model=List[CollectionSchema], summary="Получить список коллекций")
async def admin_get_collections(
    service: CollectionDep,
    include_parents: bool = Query(default=False, description="Включать ли служебные коллекции (*_parents)")    
):
    return await service.get_collections(include_parents=include_parents)


@router.get("/{collection_name}", summary="Детальная информация о коллекции (Vector repo + Keyword repo)")
async def admin_get_collection_details(
    collection_name: str, 
    service: CollectionDep
):
    return await service.get_collection_details(collection_name)


@router.delete("/{collection_name}/documents/{file_id}", summary="Удалить конкретный документ по file_id")
async def admin_delete_document_by_id(
    collection_name: str, 
    file_id: str, 
    service: CollectionDep
):
    await service.delete_document_by_file_id(collection_name, file_id)
    return {"message": f"Документ '{file_id}' удален из коллекций"}


@router.delete("/{collection_name}/points", summary="Очистить содержимое коллекции")
async def admin_clear_collection(
    collection_name: str, 
    service: CollectionDep
):
    await service.clear_collection(collection_name)
    return {"message": f"Содержимое коллекции '{collection_name}' полностью очищено"}


@router.delete("/{collection_name}", summary="Удалить коллекцию и индексы из всех БД")
async def admin_delete_collection(
    collection_name: str, 
    service: CollectionDep
):
    await service.delete_collection(collection_name)
    return {"message": f"Коллекция '{collection_name}' и её индексы полностью удалены"}