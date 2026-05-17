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
- **Observabilidade (Dev)**: Floci (emulador AWS — CloudWatch Metrics, Logs, X-Ray)
- **Observabilidade (VPS)**: OpenTelemetry Collector → Prometheus/Grafana/Loki/Tempo
- **Observabilidade (AWS)**: CloudWatch Metrics, CloudWatch Logs, AWS X-Ray
- **Coleta**: OpenTelemetry SDK + Prometheus FastAPI Instrumentator
- **Logging**: Estruturado JSON
- **Formatting**: black, isort, mypy strict

---

## Princípios Norteadores

### 1. Test-First (TDD)
Antes de implementar qualquer método novo, **deve existir um teste que falhe** e que:
- Defina o comportamento esperado do método
- Cubra o caso feliz (happy path)
- Cubra pelo menos um caso de erro (edge case)
- Use `pytest` com fixtures apropriadas

> `RED → GREEN → REFACTOR`: escreva o teste (RED), implemente o mínimo para passar (GREEN), refine (REFACTOR).

### 2. Documentação em Todo Arquivo e Método
- **Todo arquivo** deve ter docstring no topo explicando sua responsabilidade.
- **Todo método público** deve ter docstring com:
  - Descrição da intenção (WHY, não WHAT)
  - Exemplo de uso (uma linha)
  - Tipos documentados (já garantidos por type hints + mypy strict)
- **Todo método privado** deve ter docstring se sua lógica não for óbvia.

### 3. Observabilidade First
Todo método que envolva I/O (DB, cache, rede, filesystem) **deve**:
- Emitir métrica de duração
- Logar entrada/saída em structured JSON
- Propagar trace_id/span_id via OpenTelemetry

### 4. Dual-Stack Deploy (AWS + VPS)
O serviço deve ser deployável em ambos os cenários sem mudança de código:
- **VPS** (ex: Hostinger): Docker Compose com PostgreSQL, OpenTelemetry → Prometheus/Loki/Tempo
- **AWS**: ECS Fargate com CloudWatch Logs, X-Ray sidecar, Secrets Manager

### 5. Clean Code & Design

#### 5.1 Injeção de Dependências
- Toda dependência externa (DB, cache, serviços) deve ser injetada via parâmetros do construtor ou FastAPI `Depends`
- Nada de imports diretos em lógica profunda ou globais `from x import y` no meio de funções de negócio
- Bibliotecas terceiras (ex: `python-jose`, `passlib`, `boto3`) devem ser envolvidas em uma interface fina própria do projeto
  - `JWTService` encapsula `jose.jwt`
  - `AuthService` encapsula `passlib`
  - `CloudWatchMetrics` encapsula `boto3.client('cloudwatch')`

#### 5.2 Princípio da Responsabilidade Única (SRP)
- **Um módulo, uma responsabilidade**: `repositories/` só acessa dados, `services/` só tem lógica de negócio, `routes/` só orquestra HTTP
- **Uma função, uma coisa**: se a função faz validação + cálculo + persistência, divida
- **Arquivos < 500 linhas**, **funções 4-20 linhas**

#### 5.3 Nomes Específicos e Únicos
- Evite sufixos genéricos como `Handler`, `Manager`, `Data`, `Utils`, `Helper`
- Prefira nomes que retornem < 5 resultados no grep no código todo
- Exemplo: em vez de `UserManager`, use `UsuarioRepository`; em vez de `AuthHandler`, use `AuthService`

#### 5.4 Tipos Explícitos e Estritos
- Sem `Any` — use tipos específicos: `UUID`, `str`, `Usuario`, `list[Usuario]`
- Sem `dict` genérico — prefira schemas Pydantic tipados
- `mypy strict` deve passar sem erros
- Union types explícitos: `Usuario | None`, não `Optional[Usuario]`

#### 5.5 Idempotência
- **`POST /auth/register`**: idempotente — se o email já existe, retorna erro 409 consistente, nunca cria duplicata
- **`POST /auth/refresh`**: com o mesmo refresh token, produz o mesmo efeito (novo par de tokens)
- **`POST /auth/logout`**: revogar refresh token é idempotente — chamadas repetidas têm o mesmo efeito
- Evite mutação de parâmetros recebidos; prefira `frozenset` a `set` em APIs públicas

#### 5.6 Early Returns e Imports no Topo
- Máximo 2 níveis de indentação aninhada
- Early returns em vez de `if/else` aninhados
- Todos os `import` no topo do arquivo, nunca dentro de funções

#### 5.7 Zero Duplicidade (DRY)
- Toda lógica repetida em 2+ lugares deve ser extraída para função/módulo compartilhado
- Constantes mágicas (timeouts, limites) devem ser configuráveis via `Settings`, nunca literais espalhados

#### 5.8 Mensagens de Erro Descritivas
- Exceções devem incluir o **valor ofensivo** e o **formato esperado**
  - ✅ `raise ValueError(f"Email já cadastrado: {email}")`
  - ❌ `raise ValueError("Email já existe")`

#### 5.9 Anti-Corruption Layer (Bibliotecas Terceiras)
- Toda biblioteca externa encapsulada atrás de interface própria do projeto:
  - `JWTService` → `python-jose`
  - `AuthService` → `passlib` / `bcrypt`
  - `CloudWatchMetrics` → `boto3`
  - `XRayTracer` → `aws_xray_sdk`
- Se a biblioteca mudar, só a interface fina muda
- Nenhum import direto de terceiros fora dos módulos de serviço/infra


---

## Arquitetura do Serviço

```
auth-service/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Entry point FastAPI + observability init
│   ├── config.py                # Configurações (env vars + observability stack)
│   ├── database.py              # Conexão PostgreSQL
│   ├── models/                  # Pydantic models
│   │   ├── __init__.py
│   │   ├── usuario.py           # Request/Response schemas
│   │   └── auth.py              # Token schemas
│   ├── schemas/                 # SQLAlchemy ORM
│   │   ├── __init__.py
│   │   └── usuario.py           # Usuario ORM model
│   ├── repositories/            # Data access layer
│   │   ├── __init__.py
│   │   └── usuario_repo.py      # UsuarioRepository
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Auth business logic
│   │   └── jwt_service.py       # JWT operations
│   ├── routes/                  # API endpoints
│   │   ├── __init__.py
│   │   ├── usuarios.py          # Usuario CRUD endpoints
│   │   └── auth.py              # Auth endpoints
│   ├── middleware/              # Custom middleware
│   │   ├── __init__.py
│   │   ├── auth.py              # Auth middleware
│   │   └── observability.py     # Metrics + tracing + logging middleware
│   └── observability/           # Observability layer
│       ├── __init__.py
│       ├── config.py            # ObservabilityConfig (stack-aware)
│       ├── factory.py           # Factory: dev(floci) / vps(otel) / aws(cloudwatch)
│       ├── metrics.py           # Padrão: CloudWatch via boto3 / Prometheus
│       ├── tracing.py           # Padrão: X-Ray via Floci / OpenTelemetry
│       └── logging.py           # Logger estruturado JSON
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── unit/                    # Unit tests
│   │   ├── __init__.py
│   │   ├── test_jwt_service.py
│   │   ├── test_password_hash.py
│   │   ├── test_models.py
│   │   ├── test_auth_service.py
│   │   └── test_observability.py
│   ├── integration/             # Integration tests
│   │   ├── __init__.py
│   │   ├── test_auth_flow.py
│   │   └── test_usuario_crud.py
│   └── fakes/                   # Fake implementations
│       ├── __init__.py
│       ├── fake_database.py
│       └── fake_postgres.py
├── docker/                      # Docker configs
│   ├── docker-compose.yml       # Dev stack (Floci + PostgreSQL + app)
│   ├── docker-compose.vps.yml   # VPS stack (Grafana/Prometheus/Loki/Tempo)
│   └── ecs-task-definition.json # AWS ECS Fargate
├── Dockerfile
├── requirements.txt
├── .env.example
├── pyproject.toml               # black, isort, pytest, mypy configs
├── README.md
└── CLAUDE.md
```

---

## Triple-Stack Observability

```
              ┌─────────────────────┐
              │   Auth Service       │
              │   (FastAPI + OTEL)   │
              └──────────┬──────────┘
                         │
     ┌───────────────────┼───────────────────┐
     │                   │                   │
     ▼                   ▼                   ▼
┌────────────┐   ┌──────────────┐   ┌──────────────┐
│ DEV (Floci) │   │ VPS (Self)   │   │ PROD (AWS)   │
│ :4566       │   │ :9090/:3001   │   │ CloudWatch   │
├────────────┤   ├──────────────┤   ├──────────────┤
│ CloudWatch │   │ Prometheus   │   │ CloudWatch   │
│ Metrics    │   │ Grafana      │   │ Metrics+Logs │
│ Logs       │   │ Loki         │   │ X-Ray        │
│ X-Ray      │   │ Tempo        │   │ Synthetics   │
└────────────┘   └──────────────┘   └──────────────┘
```

A variável `OBSERVABILITY_STACK=floci|vps|aws` determina a stack ativa sem mudar código.

---

## Roadmap de Implementação

### Pré-condição para toda fase
- [ ] **Testes existem antes do código**: para cada método novo, o teste deve ser escrito **primeiro**.
- [ ] **Documentação**: docstring no topo do arquivo + docstring em cada método público.
- [ ] **Observabilidade**: logging estruturado + métricas de duração + tracing.

---

### Fase 1: Configuração Base (Dia 1)
- [ ] Criar estrutura de pastas do projeto
- [ ] Criar `pyproject.toml` com configs (black, isort, pytest, mypy)
- [ ] Criar `requirements.txt` com todas as dependências (incluindo observabilidade)
- [ ] Criar `Dockerfile` otimizado
- [ ] Criar `.env.example` com todas as variáveis (incluindo observabilidade)
- [ ] Criar `conftest.py` com fixtures básicos
- [ ] Configurar `.gitignore` apropriado
- [ ] **Documentar** cada arquivo criado com docstring

### Fase 2: Camada de Configuração e Database (Dia 1-2)
- [ ] Implementar `config.py` com Pydantic Settings + `OBSERVABILITY_STACK`
- [ ] Implementar `database.py` com async PostgreSQL connection
- [ ] Criar schema `auth_schema` no PostgreSQL
- [ ] Implementar ORM models em `schemas/usuario.py`
- [ ] Implementar `fake_database.py` para testes
- [ ] [TEST] `tests/unit/test_config.py` — validar leitura de env vars e stack
- [ ] [TEST] `tests/unit/test_database.py` — validar criação de engine e session
- [ ] **Documentar** config.py, database.py, schemas/usuario.py

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
- [ ] [TEST] `tests/unit/test_models.py` — validar validação de cada schema (escrito **antes** da implementação)
- [ ] **Documentar** cada modelo com docstring

### Fase 4: Camada de Repositories (Dia 2-3)
- [ ] Implementar `repositories/usuario_repo.py`:
  - `UsuarioRepository.criar(usuario) → Usuario`
  - `UsuarioRepository.buscar_por_email(email) → Usuario | None`
  - `UsuarioRepository.buscar_por_id(id) → Usuario | None`
  - `UsuarioRepository.atualizar(usuario) → Usuario`
  - `UsuarioRepository.listar_ativos() → list[Usuario]`
- [ ] Implementar FakeRepository para testes
- [ ] [TEST] `tests/unit/test_usuario_repo.py` — testar cada método **antes** da implementação
- [ ] **Observabilidade**: cada método de I/O emite métrica de duração
- [ ] **Documentar** repository com docstring

### Fase 5: Camada de Services (Dia 3-4)
- [ ] Implementar `services/jwt_service.py`:
  - `criar_access_token(usuario_id) → str`
  - `criar_refresh_token(usuario_id) → str`
  - `verificar_token(token) → TokenPayload`
- [ ] Implementar `services/auth_service.py`:
  - `registrar(data) → tuple[Usuario, str, str]`
  - `autenticar(data) → tuple[Usuario, str, str]`
  - `refresh(refresh_token) → tuple[str, str]`
  - `buscar_usuario(id) → Usuario`
- [ ] [TEST] `tests/unit/test_jwt_service.py` — testar criação e validação de tokens **antes** da implementação
- [ ] [TEST] `tests/unit/test_auth_service.py` — testar registro, login, refresh **antes** da implementação
- [ ] **Observabilidade**: cada método loga entrada/saída + métrica de duração
- [ ] **Documentar** cada método público com docstring

### Fase 6: Camada de Routes (Dia 4-5)
- [ ] Implementar `routes/usuarios.py`:
  - `GET /usuarios/me` — Perfil do usuário logado
  - `PUT /usuarios/me` — Atualizar perfil
  - `GET /usuarios/{id}` — Buscar usuário
- [ ] Implementar `routes/auth.py`:
  - `POST /auth/register` — Registro
  - `POST /auth/login` — Login
  - `POST /auth/refresh` — Refresh token
  - `POST /auth/logout` — Logout
- [ ] [TEST] `tests/integration/test_auth_flow.py` — fluxo completo de auth **antes** dos endpoints
- [ ] [TEST] `tests/integration/test_usuario_crud.py` — CRUD de usuários **antes** dos endpoints
- [ ] **Observabilidade**: middleware de métricas (requisições, latência, erros)
- [ ] **Documentar** cada endpoint com docstring

### Fase 7: Middleware e Security (Dia 5)
- [ ] Implementar `middleware/auth.py`:
  - `get_usuario_atual()` — dependency injection
- [ ] Implementar `middleware/observability.py`:
  - Middleware de métricas Prometheus
  - Middleware de tracing OpenTelemetry
  - Logger estruturado JSON com correlation_id
- [ ] Implementar CORS configuration
- [ ] Implementar security headers
- [ ] [TEST] `tests/unit/test_middleware_auth.py` — testar extração de token
- [ ] [TEST] `tests/unit/test_observability.py` — testar emissão de métricas
- [ ] **Documentar** cada middleware

### Fase 8: Observability Layer (Dia 5-6)
- [ ] Criar `app/observability/` com:
  - `config.py` — ObservabilityConfig (stack-aware, pydantic-settings)
  - `factory.py` — create_metrics, create_logger, create_tracer por stack
  - `metrics.py` — CloudWatchMetrics (Floci/AWS) ou Prometheus (VPS)
  - `tracing.py` — XRayTracer (Floci/AWS) ou LocalTracer (VPS/OTEL)
  - `logging.py` — logger estruturado JSON
- [ ] Expor endpoint `/metrics` (Prometheus)
- [ ] Adicionar health check `/health`
- [ ] [TEST] `tests/unit/test_observability.py` — testar factory e emissão
- [ ] **Documentar** cada módulo de observabilidade

### Fase 9: Entry Point e Orquestração (Dia 5-6)
- [ ] Implementar `app/main.py`:
  - Inicializar FastAPI app
  - Configurar CORS
  - Registrar middleware (auth + observability)
  - Registrar routes
  - Health check endpoint
  - Inicializar observability stack
- [ ] Configurar logging estruturado JSON
- [ ] [TEST] `tests/integration/test_health.py` — testar `/health` e `/metrics`

### Fase 10: Deploy e Containerização (Dia 6-7)
- [ ] Criar `docker/docker-compose.yml` (dev):
  - Floci (CloudWatch + X-Ray emulado)
  - OpenTelemetry Collector
  - PostgreSQL
  - Auth Service
- [ ] Criar `docker/docker-compose.vps.yml` (VPS):
  - Prometheus + Grafana + Loki + Tempo
  - PostgreSQL
  - Auth Service
- [ ] Criar `docker/ecs-task-definition.json` (AWS):
  - Auth Service container
  - X-Ray Daemon sidecar
  - CloudWatch Logs config
  - Secrets Manager references
- [ ] Health check em produção (ECS: `CMD-SHELL curl -f http://localhost:8000/health`)
- [ ] **Documentar** `docker-compose*.yml` e `ecs-task-definition.json`

### Fase 11: Testes e Validação (Dia 7-8)
- [ ] Testes unitários de `jwt_service.py`
- [ ] Testes unitários de `auth_service.py`
- [ ] Testes unitários de models Pydantic
- [ ] Testes de integração de endpoints auth
- [ ] Testes de integração de CRUD usuarios
- [ ] Testes de observabilidade (métricas sendo emitidas)
- [ ] Testes de segurança (SQL injection, XSS)
- [ ] Verificar cobertura > 80%
- [ ] Verificar mypy strict passando
- [ ] Verificar black/isort aplicados

### Fase 12: Documentação e Finalização (Dia 8)
- [ ] Configurar OpenAPI/Swagger docs
- [ ] Atualizar `README.md` com instruções completas
- [ ] Criar `docs/observability.md` com guia de stacks
- [ ] Documentar switch entre stacks (dev/vps/prod)
- [ ] Criar runbook de troubleshooting
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

## Validação e Critérios de Aceitação

### Test-First
- [ ] Todo método novo tem um teste que falha antes da implementação
- [ ] Commits separam `RED (teste)` de `GREEN (implementação)`
- [ ] Cobertura de testes > 80%
- [ ] Testes são F.I.R.S.T

### Documentação
- [ ] Todo arquivo `.py` tem docstring no topo
- [ ] Todo método público tem docstring com intenção + exemplo
- [ ] Docstrings explicam WHY, não WHAT
- [ ] README.md cobre setup, run, test, deploy
- [ ] `docs/observability.md` documenta stacks

### Observabilidade
- [ ] `ENV=development` usa Floci (CloudWatch + X-Ray emulado)
- [ ] `ENV=vps` usa Prometheus + Grafana + Loki + Tempo
- [ ] `ENV=production` usa CloudWatch + X-Ray nativo
- [ ] Endpoint `/metrics` expõe métricas Prometheus
- [ ] Endpoint `/health` responde 200
- [ ] Logs são estruturados em JSON com `timestamp`, `level`, `service`, `trace_id`
- [ ] Métricas de duração emitidas para toda operação de I/O
- [ ] Tracing distribuído propagado via OpenTelemetry / X-Ray

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

### Deploy
- [ ] Docker Compose funciona em VPS (Hostinger)
- [ ] ECS Fargate deployável na AWS
- [ ] Health checks configurados nos dois ambientes
- [ ] Variáveis de ambiente determinam stack sem mudar código

### Técnico
- [ ] Endpoints respondem em < 200ms
- [ ] Database connection pool funciona corretamente
- [ ] Async operations não bloqueiam
- [ ] Requisições concorrentes são tratadas
- [ ] Schema Pydantic valida entrada
- [ ] Erros retornam formato padronizado
- [ ] mypy strict passa sem erros

### Segurança
- [ ] Senhas nunca são expostas em logs
- [ ] JWT tokens são assinados corretamente
- [ ] Token inválido retorna 401
- [ ] Token expirado retorna 401
- [ ] SQL injection prevenido via SQLAlchemy
- [ ] Secrets gerenciados via AWS Secrets Manager (prod) ou `.env` (dev/vps)

### Código (Clean Code)
- [ ] Funções têm 4-20 linhas
- [ ] Arquivos têm < 500 linhas
- [ ] Nomes únicos (< 5 grep hits)
- [ ] Sem sufixos genéricos (Handler, Manager, Data, Utils)
- [ ] Tipo estrito (mypy strict) — sem `Any`, sem `dict` genérico
- [ ] Early returns — max 2 níveis de indentação
- [ ] DRY — zero código duplicado, constantes em Settings
- [ ] Injeção de dependências via construtor/Depends
- [ ] Anti-corruption layer — bibliotecas terceiras encapsuladas
- [ ] Mensagens de erro com valor ofensivo + formato esperado
- [ ] Idempotência em endpoints de mutação (register, refresh, logout)
- [ ] Docstrings em funções públicas (WHY, não WHAT)
- [ ] Imports no topo do arquivo
- [ ] black e isort configurados

---

## Comandos de Desenvolvimento

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar em desenvolvimento (Floci)
OBSERVABILITY_STACK=floci uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Rodar em modo VPS
OBSERVABILITY_STACK=vps uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Rodar em modo produção (AWS)
OBSERVABILITY_STACK=aws uvicorn app.main:app --host 0.0.0.0 --port 8000

# Formatar código
black app tests
isort app tests

# Verificar tipos
mypy app

# Rodar testes
pytest tests -v --cov=app --cov-report=html

# Rodar testes específicos
pytest tests/unit/test_jwt_service.py -v

# Rodar com docker (dev)
docker compose -f docker/docker-compose.yml up -d

# Rodar com docker (VPS)
docker compose -f docker/docker-compose.vps.yml up -d

# Verificar métricas
curl http://localhost:8000/metrics

# Verificar health
curl http://localhost:8000/health
```

---

## Próximos Passos

Após completar este serviço:

1. Integrar com API Gateway
2. Testar autenticação end-to-end com tracing distribuído
3. Documentar endpoints no Swagger/OpenAPI
4. Criar scripts de seed para testes
5. Configurar CloudWatch Dashboards (AWS) / Grafana (VPS)
6. Configurar alarmes de observabilidade

---

## Referências

- `PROJECT_CONTEXT.md` - Arquitetura geral
- `CLAUDE.md` - Regras de código
- `plans/observability/plano-execucao.md` - Plano global de observabilidade
- `plano-geral-execucao.md` - Roadmap global
