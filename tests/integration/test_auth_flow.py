"""Testes de integração do fluxo de autenticação — registro, login e refresh com SQLite in-memory."""

from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_session
from app.main import app
from app.schemas.usuario import Usuario


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    Usuario.__table__.schema = None
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def _get_session_override() -> AsyncGenerator[AsyncSession, None]:
        async with factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_session] = _get_session_override
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
    await engine.dispose()


@pytest.mark.asyncio
class TestAuthFlow:
    async def test_registro_retorna_201_com_usuario(self, client: AsyncClient) -> None:
        data = {
            "nome": "Fulano",
            "email": "fulano@example.com",
            "senha": "12345678",
            "tipo": "candidato",
        }
        response = await client.post("/auth/register", json=data)
        assert response.status_code == 201
        assert response.json()["email"] == "fulano@example.com"

    async def test_registro_email_duplicado_retorna_409(
        self, client: AsyncClient
    ) -> None:
        data = {
            "nome": "Fulano",
            "email": "dup@example.com",
            "senha": "12345678",
            "tipo": "candidato",
        }
        await client.post("/auth/register", json=data)
        response = await client.post("/auth/register", json=data)
        assert response.status_code == 409
        assert "dup@example.com" in response.json()["detail"]

    async def test_registro_senha_curta_retorna_422(self, client: AsyncClient) -> None:
        data = {
            "nome": "Fulano",
            "email": "fulano@example.com",
            "senha": "123",
            "tipo": "candidato",
        }
        response = await client.post("/auth/register", json=data)
        assert response.status_code == 422

    async def test_login_retorna_200_com_tokens(self, client: AsyncClient) -> None:
        await client.post(
            "/auth/register",
            json={
                "nome": "Fulano",
                "email": "fulano@example.com",
                "senha": "12345678",
                "tipo": "candidato",
            },
        )
        response = await client.post(
            "/auth/login", json={"email": "fulano@example.com", "senha": "12345678"}
        )
        assert response.status_code == 200
        tokens = response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens

    async def test_login_senha_errada_retorna_401(self, client: AsyncClient) -> None:
        await client.post(
            "/auth/register",
            json={
                "nome": "Fulano",
                "email": "fulano@example.com",
                "senha": "12345678",
                "tipo": "candidato",
            },
        )
        response = await client.post(
            "/auth/login", json={"email": "fulano@example.com", "senha": "senha-errada"}
        )
        assert response.status_code == 401

    async def test_refresh_retorna_200_com_novo_par(self, client: AsyncClient) -> None:
        await client.post(
            "/auth/register",
            json={
                "nome": "Fulano",
                "email": "fulano@example.com",
                "senha": "12345678",
                "tipo": "candidato",
            },
        )
        login_resp = await client.post(
            "/auth/login", json={"email": "fulano@example.com", "senha": "12345678"}
        )
        refresh_token = login_resp.json()["refresh_token"]
        response = await client.post(
            "/auth/refresh", json={"refresh_token": refresh_token}
        )
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "refresh_token" in response.json()

    async def test_refresh_token_invalido_retorna_401(
        self, client: AsyncClient
    ) -> None:
        response = await client.post(
            "/auth/refresh", json={"refresh_token": "token-invalido"}
        )
        assert response.status_code == 401
