# Plano de Execução — TodoList Detalhada

## TodoList Detalhada

### Git Flow Setup
- [x] Criar branch `develop` a partir de `main`
- [x] Criar branch `staging` a partir de `main`
- [ ] Proteger `main` no GitHub (PR + CI + 1 approval, sem push direto)
- [ ] Proteger `staging` no GitHub (PR + CI + 1 approval, sem push direto)
- [x] Criar `.github/PULL_REQUEST_TEMPLATE.md`
- [x] Criar `plans/git-flow.md`
- [x] Criar template de PR no GitHub

### Configuração
- [x] Criar estrutura de pastas
- [x] Criar `pyproject.toml`:
- [x] Criar `requirements.txt`:
- [x] Criar `Dockerfile`:
- [x] Documentar cada arquivo com docstring no topo

### Config Layer
- [x] `app/config.py` — Settings com pydantic-settings (database_url, secret_key, observability_stack, etc.)
- [x] [TEST] `tests/unit/test_config.py` — validar defaults, env vars override, observability stack switching
- [x] Documentar config.py com docstring

### Database Layer
- [x] `app/database.py` — async engine, session factory, Base declarativa, get_session
- [x] [TEST] `tests/unit/test_database.py` — validar engine, session factory, get_session
- [x] `app/schemas/usuario.py` — ORM model Usuario (auth_schema)
- [x] `tests/fakes/fake_database.py` — FakeDatabase com dict in-memory
- [x] `tests/fakes/fake_postgres.py` — FakePostgres async generator

### Models Pydantic
- [x] `app/models/usuario.py`:
  ```python
  """Schemas Pydantic para Usuario (request/response)."""
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
- [x] `app/models/auth.py`:
  ```python
  """Schemas Pydantic para autenticação (login, tokens)."""
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
- [x] [TEST] Testes escritos **antes** da implementação
- [x] Documentar cada classe com docstring

### Database Layer
- [x] `app/database.py`:
  ```python
  """Conexão assíncrona com PostgreSQL via SQLAlchemy."""
  from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
  from sqlalchemy.orm import declarative_base
  from app.config import settings

  engine = create_async_engine(settings.database_url, echo=settings.debug)
  async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
  Base = declarative_base()

  async def get_session() -> AsyncSession:
    """Yields async session with commit/rollback handling.
    Usage: Depends(get_session) nos endpoints.
    """
    async with async_session() as session:
      try:
        yield session
        await session.commit()
      except Exception:
        await session.rollback()
        raise
  ```

### Repository Layer
- [x] `app/repositories/usuario_repo.py` — UsuarioRepository com criar, buscar_por_email, buscar_por_id, listar_ativos, atualizar
- [x] [TEST] `tests/unit/test_usuario_repo.py` — 8 testes com SQLite in-memory
- [x] Documentar repository com docstring

### Observability Layer
- [ ] `app/observability/config.py`:
  ```python
  """Config stack-aware de observabilidade (Floci/VPS/AWS)."""
  from pydantic_settings import BaseSettings

  class ObservabilityConfig(BaseSettings):
      stack: str = 'floci'
      floci_endpoint: str = 'http://floci:4566'
      xray_daemon_address: str = 'floci:2000'
      prometheus_url: str = 'http://prometheus:9090'
      loki_url: str = 'http://loki:3100'
      tempo_url: str = 'http://tempo:3200'
      aws_region: str = 'us-east-1'
      cloudwatch_log_group: str = '/aws/ecs/auth-service'
      log_level: str = 'INFO'
      trace_sampling_rate: float = 1.0

      class Config:
          env_prefix = 'OBSERVABILITY_'
  ```
- [ ] `app/observability/factory.py`:
  ```python
  """Factory para criar clientes de observabilidade por stack."""
  ```
- [ ] `app/observability/metrics.py` — CloudWatchMetrics + Prometheus
- [ ] `app/observability/tracing.py` — XRayTracer + LocalTracer
- [ ] `app/observability/logging.py` — Logger estruturado JSON
- [ ] [TEST] Testar cada factory e emissão de métrica
- [ ] Documentar cada módulo

### Middleware
- [ ] `app/middleware/observability.py`:
  ```python
  """Middleware de observabilidade: métricas, tracing, logging."""
  from prometheus_fastapi_instrumentator import Instrumentator
  from opentelemetry import trace
  import json_logging

  instrumentator = Instrumentator().instrument(app)
  tracer = trace.get_tracer(__name__)
  ```
- [ ] [TEST] Testar middleware isoladamente

### Schemas ORM
- [ ] `app/schemas/usuario.py`:
  ```python
  """Modelo ORM SQLAlchemy para tabela usuarios (auth_schema)."""
  from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
  from sqlalchemy.sql import func
  from app.database import Base
  from app.models.usuario import UserRole

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
  """Operações JWT: criação e validação de tokens."""
  from datetime import datetime, timedelta
  from jose import JWTError, jwt
  from app.config import settings
  from app.models.auth import TokenPayload

  class JWTService:
      def criar_access_token(self, usuario_id: UUID) -> str:
          ...
      def criar_refresh_token(self, usuario_id: UUID) -> str:
          ...
      def verificar_token(self, token: str) -> TokenPayload:
          ...
  ```
- [ ] [TEST] Testes escritos **antes** da implementação

- [ ] `app/services/auth_service.py`:
  ```python
  """Lógica de negócio de autenticação: registro, login, refresh."""
  from passlib.context import CryptContext

  class AuthService:
      async def registrar(self, data: UsuarioCreate) -> tuple[Usuario, str, str]:
          """Registra novo usuário e retorna tokens."""
          ...
      async def autenticar(self, data: LoginRequest) -> tuple[Usuario, str, str]:
          """Autentica usuário e retorna tokens."""
          ...
      async def refresh(self, refresh_token: str) -> tuple[str, str]:
          """Renova tokens usando refresh token."""
          ...
  ```
- [ ] [TEST] Testes escritos **antes** da implementação

### Routes
- [ ] `app/routes/auth.py`:
  ```python
  """Endpoints de autenticação (/auth/register, /login, /refresh, /logout)."""
  ```
- [ ] `app/routes/usuarios.py`:
  ```python
  """Endpoints de CRUD de usuários (/usuarios/me, /{id})."""
  ```
- [ ] [TEST] Testes de integração escritos **antes**
- [ ] Documentar cada endpoint com docstring

### Testes
- [ ] `tests/conftest.py`:
  ```python
  """Fixtures compartilhadas: client HTTP, session de teste."""
  ```
- [ ] `tests/unit/test_*` — um arquivo por módulo
- [ ] `tests/integration/test_*` — fluxos completos
- [ ] `tests/fakes/` — fakes para I/O externo

### Docker / Deploy
- [ ] `docker/docker-compose.yml` (dev com Floci):
  ```yaml
  version: '3.8'
  services:
    floci:
      image: localstack/localstack:latest
      environment:
        SERVICES: cloudwatch,logs,xray,s3,sqs
      ports:
        - "4566:4566"
    otel-collector:
      image: otel/opentelemetry-collector-contrib:latest
      environment:
        AWS_ACCESS_KEY_ID: test
        AWS_SECRET_ACCESS_KEY: test
        AWS_REGION: us-east-1
        AWS_ENDPOINT_URL: http://floci:4566
    postgres:
      image: postgres:16-alpine
    auth-service:
      build: ..
      environment:
        OBSERVABILITY_STACK: floci
        FLOCI_ENDPOINT: http://floci:4566
  ```
- [ ] `docker/docker-compose.vps.yml` (VPS com open-source):
  ```yaml
  services:
    prometheus: ...
    grafana: ...
    loki: ...
    tempo: ...
    postgres: ...
    auth-service:
      environment:
        OBSERVABILITY_STACK: vps
        PROMETHEUS_URL: http://prometheus:9090
  ```
- [ ] `docker/ecs-task-definition.json` (AWS):
  ```json
  {
    "containerDefinitions": [
      {"name": "auth-service", ...},
      {"name": "xray-daemon", "image": "amazon/aws-xray-daemon"}
    ]
  }
  ```

---
