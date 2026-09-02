from typing import List
from uuid import UUID
from fastapi import APIRouter, Query, status
from src.api.schemas.request_schemas import AddCollectionSchema, QuerySchema, UpdateCollectionSchema
from src.api.schemas.response_schemas import CollectionResponseSchema, CollectionDetailsResponseSchema, DocumentSchema, DocumentsResponseSchema, RAGResponseSchema
from src.api.deps import CollectionDep, RAGDep, PaginationDep, DatabaseDep

router = APIRouter(prefix="/collections", tags=["Admin Collections"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=CollectionResponseSchema, summary="Создать коллекцию во всех БД")
async def admin_create_collection(
    collection: AddCollectionSchema, 
    service: CollectionDep
):
    collection = await service.create_collection(
        name=collection.name,
        size=collection.size,
        distance=collection.distance,
        description=collection.description,
    )
    return collection


@router.get("", response_model=List[CollectionResponseSchema], summary="Получить список коллекций")
async def admin_get_collections(
    service: CollectionDep   
):
    return await service.get_collections()


@router.get("/{collection_id}", response_model=CollectionDetailsResponseSchema, summary="Детальная информация о коллекции (Vector repo + Keyword repo)")
async def admin_get_collection_details(
    collection_id: UUID,
    service: CollectionDep
):
    return await service.get_collection_details(collection_id)


@router.patch("/{collection_id}", response_model=CollectionDetailsResponseSchema, summary="Обновить коллекцию")
async def update_collection(
    collection_id: UUID,
    data: UpdateCollectionSchema,
    service: CollectionDep,
):
    return await service.update_collection(
        collection_id=collection_id,
        name=data.name,
        description=data.description,
    )


@router.delete("/{collection_id}/points", summary="Очистить содержимое коллекции")
async def admin_clear_collection(
    collection_id: UUID,
    service: CollectionDep
):
    await service.clear_collection(collection_id)
    return {"message": f"Содержимое коллекции '{collection_id}' полностью очищено вместе с исходными файлами"}


@router.delete("/{collection_id}", summary="Удалить коллекцию и исходные файлы")
async def admin_delete_collection(
    collection_id: UUID,
    service: CollectionDep
):
    await service.delete_collection(collection_id)
    return {"message": f"Коллекция '{collection_id}' и её индексы полностью удалены"}


@router.get("/{collection_id}/documents", response_model=DocumentsResponseSchema, summary="Получить список документов из коллекции")
async def admin_get_collection_documents(
    collection_id: UUID,
    service: CollectionDep,
    pagination: PaginationDep
):
    documents, total = await service.get_documents(collection_id, pagination.size, pagination.offset)
    return {
        "items": documents,
        "total": total,
    }


@router.get("/{collection_id}/documents/{document_id}", response_model=DocumentSchema, summary="Получить документ из коллекции")
async def admin_get_collection_document(
    collection_id: UUID,
    document_id: UUID,
    service: CollectionDep
):
    return await service.get_document(collection_id, document_id)


@router.delete("/{collection_id}/documents/{document_id}", summary="Удалить документ и его исходный файл по document_id")
async def admin_delete_document(
    collection_id: UUID, 
    document_id: UUID, 
    service: CollectionDep
):
    await service.delete_document(collection_id, document_id)
    return {"message": f"Документ '{document_id}' удален из коллекции {collection_id}"}


@router.post("/{collection_id}/search", response_model=RAGResponseSchema, summary="Запрос в документацию (RAG)")
async def rag_query(collection_id: UUID, body: QuerySchema, rag_service: RAGDep, repos: DatabaseDep):
    answer = await rag_service.run(
        collection_id=collection_id,
        **body.model_dump(),
        repos=repos
    )
    return answer