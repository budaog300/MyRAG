import uuid

from sqlalchemy import delete, select, update

from src.db.models import CollectionModel
from src.db.repositories.base import BaseRepository


class CollectionRepository(BaseRepository):
    async def create(
        self,
        name: str,
        size: int,
        distance: str,
        description: str | None = None,
    ) -> CollectionModel:
        collection = CollectionModel(
            name=name,
            size=size,
            distance=distance,
            description=description,
        )
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

    async def update(
        self,
        collection_id: uuid.UUID,
        name: str | None = None,
        description: str | None = None,
    ) -> CollectionModel:
        values = {}

        if name is not None:
            values["name"] = name

        if description is not None:
            values["description"] = description
        stmt = (
            update(CollectionModel)
            .where(CollectionModel.id == collection_id)
            .values(**values)
            .returning(CollectionModel)
        )
        result = await self.session.execute(stmt)
        await self.session.flush()
        return result.scalar_one_or_none()

    async def delete(
        self,
        collection: CollectionModel,
    ) -> None:
        await self.session.delete(collection)
        await self.session.flush()