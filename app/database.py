"""Conexão PostgreSQL assíncrona via SQLAlchemy — engine, session factory e get_session dependency."""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Classe base declarativa para models SQLAlchemy — todos os ORM models herdam daqui."""

    pass


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Fornece uma sessão assíncrona com commit/rollback automático por request.

    Uso: `session: AsyncSession = Depends(get_session)` em rotas FastAPI.
    """
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
