"""Testes unitários do JWTService — criação, verificação e validação de tokens access/refresh."""

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from jose import jwt

from app.config import settings
from app.models.auth import TokenPayload
from app.services.jwt_service import JWTService


class TestJWTService:
    """Valida criação e verificação de tokens JWT — fluxo feliz, inválido e expirado."""

    def test_criar_e_verificar_access_token(self) -> None:
        usuario_id = uuid4()
        jwt_service = JWTService()
        token = jwt_service.criar_access_token(usuario_id)
        payload = jwt_service.verificar_token(token)
        assert payload.sub == usuario_id
        assert payload.tipo == "access"

    def test_criar_e_verificar_refresh_token(self) -> None:
        usuario_id = uuid4()
        jwt_service = JWTService()
        token = jwt_service.criar_refresh_token(usuario_id)
        payload = jwt_service.verificar_token(token)
        assert payload.sub == usuario_id
        assert payload.tipo == "refresh"

    def test_verificar_token_invalido_levanta_erro(self) -> None:
        jwt_service = JWTService()
        with pytest.raises(ValueError, match="Token inválido"):
            jwt_service.verificar_token("token-invalido")

    def test_verificar_token_expirado_levanta_erro(self) -> None:
        jwt_service = JWTService()
        exp_passado = int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp())
        payload = TokenPayload(sub=uuid4(), exp=exp_passado, tipo="access")
        token_expirado = jwt.encode(
            payload.model_dump(mode="json"),
            settings.secret_key,
            algorithm=settings.algorithm,
        )
        with pytest.raises(ValueError, match="Token inválido"):
            jwt_service.verificar_token(token_expirado)
