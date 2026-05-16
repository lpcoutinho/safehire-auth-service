# Auth Service - Plano de Execução Detalhado

## Visão Geral

O **Auth Service** é o serviço central de autenticação e autorização da plataforma SafeHire AI. Responsável por gerenciar usuários (recrutadores e candidatos), emitir tokens JWT e validar credenciais.

### Propósito
- Gerenciar o ciclo de vida de usuários (registro, login, logout)
- Emitir e validar tokens JWT
- Gerenciar refresh tokens
- Isolar dados de autenticação em schema próprio do PostgreSQL

### Stack Tecnológica
- **Framework**: FastAPI (assíncrono)
- **Linguagem**: Python 3.11+
- **Banco de Dados**: PostgreSQL (schema `auth_schema`)
- **Validação**: Pydantic v2
- **Segurança**: JWT, bcrypt para hashing de senhas
- **Formatting**: black, isort

---

## Arquitetura do Serviço

```
auth-service/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point FastAPI
│   ├── config.py            # Configurações (env vars)
│   ├── database.py          # Conexão PostgreSQL
│   ├── models/              # Pydantic models
│   │   ├── __init__.py
│   │   ├── usuario.py       # Request/Response schemas
│   │   └── auth.py          # Token schemas
│   ├── schemas/             # SQLAlchemy ORM
│   │   ├── __init__.py
│   │   └── usuario.py       # Usuario ORM model
│   ├── repositories/        # Data access layer
│   │   ├── __init__.py
│   │   └── usuario_repo.py  # UsuarioRepository
│   ├── services/            # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py  # Auth business logic
│   │   └── jwt_service.py   # JWT operations
│   ├── routes/              # API endpoints
│   │   ├── __init__.py
│   │   ├── usuarios.py      # Usuario CRUD endpoints
│   │   └── auth.py          # Auth endpoints
│   └── middleware/          # Custom middleware
│       ├── __init__.py
│       └── auth.py          # Auth middleware
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Pytest fixtures
│   ├── unit/                # Unit tests
│   │   ├── __init__.py
│   │   ├── test_jwt_service.py
│   │   ├── test_password_hash.py
│   │   └── test_models.py
│   ├── integration/         # Integration tests
│   │   ├── __init__.py
│   │   ├── test_auth_flow.py
│   │   └── test_usuario_crud.py
│   └── fakes/               # Fake implementations
│       ├── __init__.py
│       ├── fake_database.py
│       └── fake_postgres.py
├── Dockerfile
├── requirements.txt
├── .env.example
├── pyproject.toml           # black, isort, pytest configs
├── README.md
└── CLAUDE.md
```

---

## Roadmap de Implementação

### Fase 1: Configuração Base (Dia 1)
- [ ] Criar estrutura de pastas do projeto
- [ ] Criar `pyproject.toml` com configs (black, isort, pytest, mypy)
- [ ] Criar `requirements.txt` com todas as dependências
- [ ] Criar `Dockerfile` otimizado
- [ ] Criar `.env.example` com todas as variáveis
- [ ] Criar `conftest.py` com fixtures básicos
- [ ] Configurar `.gitignore` apropriado

### Fase 2: Camada de Configuração e Database (Dia 1-2)
- [ ] Implementar `config.py` com Pydantic Settings
- [ ] Implementar `database.py` com async PostgreSQL connection
- [ ] Criar schema `auth_schema` no PostgreSQL
- [ ] Implementar ORM models em `schemas/usuario.py`
- [ ] Implementar `fake_database.py` para testes
- [ ] Criar migrations (Alembic opcional)

### Fase 3: Camada de Models Pydantic (Dia 2)
- [ ] Implementar `models/usuario.py`:
  - `UsuarioCreateRequest`
  - `UsuarioResponse`
  - `RecrutadorCreateRequest`
  - `CandidatoCreateRequest`
- [ ] Implementar `models/auth.py`:
  - `LoginRequest`
  - `LoginResponse` (access_token, refresh_token)
  - `RefreshTokenRequest`
  - `RefreshTokenResponse`

### Fase 4: Camada de Repositories (Dia 2-3)
- [ ] Implementar `repositories/usuario_repo.py`:
  - `UsuarioRepository.create()`
  - `UsuarioRepository.get_by_email()`
  - `UsuarioRepository.get_by_id()`
  - `UsuarioRepository.update()`
  - `UsuarioRepository.delete()`
  - `UsuarioRepository.list_all()`
- [ ] Implementar FakeRepository para testes

### Fase 5: Camada de Services (Dia 3-4)
- [ ] Implementar `services/jwt_service.py`:
  - `encode_jwt_token()`
  - `decode_jwt_token()`
  - `verify_jwt_signature()`
  - `create_access_token()`
  - `create_refresh_token()`
- [ ] Implementar `services/auth_service.py`:
  - `hash_password()` usando bcrypt
  - `verify_password()` usando bcrypt
  - `register_usuario()`
  - `login_usuario()`
  - `refresh_token()`
  - `logout_usuario()`
  - `validate_token()`

### Fase 6: Camada de Routes (Dia 4-5)
- [ ] Implementar `routes/usuarios.py`:
  - `POST /usuarios` - Criar usuário
  - `GET /usuarios/{id}` - Buscar usuário
  - `GET /usuarios` - Listar usuários
  - `PUT /usuarios/{id}` - Atualizar usuário
  - `DELETE /usuarios/{id}` - Deletar usuário
- [ ] Implementar `routes/auth.py`:
  - `POST /auth/register` - Registro
  - `POST /auth/login` - Login
  - `POST /auth/refresh` - Refresh token
  - `POST /auth/logout` - Logout
  - `POST /auth/verify` - Verificar token

### Fase 7: Middleware e Security (Dia 5)
- [ ] Implementar `middleware/auth.py`:
  - `AuthMiddleware` para validação de tokens
  - `require_auth()` decorator
- [ ] Implementar rate limiting
- [ ] Implementar CORS configuration
- [ ] Implementar security headers

### Fase 8: Entry Point e Orquestração (Dia 5-6)
- [ ] Implementar `app/main.py`:
  - Inicializar FastAPI app
  - Configurar CORS
  - Registrar middleware
  - Registrar routes
  - Health check endpoint
- [ ] Criar `app/__init__.py`
- [ ] Configurar logging estruturado JSON

### Fase 9: Testes (Dia 6-7)
- [ ] Testes unitários de `jwt_service.py`
- [ ] Testes unitários de `auth_service.py`
- [ ] Testes unitários de models Pydantic
- [ ] Testes de integração de endpoints auth
- [ ] Testes de integração de CRUD usuarios
- [ ] Testes de autenticação entre serviços
- [ ] Testes de segurança (SQL injection, XSS)
- [ ] Testes de rate limiting

### Fase 10: Documentação e Finalização (Dia 7-8)
- [ ] Configurar OpenAPI/Swagger docs
- [ ] Criar `README.md` com instruções
- [ ] Criar scripts de setup local
- [ ] Revisão de código (peer review)
- [ ] Refinamentos baseados em feedback

---

## TodoList Detalhada

### Configuração
- [x] Criar estrutura de pastas
- [ ] Criar `pyproject.toml`:
  ```toml
  [tool.black]
  line-length = 88
  target-version = ['py311']

  [tool.isort]
  profile = "black"
  line_length = 88

  [tool.pytest.ini_options]
  testpaths = ["tests"]
  python_files = ["test_*.py"]
  python_classes = ["Test*"]
  python_functions = ["test_*"]

  [tool.mypy]
  strict = true
  ```
- [ ] Criar `requirements.txt`:
  ```
  fastapi>=0.104.0
  uvicorn[standard]>=0.24.0
  pydantic>=2.0.0
  pydantic-settings>=2.0.0
  sqlalchemy[asyncio]>=2.0.0
  asyncpg>=0.29.0
  python-jose[cryptography]>=3.3.0
  passlib[bcrypt]>=1.7.4
  python-multipart>=0.0.6
  alembic>=1.12.0
  httpx>=0.25.0  # Para testes
  pytest>=7.4.0
  pytest-asyncio>=0.21.0
  pytest-cov>=4.1.0
  black>=23.10.0
  isort>=5.12.0
  mypy>=1.6.0
  ```
- [ ] Criar `Dockerfile`:
  ```dockerfile
  FROM python:3.11-slim

  WORKDIR /app

  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  COPY . .

  EXPOSE 8000

  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```
- [ ] Criar `.env.example`:
  ```env
  # Database
  DATABASE_URL=postgresql+asyncpg://user:password@postgres:5432/safehire
  AUTH_SCHEMA=auth_schema

  # JWT
  JWT_SECRET_KEY=your-secret-key-here
  JWT_ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  REFRESH_TOKEN_EXPIRE_DAYS=7

  # App
  APP_NAME=Auth Service
  APP_VERSION=1.0.0
  DEBUG=False

  # CORS
  ALLOWED_ORIGINS=http://localhost:3000,http://frontend-app:3000
  ```

### Models Pydantic
- [ ] `app/models/usuario.py`:
  ```python
  from pydantic import BaseModel, EmailStr, Field
  from enum import Enum
  from datetime import datetime

  class UserRole(str, Enum):
    RECRUTADOR = "recrutador"
    CANDIDATO = "candidato"

  class UsuarioBase(BaseModel):
    email: EmailStr
    nome_completo: str = Field(..., min_length=3, max_length=100)

  class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=8, max_length=100)
    role: UserRole

  class UsuarioResponse(BaseModel):
    id: int
    email: EmailStr
    nome_completo: str
    role: UserRole
    ativo: bool
    criado_em: datetime

    class Config:
      from_attributes = True
  ```

- [ ] `app/models/auth.py`:
  ```python
  from pydantic import BaseModel, Field

  class LoginRequest(BaseModel):
    email: str = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")

  class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

  class RefreshTokenRequest(BaseModel):
    refresh_token: str
  ```

### Database Layer
- [ ] `app/database.py`:
  ```python
  from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
  from sqlalchemy.orm import declarative_base
  from app.config import settings

  engine = create_async_engine(settings.database_url, echo=settings.debug)
  async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
  Base = declarative_base()

  async def get_session() -> AsyncSession:
    async with async_session() as session:
      yield session
  ```

### Schemas ORM
- [ ] `app/schemas/usuario.py`:
  ```python
  from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
  from sqlalchemy.sql import func
  from app.database import Base
  from app.models.usuario import UserRole
  import enum

  class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "auth_schema"}

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    nome_completo = Column(String(100), nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False)
    ativo = Column(Boolean, default=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())
    atualizado_em = Column(DateTime(timezone=True), onupdate=func.now())
  ```

### Services
- [ ] `app/services/jwt_service.py`:
  ```python
  from datetime import datetime, timedelta
  from jose import JWTError, jwt
  from app.config import settings

  def encode_jwt_token(payload: dict) -> str:
    """Codifica payload em JWT token."""
    ...

  def decode_jwt_token(token: str) -> dict:
    """Decodifica JWT token e retorna payload."""
    ...

  def create_access_token(user_id: int, role: str) -> str:
    """Cria access token para usuário."""
    ...

  def create_refresh_token(user_id: int) -> str:
    """Cria refresh token para usuário."""
    ...
  ```

- [ ] `app/services/auth_service.py`:
  ```python
  from passlib.context import CryptContext
  from sqlalchemy.ext.asyncio import AsyncSession
  from app.repositories.usuario_repo import UsuarioRepository

  pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

  def hash_password(password: str) -> str:
    """Hash senha usando bcrypt."""
    ...

  def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica senha contra hash."""
    ...

  async def register_usuario(
    session: AsyncSession,
    email: str,
    password: str,
    nome_completo: str,
    role: str
  ) -> dict:
    """Registra novo usuário."""
    ...

  async def login_usuario(
    session: AsyncSession,
    email: str,
    password: str
  ) -> dict:
    """Autentica usuário e retorna tokens."""
    ...
  ```

### Routes
- [ ] `app/routes/auth.py`:
  ```python
  from fastapi import APIRouter, Depends, HTTPException, status
  from sqlalchemy.ext.asyncio import AsyncSession
  from app.database import get_session
  from app.models.auth import LoginRequest, LoginResponse
  from app.services.auth_service import login_usuario

  router = APIRouter(prefix="/auth", tags=["Authentication"])

  @router.post("/login", response_model=LoginResponse)
  async def login(
    request: LoginRequest,
    session: AsyncSession = Depends(get_session)
  ) -> LoginResponse:
    """Autentica usuário e retorna tokens."""
    ...

  @router.post("/register")
  async def register(...):
    """Registra novo usuário."""
    ...

  @router.post("/refresh")
  async def refresh_token(...):
    """Renova access token usando refresh token."""
    ...
  ```

### Tests
- [ ] `tests/conftest.py`:
  ```python
  import pytest
  from httpx import AsyncClient
  from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

  @pytest.fixture
  async def client():
    """Cliente HTTP assíncrono para testes."""
    ...

  @pytest.fixture
  async def test_session():
    """Sessão de teste isolada."""
    ...
  ```

- [ ] `tests/unit/test_jwt_service.py`:
  ```python
  import pytest
  from app.services.jwt_service import encode_jwt_token, decode_jwt_token

  def test_encode_decode_token():
    """Testa codificação e decodificação de token."""
    ...

  def test_invalid_token():
    """Testa erro ao decodificar token inválido."""
    ...
  ```

- [ ] `tests/integration/test_auth_flow.py`:
  ```python
  import pytest
  from httpx import AsyncClient

  @pytest.mark.asyncio
  async def test_register_login_flow(client: AsyncClient):
    """Testa fluxo completo de registro e login."""
    ...
  ```

---

## Validação e Critérios de Aceitação

### Funcional
- [ ] Usuário pode se registrar com email e senha válidos
- [ ] Senha é hasheada com bcrypt antes de armazenar
- [ ] Login retorna access_token e refresh_token
- [ ] Access token expira em 30 minutos
- [ ] Refresh token pode renovar access token
- [ ] Logout invalida refresh token
- [ ] Dados de usuário são isolados no `auth_schema`
- [ ] Validação de email único funciona
- [ ] Validação de senha forte (mínimo 8 caracteres)

### Técnico
- [ ] Endpoints respondem em < 200ms
- [ ] Database connection pool funciona corretamente
- [ ] Async operations não bloqueiam
- [ ] Requisições concorrentes são tratadas
- [ ] Schema Pydantic valida entrada
- [ ] Erros retornam formato padronizado

### Segurança
- [ ] Senhas nunca são expostas em logs
- [ ] JWT tokens são assinados corretamente
- [ ] Token inválido retorna 401
- [ ] Token expirado retorna 401
- [ ] SQL injection prevenido via SQLAlchemy
- [ ] Rate limiting evita brute force

### Testes
- [ ] Coverage >= 80%
- [ ] Todos os testes passam
- [ ] Testes são determinísticos
- [ ] Fakes implementados para I/O externo
- [ ] Testes de integração usam database isolado

### Código
- [ ] Funções têm 4-20 linhas
- [ ] Arquivos têm < 500 linhas
- [ ] Nomes únicos (anti-grep)
- [ ] Tipo estrito (mypy strict)
- [ ] Early returns
- [ ] Docstrings em funções públicas
- [ ] black e isort configurados

---

## Comandos de Desenvolvimento

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar em desenvolvimento
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Formatar código
black app tests
isort app tests

# Verificar tipos
mypy app

# Rodar testes
pytest tests -v --cov=app --cov-report=html

# Rodar testes específicos
pytest tests/unit/test_jwt_service.py -v

# Rodar com docker
docker build -t auth-service .
docker run -p 8000:8000 --env-file .env auth-service
```

---

## Próximos Passos

Após completar este serviço:

1. Integrar com API Gateway
2. Testar autenticação end-to-end
3. Documentar endpoints
4. Criar scripts de seed para testes
5. Configurar monitoramento e logging

---

## Referências

- `PROJECT_CONTEXT.md` - Arquitetura geral
- `CLAUDE.md` - Regras de código
- `plano-geral-execucao.md` - Roadmap global