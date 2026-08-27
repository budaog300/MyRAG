from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class BaseRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def ping(self) -> bool:
        try:
            await self.session.execute(text("SELECT 1"))
            return True
        except Exception:
            return False