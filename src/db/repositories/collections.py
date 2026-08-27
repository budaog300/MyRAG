import uuid

from sqlalchemy import delete, select

from src.db.models import CollectionModel
from src.db.repositories.base import BaseRepository


class CollectionRepository(BaseRepository):
    async def create(self, name: str) -> CollectionModel:
        collection = CollectionModel(name=name)

        self.session.add(collection)
        await self.session.flush()

        return collection

    async def get_by_id(
        self,
        collection_id: uuid.UUID,
    ) -> CollectionModel | None:
        result = await self.session.execute(
            select(CollectionModel).where(
                CollectionModel.id == collection_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_name(
        self,
        name: str,
    ) -> CollectionModel | None:
        result = await self.session.execute(
            select(CollectionModel).where(
                CollectionModel.name == name
            )
        )

        return result.scalar_one_or_none()

    async def get_all(self) -> list[CollectionModel]:
        result = await self.session.execute(
            select(CollectionModel).order_by(
                CollectionModel.created_at.desc()
            )
        )

        return list(result.scalars().all())

    async def delete(
        self,
        collection: CollectionModel,
    ) -> None:
        await self.session.delete(collection)
        await self.session.flush()