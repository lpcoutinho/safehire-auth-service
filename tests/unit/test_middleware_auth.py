"""Testes do middleware de autenticação — get_usuario_atual com token ausente, inválido e refresh."""

from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.middleware.auth import get_usuario_atual
from app.services.jwt_service import JWTService


class TestGetUsuarioAtual:
    """Valida comportamento do middleware de autenticação — 401 em cada cenário de erro."""

    async def test_sem_token_levanta_401(self) -> None:
        with pytest.raises(HTTPException) as exc:
            await get_usuario_atual(credentials=None, session=None)  # type: ignore[arg-type]
        assert exc.value.status_code == 401
        assert "Token de acesso não fornecido" in exc.value.detail

    async def test_token_invalido_levanta_401(self) -> None:
        from unittest.mock import AsyncMock

        from fastapi.security import HTTPAuthorizationCredentials

        creds = HTTPAuthorizationCredentials(
            scheme="Bearer", credentials="token-invalido"
        )
        with pytest.raises(HTTPException) as exc:
            await get_usuario_atual(credentials=creds, session=AsyncMock())
        assert exc.value.status_code == 401
        assert "Token inválido" in exc.value.detail

    async def test_token_de_refresh_levanta_401(self) -> None:
        from unittest.mock import AsyncMock

        from fastapi.security import HTTPAuthorizationCredentials

        jwt_service = JWTService()
        refresh_token = jwt_service.criar_refresh_token(uuid4())
        creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=refresh_token)
        with pytest.raises(HTTPException) as exc:
            await get_usuario_atual(credentials=creds, session=AsyncMock())
        assert exc.value.status_code == 401
        assert "Token fornecido não é um access token" in exc.value.detail
