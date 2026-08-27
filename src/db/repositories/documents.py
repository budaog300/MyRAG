import uuid

from sqlalchemy import select

from src.db.models import DocumentModel, DocumentStatus
from src.db.repositories.base import BaseRepository


class DocumentRepository(BaseRepository):
    async def create(
        self,
        collection_id: uuid.UUID,
        filename: str,
        s3_key: str,
        mime_type: str | None = None,
        size_bytes: int | None = None,
    ) -> DocumentModel:
        document = DocumentModel(
            collection_id=collection_id,
            filename=filename,
            s3_key=s3_key,
            mime_type=mime_type,
            size_bytes=size_bytes,
        )

        self.session.add(document)
        await self.session.flush()

        return document

    async def get_by_id(
        self,
        document_id: uuid.UUID,
    ) -> DocumentModel | None:
        result = await self.session.execute(
            select(DocumentModel).where(
                DocumentModel.id == document_id
            )
        )

        return result.scalar_one_or_none()

    async def get_by_s3_key(
        self,
        s3_key: str,
    ) -> DocumentModel | None:
        result = await self.session.execute(
            select(DocumentModel).where(
                DocumentModel.s3_key == s3_key
            )
        )

        return result.scalar_one_or_none()

    async def get_by_collection(
        self,
        collection_id: uuid.UUID,
    ) -> list[DocumentModel]:
        result = await self.session.execute(
            select(DocumentModel)
            .where(DocumentModel.collection_id == collection_id)
            .order_by(DocumentModel.created_at.desc())
        )

        return list(result.scalars().all())

    async def update_status(
        self,
        document_id: uuid.UUID,
        status: DocumentStatus,
        error_message: str | None = None,
    ) -> DocumentModel | None:
        document = await self.get_by_id(document_id)

        if document is None:
            return None

        document.status = status
        document.error_message = error_message

        await self.session.flush()

        return document

    async def delete(
        self,
        document: DocumentModel,
    ) -> None:
        await self.session.delete(document)
        await self.session.flush()