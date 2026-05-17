"""Middleware de autenticação — extrai e valida JWT do header Authorization, retorna usuário atual."""

from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.usuario import Usuario
from app.services.jwt_service import JWTService

_security = HTTPBearer(auto_error=False)
_jwt_service = JWTService()


async def get_usuario_atual(
    credentials: HTTPAuthorizationCredentials | None = Depends(_security),
    session: AsyncSession = Depends(get_session),
) -> Usuario:
    """Extrai e valida o token JWT do header Authorization, retornando o usuário autenticado.

    Uso: `usuario: Usuario = Depends(get_usuario_atual)` em rotas protegidas.
    Levanta 401 se token ausente, inválido, expirado ou se o usuário não existir.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de acesso não fornecido",
        )
    try:
        payload = _jwt_service.verificar_token(credentials.credentials)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )

    if payload.tipo != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token fornecido não é um access token",
        )

    repo = UsuarioRepository(session)
    usuario = await repo.buscar_por_id(payload.sub)
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
        )
    return usuario
