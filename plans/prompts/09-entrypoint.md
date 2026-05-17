# Fase 9: Entry Point e Orquestração

Execute este prompt para implementar a **Fase 9** do Auth Service.

## Pré-condições (obrigatório)
Antes de executar qualquer ação, considere documentação e regras em:
- `docs/2-principios-norteadores.md`
- `docs/3-arquitetura.md`
- `plans/3-validacao.md`
- `plans/git-flow.md`

## Objetivo
Criar o entry point FastAPI orquestrando todos os módulos.

## Regras
- **CORS configurável** via `ALLOWED_ORIGINS`
- **Observabilidade**: middleware registrado na inicialização
- **Health check**: endpoint `/health`

## Tarefas

### 1. [TEST] tests/integration/test_health.py (escrever PRIMEIRO)
Testar:
- `GET /health`: 200 + status + service name
- `GET /docs`: 200 (Swagger UI)
- `GET /metrics`: 200 (Prometheus metrics)

### 2. app/main.py
```python
"""Entry point do Auth Service FastAPI.
Orquestra configuração, rotas, middleware e observabilidade."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import auth, usuarios
from app.middleware.observability import setup_observability_middleware

app = FastAPI(title=settings.app_name, version="0.1.0", debug=settings.debug)

origins = [o.strip() for o in settings.allowed_origins.split(",")]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])

setup_observability_middleware(app)

@app.get("/health")
async def health():
    return {"status": "ok", "service": settings.app_name}
```

### 3. Implementar
Depois dos testes passarem (RED), implementar o arquivo acima (GREEN).

## Critérios de Aceitação
- [ ] `pytest tests/integration/test_health.py -v` passa
- [ ] `uvicorn app.main:app` sobe sem erros
- [ ] `curl http://localhost:8000/health` → 200
- [ ] `curl http://localhost:8000/docs` → 200 (Swagger)
- [ ] `mypy app/main.py` passa
- [ ] Docstring no topo do arquivo

## TodoList
- Revise as implementações e se tudo passou atualize:
    - `plans/2-todolist.md`
    - `plans/1-roadmap.md`
- Crie um PR da sua branch para `develop` e atualize os plans após o merge
