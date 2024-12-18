from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker

from src.database.models import Base
from src.utils.config import config

import logging


logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)


DATABASE_URL = f'mysql+aiomysql://{config.db_user}:{config.db_pass}@{config.db_host}:{config.db_port}/{config.db_name}'

engine: AsyncEngine = create_async_engine(DATABASE_URL, future=True)
async_session: async_sessionmaker[AsyncSession] = async_sessionmaker(engine, expire_on_commit=False)


async def init_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
