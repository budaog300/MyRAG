# src/db/models/document.py
import enum
import uuid
from typing import Optional
from sqlalchemy import String, BigInteger, Text, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.database import BaseEntity


class DocumentStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"
    DELETING = "deleting"


class CollectionModel(BaseEntity):
    __tablename__ = "collections"

    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    documents: Mapped[list["DocumentModel"]] = relationship(back_populates="collection")


class DocumentModel(BaseEntity):
    __tablename__ = "documents"

    collection_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("collections.id"), index=True, nullable=False)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    s3_key: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING, index=True, nullable=False)
    mime_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    collection: Mapped["CollectionModel"] = relationship(back_populates="documents")
