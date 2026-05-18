"""Testes do AuthService — registro, autenticação, refresh e busca de usuário com FakeRepository."""

from uuid import UUID, uuid4

import pytest

from app.models.auth import LoginRequest
from app.models.usuario import TipoUsuario, UsuarioCreate
from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.usuario import Usuario
from app.services.auth_service import AuthService
from app.services.jwt_service import JWTService


class FakeRepository:
    """Implementação em memória de UsuarioRepository — evita banco real nos testes."""

    def __init__(self) -> None:
        self._usuarios: dict[UUID, Usuario] = {}

    async def criar(self, usuario: Usuario) -> Usuario:
        usuario.id = usuario.id or uuid4()
        self._usuarios[usuario.id] = usuario
        return usuario

    async def buscar_por_email(self, email: str) -> Usuario | None:
        for u in self._usuarios.values():
            if u.email == email:
                return u
        return None

    async def buscar_por_id(self, usuario_id: UUID) -> Usuario | None:
        return self._usuarios.get(usuario_id)


@pytest.fixture
def auth_service() -> AuthService:
    repo = FakeRepository()
    jwt_service = JWTService()
    return AuthService(repo, jwt_service)


class TestAuthServiceRegistrar:
    """registrar cria usuário e retorna tokens."""

    @pytest.mark.asyncio
    async def test_registra_usuario_e_retorna_tokens(
        self, auth_service: AuthService
    ) -> None:
        data = UsuarioCreate(
            nome="Fulano",
            email="fulano@example.com",
            senha="12345678",
            tipo=TipoUsuario.candidato,
        )
        usuario, access, refresh = await auth_service.registrar(data)
        assert usuario.nome == "Fulano"
        assert usuario.email == "fulano@example.com"
        assert len(access) > 0
        assert len(refresh) > 0

    @pytest.mark.asyncio
    async def test_email_duplicado_levanta_erro(
        self, auth_service: AuthService
    ) -> None:
        data = UsuarioCreate(
            nome="Fulano",
            email="dup@example.com",
            senha="12345678",
            tipo=TipoUsuario.candidato,
        )
        await auth_service.registrar(data)
        with pytest.raises(ValueError, match="Email já cadastrado: dup@example.com"):
            await auth_service.registrar(data)


class TestAuthServiceAutenticar:
    """autenticar valida credenciais e retorna tokens."""

    @pytest.mark.asyncio
    async def test_autentica_com_credenciais_validas(
        self, auth_service: AuthService
    ) -> None:
        await auth_service.registrar(
            UsuarioCreate(
                nome="Fulano",
                email="fulano@example.com",
                senha="12345678",
                tipo=TipoUsuario.candidato,
            )
        )
        login = LoginRequest(email="fulano@example.com", senha="12345678")
        usuario, access, refresh = await auth_service.autenticar(login)
        assert usuario.email == "fulano@example.com"
        assert len(access) > 0

    @pytest.mark.asyncio
    async def test_senha_errada_levanta_erro(self, auth_service: AuthService) -> None:
        await auth_service.registrar(
            UsuarioCreate(
                nome="Fulano",
                email="fulano@example.com",
                senha="12345678",
                tipo=TipoUsuario.candidato,
            )
        )
        login = LoginRequest(email="fulano@example.com", senha="senha-errada")
        with pytest.raises(
            ValueError, match="Credenciais inválidas para: fulano@example.com"
        ):
            await auth_service.autenticar(login)

    @pytest.mark.asyncio
    async def test_email_inexistente_levanta_erro(
        self, auth_service: AuthService
    ) -> None:
        login = LoginRequest(email="nao-existe@example.com", senha="12345678")
        with pytest.raises(
            ValueError, match="Credenciais inválidas para: nao-existe@example.com"
        ):
            await auth_service.autenticar(login)


class TestAuthServiceRefresh:
    """refresh gera novo par de tokens a partir de refresh token válido."""

    @pytest.mark.asyncio
    async def test_refresh_com_token_valido_retorna_novo_par(
        self, auth_service: AuthService
    ) -> None:
        data = UsuarioCreate(
            nome="Fulano",
            email="fulano@example.com",
            senha="12345678",
            tipo=TipoUsuario.candidato,
        )
        _, _, refresh_token = await auth_service.registrar(data)
        new_access, new_refresh = await auth_service.refresh(refresh_token)
        assert len(new_access) > 0
        assert len(new_refresh) > 0

    @pytest.mark.asyncio
    async def test_refresh_com_access_token_levanta_erro(
        self, auth_service: AuthService
    ) -> None:
        data = UsuarioCreate(
            nome="Fulano",
            email="fulano@example.com",
            senha="12345678",
            tipo=TipoUsuario.candidato,
        )
        _, access_token, _ = await auth_service.registrar(data)
        with pytest.raises(ValueError, match="Token fornecido não é um refresh token"):
            await auth_service.refresh(access_token)


class TestAuthServiceBuscarUsuario:
    """buscar_usuario retorna usuário ou levanta erro."""

    @pytest.mark.asyncio
    async def test_busca_usuario_por_id_existente(
        self, auth_service: AuthService
    ) -> None:
        data = UsuarioCreate(
            nome="Fulano",
            email="fulano@example.com",
            senha="12345678",
            tipo=TipoUsuario.candidato,
        )
        usuario, _, _ = await auth_service.registrar(data)
        encontrado = await auth_service.buscar_usuario(usuario.id)
        assert encontrado.id == usuario.id

    @pytest.mark.asyncio
    async def test_busca_usuario_id_inexistente_levanta_erro(
        self, auth_service: AuthService
    ) -> None:
        with pytest.raises(ValueError, match="Usuário não encontrado"):
            await auth_service.buscar_usuario(uuid4())
