from uuid import UUID

from sqlalchemy import select, delete, func

from src.db.models import QueryHistoryModel
from src.db.repositories.base import BaseRepository


class QueryHistoryRepository(BaseRepository):
    async def create(
        self,
        collection_id: UUID,
        query: str,
        answer: str,
        request_id: UUID,
        response_time_ms: int | None = None
    ) -> QueryHistoryModel:
        new_query = QueryHistoryModel(
            collection_id=collection_id,
            query=query,
            answer=answer,
            request_id=request_id,
            response_time_ms=response_time_ms
        )
        self.session.add(new_query)
        await self.session.flush()
        return new_query

    async def get_by_id(
        self,
        id: UUID,
        collection_id: UUID
    ) -> QueryHistoryModel | None:
        query = select(QueryHistoryModel).where(
            QueryHistoryModel.id == id,
            QueryHistoryModel.collection_id == collection_id
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        collection_id: UUID,
        limit: int | None = None,
        offset: int = 0
    ) -> list[QueryHistoryModel]:
        query = (
            select(QueryHistoryModel)
            .where(QueryHistoryModel.collection_id == collection_id)
            .order_by(QueryHistoryModel.created_at.desc())
        )
        if limit is not None:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def count_by_collection_id(
        self,
        collection_id: UUID,
    ) -> int:
        result = await self.session.execute(
            select(func.count(QueryHistoryModel.id))
            .where(QueryHistoryModel.collection_id == collection_id)
        )
        return result.scalar_one()

    async def delete_by_collection_id(self, collection_id: UUID) -> None:
        await self.session.execute(
            delete(QueryHistoryModel).where(QueryHistoryModel.collection_id == collection_id)
        )
        
    async def delete(
        self,
        query_history: QueryHistoryModel
    ) -> None:
        await self.session.delete(query_history)