"""Testes de integração do fluxo de autenticação — registro, login e refresh."""

import pytest


@pytest.mark.skip(reason="requer PostgreSQL — execute com docker compose up -d db")
class TestAuthFlow:
    """Valida fluxo completo de autenticação via HTTP — registro, login e email duplicado."""

    async def test_registro_e_login(self, client) -> None:
        """Registro deve retornar 201 com dados do usuário; login deve retornar tokens."""
        registro_data = {
            "nome": "Fulano",
            "email": "fulano@example.com",
            "senha": "12345678",
            "tipo": "candidato",
        }
        response = await client.post("/auth/register", json=registro_data)
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "fulano@example.com"
        assert "id" in data

        login_data = {"email": "fulano@example.com", "senha": "12345678"}
        response = await client.post("/auth/login", json=login_data)
        assert response.status_code == 200
        tokens = response.json()
        assert "access_token" in tokens
        assert "refresh_token" in tokens

    async def test_registro_com_email_duplicado(self, client) -> None:
        """Registrar com email já existente deve retornar erro 500."""
        data = {
            "nome": "Fulano",
            "email": "duplicado@example.com",
            "senha": "12345678",
            "tipo": "candidato",
        }
        await client.post("/auth/register", json=data)
        response = await client.post("/auth/register", json=data)
        assert response.status_code == 500
