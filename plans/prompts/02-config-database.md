# Fase 2: Camada de Configuração e Database

Execute este prompt para implementar a **Fase 2** do Auth Service.

## Pré-condições
- Fase 1 concluída (estrutura de pastas + dependências instaladas)
- Consulte `docs/2-principios-norteadores.md` para regras de clean code

## Objetivo
Implementar config, database e ORM models.

## Regras (TEST-FIRST)
**Antes de implementar cada arquivo, escreva o teste que valida seu comportamento.** Commite o teste primeiro (RED), depois a implementação (GREEN).

## Tarefas

### 1. app/config.py
```python
"""Configurações centralizadas via pydantic-settings."""
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    app_name: str = "SafeHire Auth Service"
    debug: bool = True
    env: str = "development"
    allowed_origins: str = "http://localhost:3000"
    observability_stack: str = "floci"  # floci | vps | aws
    floci_endpoint: str = "http://floci:4566"
    aws_region: str = "us-east-1"
    xray_daemon_address: str = "floci:2000"
    log_level: str = "INFO"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

settings = Settings()
```

### 2. [TEST] tests/unit/test_config.py
Testar:
- Leitura de variáveis de ambiente
- Valores default
- Observability stack switching

### 3. app/database.py
```python
"""Conexão assíncrona PostgreSQL via SQLAlchemy."""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from app.config import settings

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def get_session() -> AsyncSession:
    """Yields async session com commit/rollback automático.
    Uso: Depends(get_session) nos endpoints."""
    async with async_session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

### 4. [TEST] tests/unit/test_database.py
Testar criação de engine e session factory.

### 5. app/schemas/usuario.py
```python
"""Modelo ORM SQLAlchemy para tabela usuarios (auth_schema)."""
from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base
from app.models.usuario import TipoUsuario
import uuid
from datetime import datetime

class Usuario(Base):
    __tablename__ = "usuarios"
    __table_args__ = {"schema": "auth_schema"}

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[TipoUsuario] = mapped_column(Enum(TipoUsuario, schema="auth_schema"), nullable=False)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
```

### 6. tests/fakes/fake_database.py
Implementar FakeDatabase com SQLite in-memory para testes.

## Critérios de Aceitação
- [ ] `pytest tests/unit/test_config.py -v` passa
- [ ] `pytest tests/unit/test_database.py -v` passa
- [ ] `mypy app/` não acusa erros nos novos módulos
- [ ] Docstring no topo de cada arquivo
- [ ] Injeção de dependência via parâmetros (sem globais)
