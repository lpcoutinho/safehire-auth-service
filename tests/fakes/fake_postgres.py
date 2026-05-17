"""Fake de engine PostgreSQL — retorna sessões que operam sobre FakeDatabase em memória."""

from collections.abc import AsyncGenerator
from uuid import UUID

from app.schemas.usuario import Usuario
from tests.fakes.fake_database import FakeDatabase


class FakePostgres:
    """Fake de engine assíncrona PostgreSQL — fornece FakeDatabase como sessão.

    Uso: `async for session in FakePostgres().get_session(): ...`
    """

    def __init__(self) -> None:
        self._db = FakeDatabase()

    async def get_session(self) -> AsyncGenerator[FakeDatabase, None]:
        """Retorna FakeDatabase como sessão — compatível com async generator de get_session()."""
        yield self._db
