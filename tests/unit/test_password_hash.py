"""Testes unitários do hash de senha — verifica bcrypt via AuthService."""

from app.services.auth_service import AuthService


class TestPasswordHash:
    """Valida hash e verificação de senha com bcrypt — acerto e erro."""

    def test_hash_e_verificacao(self) -> None:
        """Senha hash deve ser diferente da original e verificar corretamente."""
        auth_service = AuthService.__new__(AuthService)
        senha = "minha-senha-segura-123"
        hashed = auth_service._hash_senha(senha)
        assert hashed != senha
        assert auth_service._verificar_senha(senha, hashed)

    def test_senha_incorreta_nao_verifica(self) -> None:
        """Senha errada não deve passar na verificação contra o hash."""
        auth_service = AuthService.__new__(AuthService)
        hashed = auth_service._hash_senha("senha-correta")
        assert not auth_service._verificar_senha("senha-errada", hashed)
