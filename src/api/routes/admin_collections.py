from typing import List, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from src.api.schemas.request_schemas import AddCollectionSchema, QuerySchema
from src.api.schemas.response_schemas import CollectionSchema, RAGResponseSchema
from src.api.deps import CollectionDep, RAGDep, QdrantPaginationDep, PaginationDep

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


@router.delete("/{collection_name}/points", summary="Очистить содержимое коллекции")
async def admin_clear_collection(
    collection_name: str, 
    service: CollectionDep
):
    await service.clear_collection(collection_name)
    return {"message": f"Содержимое коллекции '{collection_name}' полностью очищено вместе с исходными файлами"}


@router.delete("/{collection_name}", summary="Удалить коллекцию и исходные файлы")
async def admin_delete_collection(
    collection_name: str, 
    service: CollectionDep
):
    await service.delete_collection(collection_name)
    return {"message": f"Коллекция '{collection_name}' и её индексы полностью удалены"}


@router.get("/{collection_name}/documents", response_model=List[CollectionSchema], summary="Получить список документов из коллекции")
async def admin_get_collection_documents(
    service: CollectionDep,
    pagination: PaginationDep
):
    return {"message": "Метод пока не готов"}


@router.delete("/{collection_name}/documents/{document_id}", summary="Удалить документ и его исходный файл по document_id")
async def admin_delete_document(
    collection_name: str, 
    document_id: UUID, 
    service: CollectionDep
):
    await service.delete_document(collection_name, document_id)
    return {"message": f"Документ '{document_id}' удален из коллекций"}


@router.get("/{collection_name}/documents/{document_id}/chunks", summary="Получить чанки документа")
async def admin_get_document_chunks(
    collection_name: str,
    document_id: UUID,
    service: CollectionDep,
    pagination: QdrantPaginationDep
):
    chunks, next_offset = await service.get_chunks(
        collection_name=collection_name,
        document_id=document_id,
        limit=pagination.limit,
        offset=pagination.offset,
    )
    return {
        "items": chunks,
        "next_offset": next_offset,
    }


@router.post("/{collection_name}/search", response_model=RAGResponseSchema, summary="Запрос в документацию (RAG)")
async def rag_query(collection_name: str, body: QuerySchema, rag_service: RAGDep):
    answer = await rag_service.run(
        collection_name=collection_name,
        **body.model_dump()
    )
    return answer