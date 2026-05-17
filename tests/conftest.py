"""Fixtures globais do pytest — cliente HTTP fake e factory de usuário para testes."""

from collections.abc import AsyncGenerator
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.usuario import TipoUsuario
from app.schemas.usuario import Usuario


@pytest.fixture
def usuario_fake() -> Usuario:
    """Retorna instância de Usuario ORM com dados válidos — útil para testes de repositório e serviço.

    Uso: `usuario = usuario_fake()` — senha hash pré-computada de "minha-senha-segura-123".
    """
    return Usuario(
        id=uuid4(),
        nome="Fulano",
        email="fulano@example.com",
        senha_hash="$2b$12$LJ3m4ys3Lk0TSwHnbfOMiOXPm1QjqO6qZGjqIjK9k3S8Z5p3bqLQq",
        tipo=TipoUsuario.candidato,
        ativo=True,
    )


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """AsyncClient do httpx apontando para app.main:app — testa endpoints sem servidor real.

    Uso: `response = await client.post("/auth/register", json={...})`
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
