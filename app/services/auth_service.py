"""Serviço de autenticação — registro, login, refresh e hash de senha com bcrypt."""

from uuid import UUID

from passlib.context import CryptContext

from app.models.auth import LoginRequest
from app.models.usuario import UsuarioCreate
from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.usuario import Usuario
from app.services.jwt_service import JWTService

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Serviço central de autenticação — orquestra repositório, hash de senha e emissão de JWT.

    Uso: `AuthService(repo, jwt_service).registrar(create_data)`
    """

    def __init__(self, repo: UsuarioRepository, jwt_service: JWTService):
        self._repo = repo
        self._jwt = jwt_service

    async def registrar(self, data: UsuarioCreate) -> tuple[Usuario, str, str]:
        """Registra novo usuário: valida unicidade de email, hasheia senha e retorna par de tokens.

        Uso: `usuario, access, refresh = await auth.registrar(create_data)`
        """
        ja_existe = await self._repo.buscar_por_email(data.email)
        if ja_existe:
            raise ValueError(f"Email já cadastrado: {data.email}")

        usuario = Usuario(
            nome=data.nome,
            email=data.email,
            senha_hash=self._hash_senha(data.senha),
            tipo=data.tipo,
        )
        usuario = await self._repo.criar(usuario)
        access = self._jwt.criar_access_token(usuario.id)
        refresh = self._jwt.criar_refresh_token(usuario.id)
        return usuario, access, refresh

    async def autenticar(self, data: LoginRequest) -> tuple[Usuario, str, str]:
        """Autentica usuário por email+senha: verifica credenciais e retorna par de tokens.

        Uso: `usuario, access, refresh = await auth.autenticar(login_data)`
        """
        usuario = await self._repo.buscar_por_email(data.email)
        if not usuario:
            raise ValueError(f"Credenciais inválidas para: {data.email}")
        if not self._verificar_senha(data.senha, usuario.senha_hash):
            raise ValueError(f"Credenciais inválidas para: {data.email}")

        access = self._jwt.criar_access_token(usuario.id)
        refresh = self._jwt.criar_refresh_token(usuario.id)
        return usuario, access, refresh

    async def refresh(self, refresh_token: str) -> tuple[str, str]:
        """Gera novo par de tokens a partir de um refresh token válido — usado para renovação.

        Uso: `access, refresh = await auth.refresh("eyJ...")`
        """
        payload = self._jwt.verificar_token(refresh_token)
        if payload.tipo != "refresh":
            raise ValueError("Token fornecido não é um refresh token")
        usuario = await self._repo.buscar_por_id(payload.sub)
        if not usuario:
            raise ValueError(f"Usuário não encontrado: {payload.sub}")
        access = self._jwt.criar_access_token(usuario.id)
        refresh = self._jwt.criar_refresh_token(usuario.id)
        return access, refresh

    async def buscar_usuario(self, usuario_id: UUID) -> Usuario:
        """Busca usuário por ID — usado internamente quando apenas o ID está disponível.

        Uso: `usuario = await auth.buscar_usuario(uuid4())`
        """
        usuario = await self._repo.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError(f"Usuário não encontrado: {usuario_id}")
        return usuario

    def _hash_senha(self, senha: str) -> str:
        """Aplica bcrypt hash em senha pura — usado no registro antes de persistir."""
        hashed: str = _pwd_context.hash(senha)
        return hashed

    def _verificar_senha(self, senha: str, senha_hash: str) -> bool:
        """Compara senha pura com hash armazenado — usado no login."""
        valido: bool = _pwd_context.verify(senha, senha_hash)
        return valido
