"""Schemas Pydantic para domínio de usuário — criação, resposta, atualização e enum de tipo."""

from datetime import datetime
from enum import Enum
from typing import ClassVar
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class TipoUsuario(str, Enum):
    """Enum de tipos de usuário do sistema — usado no cadastro e nas responses.

    Uso: `TipoUsuario.candidato` ou `TipoUsuario.recrutador`
    """

    recrutador = "recrutador"
    candidato = "candidato"


class UsuarioCreate(BaseModel):
    """Schema de criação de usuário — valida nome, email, senha (min 8 chars) e tipo.

    Uso: `UsuarioCreate(nome="Fulano", email="f@e.com", senha="12345678", tipo=TipoUsuario.candidato)`
    """

    nome: str
    email: EmailStr
    senha: str
    tipo: TipoUsuario

    @field_validator("senha")
    @classmethod
    def senha_deve_ter_no_minimo_8_caracteres(cls, v: str) -> str:
        """Valida que a senha tem ao menos 8 caracteres — requisito de segurança mínimo.

        Uso: chamado automaticamente pelo Pydantic ao instanciar UsuarioCreate.
        """
        if len(v) < 8:
            raise ValueError("senha deve ter no mínimo 8 caracteres")
        return v


class UsuarioResponse(BaseModel):
    """Schema de resposta pública de usuário — expõe dados sem a senha hash.

    Uso: usado como `response_model` nos endpoints GET/PUT de usuário.
    """

    id: UUID
    nome: str
    email: EmailStr
    tipo: TipoUsuario
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class UsuarioUpdate(BaseModel):
    """Schema de atualização de usuário — todos os campos opcionais para PATCH semântico.

    Uso: `UsuarioUpdate(nome="Novo Nome")` ou `UsuarioUpdate(email="novo@e.com")`
    """

    nome: str | None = None
    email: EmailStr | None = None
    senha: str | None = None
