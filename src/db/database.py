from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import text, UUID, func
import uuid
from datetime import datetime

from src.core.config import settingsDB

DATABASE_URL = settingsDB.get_auth_data

engine = create_async_engine(
    DATABASE_URL,
    pool_size=settingsDB.DB_POOL_SIZE,
    max_overflow=settingsDB.DB_MAX_OVERFLOW,
    echo=False
)
async_session = async_sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False
)


class Base(DeclarativeBase):
    __abstract__ = True


class BaseEntity(Base):
    __abstract__ = True

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, server_default=text("gen_random_uuid()"), primary_key=True
    )
    created_at: Mapped[datetime] = mapped_column(
        default=func.now(), server_default=text("TIMEZONE('utc', now())")
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=text("TIMEZONE('utc', now())"),
        onupdate=text("TIMEZONE('utc', now())"),
    )


async def get_db():
    async with async_session() as session:
        yield session