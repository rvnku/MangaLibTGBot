from datetime import datetime, UTC
from sqlalchemy import update, or_, select, insert
from src.database import async_session
from src.database.models import UserModel


class User:
    telegram_id: int

    def __init__(self, telegram_id: int) -> None:
        self.telegram_id = telegram_id

    async def create(self) -> None:
        async with async_session() as session:
            await session.execute(
                insert(UserModel)
                .prefix_with('IGNORE')
                .values(telegram_id=self.telegram_id, start_at=datetime.now(UTC))
            )
            await session.commit()

    async def login(self, id: int, token: str) -> None:
        async with async_session() as session:
            await session.execute(
                update(UserModel)
                .where(or_(UserModel.telegram_id == self.telegram_id))
                .values(id=id, token=token, login_at=datetime.now(UTC))
            )
            await session.commit()

    async def logout(self) -> None:
        async with async_session() as session:
            await session.execute(
                update(UserModel)
                .where(or_(UserModel.telegram_id == self.telegram_id))
                .values(id=None, token=None, logout_at=datetime.now(UTC))
            )
            await session.commit()

    async def get_id(self) -> int:
        async with async_session() as session:
            result = await session.execute(
                select(UserModel)
                .where(or_(UserModel.telegram_id == self.telegram_id))
            )
            return result.scalar_one_or_none().id

    async def get_token(self) -> str:
        async with async_session() as session:
            result = await session.execute(
                select(UserModel)
                .where(or_(UserModel.telegram_id == self.telegram_id))
            )
            return result.scalar_one_or_none().token
