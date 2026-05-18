"""Testes para app.database — criação de engine, session factory e get_session."""

import pytest

from app.config import settings
from app.database import Base, async_session, engine, get_session


class TestDatabaseEngine:
    """Engine SQLAlchemy é criada com a URL do settings."""

    def test_engine_e_criada_com_database_url(self):
        from sqlalchemy import make_url

        url_engine = make_url(str(engine.url))
        url_settings = make_url(settings.database_url)
        assert url_engine.drivername == url_settings.drivername
        assert url_engine.host == url_settings.host
        assert url_engine.port == url_settings.port
        assert url_engine.database == url_settings.database

    def test_engine_e_instancia_de_AsyncEngine(self):
        from sqlalchemy.ext.asyncio import AsyncEngine

        assert isinstance(engine, AsyncEngine)


class TestDatabaseSession:
    """Session factory produz sessões assíncronas."""

    def test_async_session_e_async_sessionmaker(self):
        from sqlalchemy.ext.asyncio import async_sessionmaker

        assert isinstance(async_session, async_sessionmaker)

    def test_async_session_produz_async_session(self):
        from sqlalchemy.ext.asyncio import AsyncSession

        assert async_session.class_ is AsyncSession


class TestDatabaseBase:
    """Base declarativa existe para models herdarem."""

    def test_base_e_declarative_base(self):
        from sqlalchemy.orm import DeclarativeBase

        assert isinstance(Base, type)
        assert issubclass(Base, DeclarativeBase)

    def test_base_tem_metadata(self):
        assert hasattr(Base, "metadata")


class TestGetSession:
    """get_session é um async generator que yield uma sessão."""

    @pytest.mark.asyncio
    async def test_get_session_yields_async_session(self):
        from sqlalchemy.ext.asyncio import AsyncSession

        async_gen = get_session()
        session = await async_gen.__anext__()
        assert isinstance(session, AsyncSession)
        await session.close()
        try:
            await async_gen.__anext__()
        except StopAsyncIteration:
            pass
