"""Repository para operações de banco na tabela de usuários — CRUD e consultas por email/id."""

from __future__ import annotations

import logging
import time
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.usuario import Usuario

logger = logging.getLogger(__name__)


class UsuarioRepository:
    """Repository de usuários — abstrai consultas SQLAlchemy na tabela auth_schema.usuarios.

    Uso: `UsuarioRepository(session).buscar_por_email("f@e.com")`
    """

    def __init__(self, session: AsyncSession):
        self._session = session

    async def criar(self, usuario: Usuario) -> Usuario:
        """Persiste um novo usuário no banco e retorna a instância com id populado.

        Uso: `await repo.criar(usuario_orm)`
        """
        start = time.monotonic()
        self._session.add(usuario)
        await self._session.flush()
        elapsed = time.monotonic() - start
        logger.info(
            "DB criar id=%s email=%s duracao=%.3fs", usuario.id, usuario.email, elapsed
        )
        return usuario

    async def buscar_por_email(self, email: str) -> Usuario | None:
        """Busca usuário pelo email (coluna única indexada) — usado no login e registro.

        Uso: `await repo.buscar_por_email("fulano@example.com")`
        """
        start = time.monotonic()
        query = select(Usuario).where(Usuario.email == email)
        result = await self._session.execute(query)
        usuario = result.scalar_one_or_none()
        elapsed = time.monotonic() - start
        encontrado = "encontrado" if usuario else "inexistente"
        logger.info(
            "DB buscar_por_email email=%s resultado=%s duracao=%.3fs",
            email,
            encontrado,
            elapsed,
        )
        return usuario

    async def buscar_por_id(self, usuario_id: UUID) -> Usuario | None:
        """Busca usuário pelo UUID primário — usado no middleware de autenticação.

        Uso: `await repo.buscar_por_id(uuid4())`
        """
        start = time.monotonic()
        query = select(Usuario).where(Usuario.id == usuario_id)
        result = await self._session.execute(query)
        usuario = result.scalar_one_or_none()
        elapsed = time.monotonic() - start
        encontrado = "encontrado" if usuario else "inexistente"
        logger.info(
            "DB buscar_por_id id=%s resultado=%s duracao=%.3fs",
            usuario_id,
            encontrado,
            elapsed,
        )
        return usuario

    async def listar_ativos(self) -> list[Usuario]:
        """Lista todos os usuários com ativo=True — útil para relatórios admins.

        Uso: `ativos = await repo.listar_ativos()`
        """
        start = time.monotonic()
        query = select(Usuario).where(Usuario.ativo.is_(True))
        result = await self._session.execute(query)
        usuarios = list(result.scalars().all())
        elapsed = time.monotonic() - start
        logger.info("DB listar_ativos total=%d duracao=%.3fs", len(usuarios), elapsed)
        return usuarios

    async def atualizar(self, usuario: Usuario) -> Usuario:
        """Persiste alterações em um usuário já existente (trackeado pelo SQLAlchemy).

        Uso: `usuario.nome = "Novo"; await repo.atualizar(usuario)`
        """
        start = time.monotonic()
        await self._session.flush()
        elapsed = time.monotonic() - start
        logger.info(
            "DB atualizar id=%s email=%s duracao=%.3fs",
            usuario.id,
            usuario.email,
            elapsed,
        )
        return usuario
