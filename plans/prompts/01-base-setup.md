# Fase 1: Configuração Base

Execute este prompt para implementar a **Fase 1** do Auth Service.

## Pré-condições (obrigatório)
Antes de executar qualquer ação, considere documentação e regras em:
- `docs/2-principios-norteadores.md`
- `docs/3-arquitetura.md`
- `plans/3-validacao.md`

## Objetivo
Criar estrutura de pastas e arquivos de configuração base do projeto.

## Tarefas

### 1. Estrutura de pastas
Criar toda a árvore de diretórios conforme `docs/3-arquitetura.md`.

### 2. pyproject.toml
Criar com configs de black (line-length=88, target py311), isort (profile=black), pytest (testpaths=tests), mypy (strict=true).

### 3. requirements.txt
Incluir dependências:
- **Framework**: fastapi, uvicorn
- **Database**: sqlalchemy[asyncio], asyncpg
- **Validation**: pydantic, pydantic-settings
- **Auth**: python-jose[cryptography], passlib[bcrypt], python-multipart
- **Observability**: prometheus-fastapi-instrumentator, opentelemetry-api, opentelemetry-sdk, opentelemetry-instrumentation-fastapi, opentelemetry-instrumentation-httpx, opentelemetry-exporter-otlp, python-json-logger, boto3, aws-xray-sdk
- **Dev/Test**: httpx, pytest, pytest-asyncio, pytest-cov, black, isort, mypy

### 4. Dockerfile
Otimizado (multi-stage se aplicável), python:3.11-slim, usuário não-root.

### 5. .env.example
Variáveis: DATABASE_URL, JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS, APP_NAME, DEBUG, ENV, ALLOWED_ORIGINS, OBSERVABILITY_STACK, FLOCI_ENDPOINT, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION, XRAY_DAEMON_ADDRESS, PROMETHEUS_URL, LOKI_URL, TEMPO_URL, CLOUDWATCH_LOG_GROUP, TRACE_SAMPLING_RATE, LOG_LEVEL, LOG_FORMAT.

### 6. .gitignore
Incluir: __pycache__/, *.pyc, .venv/, .env, .pytest_cache/, .coverage, htmlcov/, .mypy_cache/, .vscode/, .idea/, *.log, CLAUDE.md

### 7. tests/conftest.py
Fixtures:
- `usuario_fake()` — retorna instância de Usuario com dados válidos
- `client()` — AsyncClient do httpx apontando para app.main:app

### 8. Documentação
**Todo arquivo criado deve ter docstring no topo** explicando sua responsabilidade.

## Critérios de Aceitação
- [x] `pip install -r requirements.txt` instala sem erros
- [x] `pytest -v` roda (pode pular testes que dependem de módulos ainda não implementados)
- [x] `black app/ tests/ --check` passa
- [x] `isort app/ tests/ --check` passa
- [x] `mypy app/` passa
- [x] Todos os arquivos têm docstring

## TodoList
- Revise as implementações e se tudo passou atualize: 
    - `plans/2-todolist.md`
    - `plans/1-roadmap.md`