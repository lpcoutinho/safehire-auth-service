# Fase 4: Camada de Repositories

Execute este prompt para implementar a **Fase 4** do Auth Service.

## Pré-condições
- Fase 3 concluída (Pydantic models + ORM)
- Consulte `docs/2-principios-norteadores.md` (SRP, injeção de dependências)

## Objetivo
Implementar a camada de acesso a dados (Repository pattern).

## Regras
- **TEST-FIRST**: teste antes do código
- **Injeção de dependência**: UsuarioRepository recebe AsyncSession no construtor
- **SRP**: repository só acessa dados, sem lógica de negócio
- **Observabilidade**: cada método de I/O deve emitir métrica de duração (via wrapper ou decorator futuro)

## Tarefas

### 1. [TEST] tests/unit/test_usuario_repo.py (escrever PRIMEIRO)
Usar `FakeDatabase` (SQLite in-memory) para testar:
- `criar(usuario) → Usuario`: cria e retorna com id gerado
- `buscar_por_email(email) → Usuario | None`: retorna usuário ou None
- `buscar_por_id(id) → Usuario | None`: retorna usuário ou None
- `buscar_por_email(email) → None`: email inexistente
- `buscar_por_id(id) → None`: id inexistente
- `listar_ativos() → list[Usuario]`: só retorna ativos
- `atualizar(usuario) → Usuario`: persiste mudanças

### 2. app/repositories/usuario_repo.py
```python
"""Acesso a dados da entidade Usuario (Repository pattern)."""
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.usuario import Usuario

class UsuarioRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def criar(self, usuario: Usuario) -> Usuario:
        """Persiste novo usuário e retorna com id gerado."""
        self._session.add(usuario)
        await self._session.flush()
        return usuario

    async def buscar_por_email(self, email: str) -> Usuario | None:
        """Busca usuário por email. Retorna None se não existir."""
        query = select(Usuario).where(Usuario.email == email)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def buscar_por_id(self, usuario_id: UUID) -> Usuario | None:
        """Busca usuário por UUID. Retorna None se não existir."""
        query = select(Usuario).where(Usuario.id == usuario_id)
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def listar_ativos(self) -> list[Usuario]:
        """Retorna lista de usuários ativos."""
        query = select(Usuario).where(Usuario.ativo.is_(True))
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def atualizar(self, usuario: Usuario) -> Usuario:
        """Persiste alterações em usuário existente."""
        await self._session.flush()
        return usuario
```

### 3. Implementar
Depois dos testes passarem (RED), implementar o arquivo acima (GREEN).

## Critérios de Aceitação
- [ ] `pytest tests/unit/test_usuario_repo.py -v` passa
- [ ] Nenhum import direto de SQLAlchemy fora do repository
- [ ] `mypy app/repositories/` passa sem erros
- [ ] Docstring no topo do arquivo e em cada método público
