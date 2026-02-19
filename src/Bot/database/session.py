from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from ..config import config


class Base(DeclarativeBase):
    """Базовый класс для всех ORM моделей"""
    pass

engine = create_async_engine(config.DB_URL, echo=True, future=True)

async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db():
    """Инициализация БД - создание всех таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
async def get_session() -> AsyncSession:
    """Получение сессии для работы с БД"""
    return async_session_maker()
