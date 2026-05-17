"""Repository para operações de banco na tabela de usuários — CRUD e consultas por email/id."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.usuario import Usuario


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
        self._session.add(usuario)
        await self._session.flush()
        return usuario

    async def buscar_por_email(self, email: str) -> Usuario | None:
        """Busca usuário pelo email (coluna única indexada) — usado no login e registro.

        Uso: `await repo.buscar_por_email("fulano@example.com")`
        """
        query = select(Usuario).where(Usuario.email == email)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def buscar_por_id(self, usuario_id: UUID) -> Usuario | None:
        """Busca usuário pelo UUID primário — usado no middleware de autenticação.

        Uso: `await repo.buscar_por_id(uuid4())`
        """
        query = select(Usuario).where(Usuario.id == usuario_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def listar_ativos(self) -> list[Usuario]:
        """Lista todos os usuários com ativo=True — útil para relatórios admins.

        Uso: `ativos = await repo.listar_ativos()`
        """
        query = select(Usuario).where(Usuario.ativo.is_(True))
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def atualizar(self, usuario: Usuario) -> Usuario:
        """Persiste alterações em um usuário já existente (trackeado pelo SQLAlchemy).

        Uso: `usuario.nome = "Novo"; await repo.atualizar(usuario)`
        """
        await self._session.flush()
        return usuario
