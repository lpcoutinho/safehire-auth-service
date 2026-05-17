"""Testes de integração do CRUD de usuários — consulta de perfil e usuários."""

import pytest


@pytest.mark.skip(reason="requer PostgreSQL — execute com docker compose up -d db")
class TestUsuarioCRUD:
    """Valida endpoints de consulta de usuários — caso de borda (não encontrado)."""

    async def test_buscar_usuario_inexistente(self, client) -> None:
        """Buscar UUID aleatório deve retornar 404."""
        from uuid import uuid4

        response = await client.get(f"/usuarios/{uuid4()}")
        assert response.status_code == 404
