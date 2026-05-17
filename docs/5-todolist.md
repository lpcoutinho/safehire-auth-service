# Plano de Execução — TodoList Detalhada

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
  # Framework
  fastapi>=0.104.0
  uvicorn[standard]>=0.24.0

  # Database
  sqlalchemy[asyncio]>=2.0.0
  asyncpg>=0.29.0

  # Validation
  pydantic>=2.0.0
  pydantic-settings>=2.0.0

  # Auth
  python-jose[cryptography]>=3.3.0
  passlib[bcrypt]>=1.7.4
  python-multipart>=0.0.6

  # Observability
  prometheus-fastapi-instrumentator>=7.0.0
  opentelemetry-api>=1.21.0
  opentelemetry-sdk>=1.21.0
  opentelemetry-instrumentation-fastapi>=0.42b0
  opentelemetry-instrumentation-httpx>=0.42b0
  opentelemetry-exporter-otlp>=1.21.0
  python-json-logger>=2.0.7
  boto3>=1.35.0         # CloudWatch (Floci + AWS)
  aws-xray-sdk>=2.14.0  # X-Ray (Floci + AWS)

  # Dev / Test
  httpx>=0.25.0
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
  ENV=development

  # CORS
  ALLOWED_ORIGINS=http://localhost:3000,http://frontend-app:3000

  # Observability Stack
  OBSERVABILITY_STACK=floci      # floci | vps | aws

  # Floci (dev)
  FLOCI_ENDPOINT=http://floci:4566
  AWS_ACCESS_KEY_ID=test_access_key
  AWS_SECRET_ACCESS_KEY=test_secret_key
  AWS_REGION=us-east-1
  XRAY_DAEMON_ADDRESS=floci:2000

  # VPS (open-source)
  PROMETHEUS_URL=http://prometheus:9090
  LOKI_URL=http://loki:3100
  TEMPO_URL=http://tempo:3200

  # AWS (production)
  CLOUDWATCH_LOG_GROUP=/aws/ecs/auth-service

  # Tracing
  TRACE_SAMPLING_RATE=1.0  # 100% dev, 0.1 prod

  # Logs
  LOG_LEVEL=INFO
  LOG_FORMAT=json
  ```
- [ ] Documentar cada arquivo com docstring no topo

### Models Pydantic
- [ ] `app/models/usuario.py`:
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
- [ ] `app/models/auth.py`:
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
- [ ] [TEST] Testes escritos **antes** da implementação
- [ ] Documentar cada classe com docstring

### Database Layer
- [ ] `app/database.py`:
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
