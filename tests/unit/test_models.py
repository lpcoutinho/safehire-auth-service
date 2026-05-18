"""Testes unitários dos modelos Pydantic — validação de campos, serialização e regras de negócio."""

from uuid import UUID, uuid4

import pytest
from pydantic import ValidationError

from app.models.auth import LoginRequest, RefreshRequest, TokenPayload, TokenResponse
from app.models.usuario import (
    TipoUsuario,
    UsuarioCreate,
    UsuarioResponse,
    UsuarioUpdate,
)


class TestUsuarioCreate:
    """Valida regras de negócio do schema UsuarioCreate — senha mínima, email, tipo."""

    def test_senha_com_menos_de_8_caracteres_e_invalida(self) -> None:
        with pytest.raises(ValidationError):
            UsuarioCreate(
                nome="Fulano",
                email="fulano@example.com",
                senha="1234567",
                tipo=TipoUsuario.candidato,
            )

    def test_senha_com_8_caracteres_e_valida(self) -> None:
        usuario = UsuarioCreate(
            nome="Fulano",
            email="fulano@example.com",
            senha="12345678",
            tipo=TipoUsuario.candidato,
        )
        assert usuario.senha == "12345678"

    def test_email_invalido_levanta_erro(self) -> None:
        with pytest.raises(ValidationError):
            UsuarioCreate(
                nome="Fulano",
                email="email-invalido",
                senha="12345678",
                tipo=TipoUsuario.candidato,
            )

    def test_tipo_invalido_levanta_erro(self) -> None:
        with pytest.raises(ValidationError):
            UsuarioCreate(
                nome="Fulano",
                email="fulano@example.com",
                senha="12345678",
                tipo="admin",
            )


class TestUsuarioResponse:
    """Serialização from_attributes e campos obrigatórios."""

    def test_from_attributes_com_dados_validos(self) -> None:
        usuario_id = uuid4()
        data = {
            "id": usuario_id,
            "nome": "Fulano",
            "email": "fulano@example.com",
            "tipo": TipoUsuario.candidato,
            "ativo": True,
            "criado_em": "2024-01-01T00:00:00Z",
            "atualizado_em": "2024-01-01T00:00:00Z",
        }
        response = UsuarioResponse(**data)
        assert response.id == usuario_id
        assert response.nome == "Fulano"
        assert response.ativo is True
        assert response.tipo == TipoUsuario.candidato

    def test_campos_obrigatorios_faltando_levanta_erro(self) -> None:
        with pytest.raises(ValidationError):
            UsuarioResponse()


class TestUsuarioUpdate:
    """Campos opcionais para PATCH semântico."""

    def test_todos_os_campos_sao_opcionais(self) -> None:
        update = UsuarioUpdate()
        assert update.nome is None
        assert update.email is None
        assert update.senha is None

    def test_apenas_nome_e_enviado(self) -> None:
        update = UsuarioUpdate(nome="Novo Nome")
        assert update.nome == "Novo Nome"
        assert update.email is None
        assert update.senha is None

    def test_email_invalido_no_update_levanta_erro(self) -> None:
        with pytest.raises(ValidationError):
            UsuarioUpdate(email="invalido")


class TestLoginRequest:
    """Valida email no login."""

    def test_email_valido_e_aceito(self) -> None:
        req = LoginRequest(email="fulano@example.com", senha="12345678")
        assert req.email == "fulano@example.com"

    def test_email_invalido_levanta_erro(self) -> None:
        with pytest.raises(ValidationError):
            LoginRequest(email="invalido", senha="12345678")


class TestTokenResponse:
    """Campos obrigatórios do response de tokens."""

    def test_campos_obrigatorios_preenchidos(self) -> None:
        resp = TokenResponse(access_token="abc", refresh_token="def")
        assert resp.access_token == "abc"
        assert resp.refresh_token == "def"
        assert resp.token_type == "bearer"

    def test_access_token_faltando_levanta_erro(self) -> None:
        with pytest.raises(ValidationError):
            TokenResponse(refresh_token="def")

    def test_refresh_token_faltando_levanta_erro(self) -> None:
        with pytest.raises(ValidationError):
            TokenResponse(access_token="abc")


class TestRefreshRequest:
    """Token de refresh não pode ser vazio."""

    def test_token_preenchido_e_aceito(self) -> None:
        req = RefreshRequest(refresh_token="meu-token-valido")
        assert req.refresh_token == "meu-token-valido"

    def test_token_vazio_e_aceito(self) -> None:
        req = RefreshRequest(refresh_token="")
        assert req.refresh_token == ""


class TestTokenPayload:
    """Construção do payload JWT interno."""

    def test_construcao_a_partir_de_dict(self) -> None:
        usuario_id = uuid4()
        payload = TokenPayload(sub=usuario_id, exp=1234567890, tipo="access")
        assert payload.sub == usuario_id
        assert payload.exp == 1234567890
        assert payload.tipo == "access"

    def test_tipo_padrao_e_access(self) -> None:
        payload = TokenPayload(sub=uuid4(), exp=1234567890)
        assert payload.tipo == "access"

    def test_sub_uuid_invalido_levanta_erro(self) -> None:
        with pytest.raises(ValidationError):
            TokenPayload(sub="invalido", exp=1234567890)
