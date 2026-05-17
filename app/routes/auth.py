"""Endpoints de autenticação — registro, login e refresh de tokens."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.models.auth import LoginRequest, RefreshRequest, TokenResponse
from app.models.usuario import UsuarioCreate, UsuarioResponse
from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.usuario import Usuario
from app.services.auth_service import AuthService
from app.services.jwt_service import JWTService

router = APIRouter()


def _auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    """Factory de AuthService com injeção de dependências — evita instanciar globais."""
    repo = UsuarioRepository(session)
    jwt_service = JWTService()
    return AuthService(repo, jwt_service)


@router.post("/register", response_model=UsuarioResponse, status_code=201)
async def register(
    data: UsuarioCreate, auth: AuthService = Depends(_auth_service)
) -> UsuarioResponse:
    """Registra novo usuário — email único, senha hash com bcrypt, retorna dados públicos.

    Uso: `POST /auth/register` com `{"nome":"Fulano","email":"f@e.com","senha":"12345678","tipo":"candidato"}`
    """
    usuario, _, _ = await auth.registrar(data)
    return UsuarioResponse.model_validate(usuario)


@router.post("/login", response_model=TokenResponse)
async def login(
    data: LoginRequest, auth: AuthService = Depends(_auth_service)
) -> TokenResponse:
    """Autentica usuário por email+senha — retorna access_token + refresh_token.

    Uso: `POST /auth/login` com `{"email":"f@e.com","senha":"12345678"}`
    """
    _, access, refresh = await auth.autenticar(data)
    return TokenResponse(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest, auth: AuthService = Depends(_auth_service)
) -> TokenResponse:
    """Renova tokens usando refresh_token — gera novo par access+refresh.

    Uso: `POST /auth/refresh` com `{"refresh_token":"eyJ..."}`
    """
    access, refresh = await auth.refresh(data.refresh_token)
    return TokenResponse(access_token=access, refresh_token=refresh)
