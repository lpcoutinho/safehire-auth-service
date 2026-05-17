# Fase 5: Camada de Services

Execute este prompt para implementar a **Fase 5** do Auth Service.

## Pré-condições (obrigatório)
Antes de executar qualquer ação, considere documentação e regras em:
- `docs/2-principios-norteadores.md`
- `docs/3-arquitetura.md`
- `plans/3-validacao.md`

## Objetivo
Implementar lógica de negócio: JWT operations e autenticação.

## Regras
- **TEST-FIRST**: teste antes do código
- **Anti-Corruption Layer**: `JWTService` encapsula `python-jose`; `AuthService` encapsula `passlib`
- **Idempotência**: registrar com email duplicado retorna erro; refresh com mesmo token produz novo par
- **Mensagens de erro**: incluir valor ofensivo (ex: email duplicado)

## Tarefas

### 1. [TEST] tests/unit/test_jwt_service.py (escrever PRIMEIRO)
Testes para `JWTService`:
- `criar_access_token(usuario_id)`: retorna string JWT válida
- `criar_refresh_token(usuario_id)`: retorna string JWT com tipo "refresh"
- `verificar_token(token)`: retorna TokenPayload com sub e tipo corretos
- `verificar_token(token_invalido)`: levanta ValueError com mensagem descritiva
- `verificar_token(token_expirado)`: levanta ValueError

### 2. app/services/jwt_service.py
```python
"""Operações JWT encapsulando python-jose.
Anti-Corruption Layer: se a biblioteca mudar, só este arquivo muda."""
from datetime import datetime, timedelta, timezone
from uuid import UUID
from jose import JWTError, jwt
from app.config import settings
from app.models.auth import TokenPayload

class JWTService:
    def __init__(self):
        self._secret = settings.secret_key
        self._algorithm = settings.algorithm
        self._access_expire = settings.access_token_expire_minutes
        self._refresh_expire = settings.refresh_token_expire_days

    def criar_access_token(self, usuario_id: UUID) -> str:
        exp = datetime.now(timezone.utc) + timedelta(minutes=self._access_expire)
        payload = TokenPayload(sub=usuario_id, exp=int(exp.timestamp()), tipo="access")
        return jwt.encode(payload.model_dump(), self._secret, algorithm=self._algorithm)

    def criar_refresh_token(self, usuario_id: UUID) -> str:
        exp = datetime.now(timezone.utc) + timedelta(days=self._refresh_expire)
        payload = TokenPayload(sub=usuario_id, exp=int(exp.timestamp()), tipo="refresh")
        return jwt.encode(payload.model_dump(), self._secret, algorithm=self._algorithm)

    def verificar_token(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(token, self._secret, algorithms=[self._algorithm])
            return TokenPayload(**payload)
        except JWTError as e:
            raise ValueError(f"Token inválido: {e}") from e
```

### 3. [TEST] tests/unit/test_auth_service.py (escrever PRIMEIRO)
Testes para `AuthService` (usar FakeDatabase + FakeRepository):
- `registrar(data)`: cria usuário, retorna (Usuario, access_token, refresh_token)
- `registrar(email_duplicado)`: levanta ValueError com email no erro
- `autenticar(data)`: retorna tokens para credenciais válidas
- `autenticar(senha_errada)`: levanta ValueError
- `autenticar(email_inexistente)`: levanta ValueError
- `refresh(token)`: retorna novo par de tokens
- `refresh(token_de_access)`: levanta ValueError (tipo errado)
- `buscar_usuario(id)`: retorna usuário
- `buscar_usuario(id_invalido)`: levanta ValueError

### 4. app/services/auth_service.py
```python
"""Lógica de negócio de autenticação.
Encapsula passlib para hash de senhas (Anti-Corruption Layer)."""
from uuid import UUID
from passlib.context import CryptContext
from app.models.auth import LoginRequest
from app.models.usuario import UsuarioCreate
from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.usuario import Usuario
from app.services.jwt_service import JWTService

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, repo: UsuarioRepository, jwt_service: JWTService):
        self._repo = repo
        self._jwt = jwt_service

    async def registrar(self, data: UsuarioCreate) -> tuple[Usuario, str, str]:
        ja_existe = await self._repo.buscar_por_email(data.email)
        if ja_existe:
            raise ValueError(f"Email já cadastrado: {data.email}")
        usuario = Usuario(
            nome=data.nome, email=data.email,
            senha_hash=self._hash_senha(data.senha), tipo=data.tipo,
        )
        usuario = await self._repo.criar(usuario)
        return usuario, self._jwt.criar_access_token(usuario.id), self._jwt.criar_refresh_token(usuario.id)

    async def autenticar(self, data: LoginRequest) -> tuple[Usuario, str, str]:
        usuario = await self._repo.buscar_por_email(data.email)
        if not usuario or not self._verificar_senha(data.senha, usuario.senha_hash):
            raise ValueError(f"Credenciais inválidas para: {data.email}")
        return usuario, self._jwt.criar_access_token(usuario.id), self._jwt.criar_refresh_token(usuario.id)

    async def refresh(self, refresh_token: str) -> tuple[str, str]:
        payload = self._jwt.verificar_token(refresh_token)
        if payload.tipo != "refresh":
            raise ValueError("Token fornecido não é um refresh token")
        usuario = await self._repo.buscar_por_id(payload.sub)
        if not usuario:
            raise ValueError(f"Usuário não encontrado: {payload.sub}")
        return self._jwt.criar_access_token(usuario.id), self._jwt.criar_refresh_token(usuario.id)

    async def buscar_usuario(self, usuario_id: UUID) -> Usuario:
        usuario = await self._repo.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError(f"Usuário não encontrado: {usuario_id}")
        return usuario

    def _hash_senha(self, senha: str) -> str:
        return _pwd_context.hash(senha)

    def _verificar_senha(self, senha: str, senha_hash: str) -> bool:
        return _pwd_context.verify(senha, senha_hash)
```

### 5. Implementar
Depois dos testes passarem (RED), implementar os arquivos acima (GREEN).

## Critérios de Aceitação
- [ ] `pytest tests/unit/test_jwt_service.py -v` passa
- [ ] `pytest tests/unit/test_auth_service.py -v` passa
- [ ] `mypy app/services/` passa sem erros
- [ ] Nenhum import direto de `jose` ou `passlib` fora dos services
- [ ] Docstring em todos os métodos públicos

## TodoList
- Revise as implementações e se tudo passou atualize:
    - `plans/2-todolist.md`
    - `plans/1-roadmap.md`
