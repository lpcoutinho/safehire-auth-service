"""Endpoints de usuário — consulta e atualização do perfil do usuário autenticado."""

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_session
from app.middleware.auth import get_usuario_atual
from app.models.usuario import UsuarioResponse, UsuarioUpdate
from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.usuario import Usuario

router = APIRouter()


def _repo(session: AsyncSession = Depends(get_session)) -> UsuarioRepository:
    """Factory de UsuarioRepository — evita instanciar repositório diretamente nas rotas."""
    return UsuarioRepository(session)


@router.get("/me", response_model=UsuarioResponse)
async def me(usuario: Usuario = Depends(get_usuario_atual)) -> Usuario:
    """Retorna perfil do usuário autenticado — requer token Bearer no header.

    Uso: `GET /usuarios/me` com `Authorization: Bearer <access_token>`
    """
    return usuario


@router.put("/me", response_model=UsuarioResponse)
async def atualizar_me(
    data: UsuarioUpdate,
    usuario: Usuario = Depends(get_usuario_atual),
    repo: UsuarioRepository = Depends(_repo),
) -> Usuario:
    """Atualiza dados do perfil do usuário autenticado (nome, email, senha).

    Uso: `PUT /usuarios/me` com `Authorization: Bearer <token>` e `{"nome":"Novo Nome"}`
    """
    if data.nome is not None:
        usuario.nome = data.nome
    if data.email is not None:
        usuario.email = data.email
    usuario = await repo.atualizar(usuario)
    return usuario


@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def buscar_usuario(
    usuario_id: UUID,
    repo: UsuarioRepository = Depends(_repo),
) -> Usuario | None:
    """Busca usuário por ID público — retorna 404 se não encontrado.

    Uso: `GET /usuarios/<uuid>`
    """
    usuario = await repo.buscar_por_id(usuario_id)
    if not usuario:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=404, detail=f"Usuário não encontrado: {usuario_id}"
        )
    return usuario
