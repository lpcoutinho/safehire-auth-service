"""Testes unitários dos modelos Pydantic — validação de campos e regras de negócio."""

import pytest
from pydantic import ValidationError

from app.models.usuario import TipoUsuario, UsuarioCreate


class TestUsuarioCreate:
    """Valida regras de negócio do schema UsuarioCreate — senha mínima e email válido."""

    def test_senha_com_menos_de_8_caracteres_e_invalida(self) -> None:
        """Senha com 7 caracteres deve levantar ValidationError."""
        with pytest.raises(ValidationError):
            UsuarioCreate(
                nome="Fulano",
                email="fulano@example.com",
                senha="1234567",
                tipo=TipoUsuario.candidato,
            )

    def test_senha_com_8_caracteres_e_valida(self) -> None:
        """Senha com exatos 8 caracteres deve ser aceita."""
        usuario = UsuarioCreate(
            nome="Fulano",
            email="fulano@example.com",
            senha="12345678",
            tipo=TipoUsuario.candidato,
        )
        assert usuario.senha == "12345678"

    def test_email_invalido_levanta_erro(self) -> None:
        """Email sem formato válido deve levantar ValidationError."""
        with pytest.raises(ValidationError):
            UsuarioCreate(
                nome="Fulano",
                email="email-invalido",
                senha="12345678",
                tipo=TipoUsuario.candidato,
            )
