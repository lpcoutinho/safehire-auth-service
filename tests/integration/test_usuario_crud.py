"""Testes de integração do CRUD de usuários — consulta de perfil e usuários com SQLite in-memory."""

from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_session
from app.main import app
from app.schemas.usuario import Usuario


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    """AsyncClient com SQLite in-memory — sobrescreve get_session para evitar PostgreSQL."""
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    Usuario.__table__.schema = None
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def _get_session_override() -> AsyncSession:
        async with factory() as session:
            yield session

    app.dependency_overrides[get_session] = _get_session_override

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
class TestUsuarioCRUD:
    """Valida endpoints de consulta de usuários — perfil autenticado e busca por ID."""

    async def test_me_sem_token_retorna_401(self, client: AsyncClient) -> None:
        response = await client.get("/usuarios/me")
        assert response.status_code == 401
        assert "Token" in response.json()["detail"]

    async def test_buscar_usuario_inexistente_retorna_404(
        self, client: AsyncClient
    ) -> None:
        response = await client.get(f"/usuarios/{uuid4()}")
        assert response.status_code == 404
        assert "Usuário não encontrado" in response.json()["detail"]
