"""Testes unitários do JWTService — criação e verificação de tokens access/refresh."""

from uuid import uuid4

import pytest

from app.services.jwt_service import JWTService


class TestJWTService:
    """Valida criação e verificação de tokens JWT — fluxo feliz e token inválido."""

    def test_criar_e_verificar_access_token(self) -> None:
        """Access token criado deve ser decodificado com mesmo sub e tipo='access'."""
        usuario_id = uuid4()
        jwt_service = JWTService()
        token = jwt_service.criar_access_token(usuario_id)
        payload = jwt_service.verificar_token(token)
        assert payload.sub == usuario_id
        assert payload.tipo == "access"

    def test_criar_e_verificar_refresh_token(self) -> None:
        """Refresh token criado deve ser decodificado com mesmo sub e tipo='refresh'."""
        usuario_id = uuid4()
        jwt_service = JWTService()
        token = jwt_service.criar_refresh_token(usuario_id)
        payload = jwt_service.verificar_token(token)
        assert payload.sub == usuario_id
        assert payload.tipo == "refresh"

    def test_verificar_token_invalido_levanta_erro(self) -> None:
        """Token mal-formado deve levantar ValueError com mensagem 'Token inválido'."""
        jwt_service = JWTService()
        with pytest.raises(ValueError, match="Token inválido"):
            jwt_service.verificar_token("token-invalido")
