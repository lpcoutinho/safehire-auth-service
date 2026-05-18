"""Testes unitários das rotas — registro, login, refresh, /me e buscar usuário com dependências mockadas."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.routes.auth import _auth_service
from app.schemas.usuario import Usuario


@pytest.mark.asyncio
async def test_register_duplicado_retorna_409() -> None:
    mock_auth = AsyncMock()
    mock_auth.registrar.side_effect = ValueError("Email já cadastrado: joao@email.com")
    app.dependency_overrides[_auth_service] = lambda: mock_auth
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/auth/register",
            json={
                "nome": "Joao",
                "email": "joao@email.com",
                "senha": "12345678",
                "tipo": "candidato",
            },
        )
    assert resp.status_code == 409
    assert "Email já cadastrado" in resp.json()["detail"]
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_invalido_retorna_401() -> None:
    mock_auth = AsyncMock()
    mock_auth.autenticar.side_effect = ValueError(
        "Credenciais inválidas para: joao@email.com"
    )
    app.dependency_overrides[_auth_service] = lambda: mock_auth
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/auth/login", json={"email": "joao@email.com", "senha": "senha_errada"}
        )
    assert resp.status_code == 401
    assert "Credenciais inválidas" in resp.json()["detail"]
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_refresh_invalido_retorna_401() -> None:
    mock_auth = AsyncMock()
    mock_auth.refresh.side_effect = ValueError("Token inválido ou expirado")
    app.dependency_overrides[_auth_service] = lambda: mock_auth
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post(
            "/auth/refresh", json={"refresh_token": "token_invalido"}
        )
    assert resp.status_code == 401
    assert "Token inválido" in resp.json()["detail"]
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_buscar_usuario_inexistente_retorna_404() -> None:
    from fastapi import HTTPException

    from app.repositories.usuario_repo import UsuarioRepository
    from app.routes.usuarios import buscar_usuario

    repo = AsyncMock(spec=UsuarioRepository)
    repo.buscar_por_id.return_value = None
    with pytest.raises(HTTPException) as exc:
        await buscar_usuario(usuario_id=uuid4(), repo=repo)
    assert exc.value.status_code == 404
    assert "Usuário não encontrado" in exc.value.detail


@pytest.mark.asyncio
async def test_atualizar_me_atualiza_nome() -> None:
    from app.models.usuario import UsuarioUpdate
    from app.routes.usuarios import atualizar_me

    user = Usuario(
        id=uuid4(), nome="Joao", email="joao@email.com", tipo="candidato", ativo=True
    )
    repo = AsyncMock()
    repo.atualizar.return_value = Usuario(
        id=user.id, nome="Joao Silva", email=user.email, tipo=user.tipo, ativo=True
    )
    result = await atualizar_me(
        data=UsuarioUpdate(nome="Joao Silva"), usuario=user, repo=repo
    )
    assert result.nome == "Joao Silva"
    repo.atualizar.assert_awaited_once()
