"""Modelo ORM SQLAlchemy para tabela auth_schema.usuarios — colunas, tipos e constraints."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.models.usuario import TipoUsuario


class Usuario(Base):
    """Modelo ORM para tabela auth_schema.usuarios — colunas mapeadas via SQLAlchemy Mapped."""

    __tablename__ = "usuarios"
    __table_args__ = {"schema": "auth_schema"}

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    nome: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[TipoUsuario] = mapped_column(
        Enum(TipoUsuario, schema="auth_schema"), nullable=False
    )
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
