"""Fake de sessão de banco — utiliza dict em memória para simular operações de repositório."""

from collections.abc import AsyncGenerator
from uuid import UUID

from app.schemas.usuario import Usuario


class FakeDatabase:
    """Fake de banco PostgreSQL — armazena usuários em dict para testes sem DB real.

    Uso: `FakeDatabase().adicionar(usuario)` ou usado via FakePostgres como session.
    """

    def __init__(self) -> None:
        self._usuarios: dict[UUID, Usuario] = {}

    def adicionar(self, usuario: Usuario) -> None:
        """Adiciona usuário ao cache — simula INSERT com chave primária UUID."""
        self._usuarios[usuario.id] = usuario

    def buscar_por_id(self, usuario_id: UUID) -> Usuario | None:
        """Retorna usuário por UUID — simula `SELECT WHERE id = :id`."""
        return self._usuarios.get(usuario_id)

    def buscar_por_email(self, email: str) -> Usuario | None:
        """Retorna usuário por email — simula `SELECT WHERE email = :email`."""
        for u in self._usuarios.values():
            if u.email == email:
                return u
        return None

    def todos(self) -> list[Usuario]:
        """Retorna todos os usuários — simula `SELECT * FROM usuarios`."""
        return list(self._usuarios.values())

    def limpar(self) -> None:
        """Remove todos os usuários — usado no setup/teardown entre testes."""
        self._usuarios.clear()
