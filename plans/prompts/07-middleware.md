# Fase 7: Middleware e Security

Execute este prompt para implementar a **Fase 7** do Auth Service.

## Pré-condições (obrigatório)
Antes de executar qualquer ação, considere documentação e regras em:
- `docs/2-principios-norteadores.md`
- `docs/3-arquitetura.md`
- `plans/3-validacao.md`
- `plans/git-flow.md`

## Objetivo
Implementar middleware de autenticação e observabilidade.

## Regras
- **TEST-FIRST**: teste antes da implementação
- **Early returns**: tratar casos de erro primeiro (token ausente, inválido)
- **Injeção**: JWTService injetado via instância, não global

## Tarefas

### 1. [TEST] tests/unit/test_middleware_auth.py (escrever PRIMEIRO)
Testar:
- `get_usuario_atual` sem header: 401
- `get_usuario_atual` com token inválido: 401
- `get_usuario_atual` com token de refresh (não access): 401

### 2. app/middleware/auth.py
```python
"""Middleware de autenticação via JWT Bearer token.
Extrai usuário atual do token para injeção via Depends."""
from uuid import UUID
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.repositories.usuario_repo import UsuarioRepository
from app.schemas.usuario import Usuario
from app.services.jwt_service import JWTService

_security = HTTPBearer(auto_error=False)
_jwt_service = JWTService()

async def get_usuario_atual(
    credentials: HTTPAuthorizationCredentials | None = Depends(_security),
    session: AsyncSession = Depends(get_session),
) -> Usuario:
    if credentials is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token de acesso não fornecido")
    try:
        payload = _jwt_service.verificar_token(credentials.credentials)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    if payload.tipo != "access":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token fornecido não é um access token")
    repo = UsuarioRepository(session)
    usuario = await repo.buscar_por_id(UUID(payload.sub))
    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário não encontrado")
    return usuario
```

### 3. [TEST] tests/unit/test_middleware_observability.py (escrever PRIMEIRO)
Testar que o middleware de observabilidade:
- Registra métricas no endpoint /metrics
- Adiciona correlation_id nos responses

### 4. app/middleware/observability.py
```python
"""Middleware de observabilidade: métricas Prometheus e tracing OpenTelemetry."""
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi import FastAPI

instrumentator = Instrumentator()

def setup_observability_middleware(app: FastAPI) -> None:
    instrumentator.instrument(app).expose(app)
```

### 5. Implementar
Depois dos testes passarem (RED), implementar os arquivos acima (GREEN).

## Critérios de Aceitação
- [ ] `pytest tests/unit/test_middleware_auth.py -v` passa
- [ ] `curl -v http://localhost:8000/usuarios/me` sem token → 401
- [ ] `curl http://localhost:8000/metrics` → 200 com métricas Prometheus
- [ ] `mypy app/middleware/` passa sem erros
- [ ] Docstring em cada arquivo e função pública

## TodoList
- Revise as implementações e se tudo passou atualize:
    - `plans/2-todolist.md`
    - `plans/1-roadmap.md`
- Crie um PR da sua branch para `develop` e atualize os plans após o merge
