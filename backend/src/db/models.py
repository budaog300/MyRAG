import enum
from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy import String, Integer, BigInteger, Text, ForeignKey, Boolean, Enum as SQLEnum
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

    name: Mapped[str] = mapped_column(String, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    size: Mapped[Optional[str]] = mapped_column(Integer, default=1024, nullable=False)
    distance: Mapped[Optional[str]] = mapped_column(String, default="COSINE", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    documents: Mapped[list["DocumentModel"]] = relationship(
        "DocumentModel",
        back_populates="collection",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    query_history: Mapped[list["QueryHistoryModel"]] = relationship(
        "QueryHistoryModel",
        back_populates="collection",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class DocumentModel(BaseEntity):
    __tablename__ = "documents"

    collection_id: Mapped[UUID] = mapped_column(ForeignKey("collections.id", ondelete="CASCADE"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    s3_key: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[DocumentStatus] = mapped_column(SQLEnum(DocumentStatus), default=DocumentStatus.PENDING, index=True, nullable=False)
    mime_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    collection: Mapped["CollectionModel"] = relationship("CollectionModel", back_populates="documents")


class QueryHistoryModel(BaseEntity):
    __tablename__ = "query_history"

    collection_id: Mapped[UUID] = mapped_column(ForeignKey("collections.id", ondelete="CASCADE"), nullable=False, index=True)
    query: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=True)
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    collection: Mapped["CollectionModel"] = relationship("CollectionModel", back_populates="query_history")