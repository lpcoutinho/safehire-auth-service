"""Schemas Pydantic para autenticação — login, tokens, refresh e payload JWT."""

from uuid import UUID

from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    """Schema de requisição de login — email + senha para autenticação.

    Uso: `POST /auth/login` com `{"email": "f@e.com", "senha": "123"}`
    """

    email: EmailStr
    senha: str


class TokenResponse(BaseModel):
    """Schema de resposta com tokens JWT — access (curta duração) + refresh (longa duração).

    Uso: retornado por `POST /auth/login` e `POST /auth/refresh`
    """

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Schema de requisição de refresh — recebe o refresh_token para gerar novo par.

    Uso: `POST /auth/refresh` com `{"refresh_token": "..."}`
    """

    refresh_token: str


class TokenPayload(BaseModel):
    """Payload interno do JWT — contém subject (UUID do usuário), exp e tipo (access|refresh).

    Uso: usado por JWTService para codificar/decodificar tokens.
    """

    sub: UUID
    exp: int
    tipo: str = "access"
