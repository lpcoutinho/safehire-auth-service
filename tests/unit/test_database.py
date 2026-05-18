"""Testes da camada de banco — engine, session, get_session e rollback em caso de exceção."""

from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


class TestDatabaseEngine:
    """Valida criação de engine e session factory."""

    def test_engine_echo_matches_debug(self) -> None:
        engine = create_async_engine(settings.database_url, echo=settings.debug)
        assert engine.echo == settings.debug

    def test_async_sessionmaker_cria_sessoes(self) -> None:
        engine = create_async_engine(settings.database_url, echo=False)
        factory = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        assert factory is not None


class TestGetSession:
    """Valida comportamento do get_session — rollback em caso de exceção."""

    @pytest.mark.asyncio
    async def test_rollback_em_excecao(self) -> None:
        from app.database import get_session

        mock_session = AsyncMock(spec=AsyncSession)
        mock_session.commit.side_effect = RuntimeError("erro simulado")

        mock_ctx_mgr = AsyncMock()
        mock_ctx_mgr.__aenter__.return_value = mock_session

        with patch("app.database.async_session", return_value=mock_ctx_mgr):
            gen = get_session()
            await gen.__anext__()
            with pytest.raises(RuntimeError, match="erro simulado"):
                await gen.__anext__()

        mock_session.rollback.assert_awaited_once()
        mock_session.close.assert_awaited_once()
