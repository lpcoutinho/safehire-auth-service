# Plano de Execução — Roadmap

## Roadmap de Implementação

### Pré-condição para toda fase
- [ ] **Testes existem antes do código**: para cada método novo, o teste deve ser escrito **primeiro**.
- [ ] **Documentação**: docstring no topo do arquivo + docstring em cada método público.
- [ ] **Observabilidade**: logging estruturado + métricas de duração + tracing.
- [ ] **Git Flow**: cada fase implementada em uma branch `feature/*` com PR para `develop`.

---

### Fase 0: Git Flow Setup
- [x] Criar branch `develop` a partir de `main`
- [x] Criar branch `staging` a partir de `main`
- [ ] Proteger `main` no GitHub (PR + CI + 1 approval, sem push direto)
- [ ] Proteger `staging` no GitHub (PR + CI + 1 approval, sem push direto)
- [x] Criar `.github/PULL_REQUEST_TEMPLATE.md`
- [x] Criar `plans/git-flow.md`
- [x] Atualizar `plans/1-roadmap.md` com Fase 0
- [x] Atualizar `plans/2-todolist.md` com Git Flow checklist
- [x] Atualizar `plans/3-validacao.md` com Git Flow validation
- [x] Atualizar `docs/2-principios-norteadores.md` com Princípio 6
- [x] Atualizar `docs/4-comandos.md` com comandos Git Flow
- [x] Atualizar prompts em `plans/prompts/` com referência ao `plans/git-flow.md`

### Fase 1: Configuração Base (Dia 1)
- [x] Criar estrutura de pastas do projeto
- [x] Criar `pyproject.toml` com configs (black, isort, pytest, mypy)
- [x] Criar `requirements.txt` com todas as dependências (incluindo observabilidade)
- [x] Criar `Dockerfile` otimizado
- [x] Criar `.env.example` com todas as variáveis (incluindo observabilidade)
- [x] Criar `conftest.py` com fixtures básicos
- [x] Configurar `.gitignore` apropriado
- [x] **Documentar** cada arquivo criado com docstring

### Fase 2: Camada de Configuração e Database (Dia 1-2)
- [x] Implementar `config.py` com Pydantic Settings + `OBSERVABILITY_STACK`
- [x] Implementar `database.py` com async PostgreSQL connection
- [ ] Criar schema `auth_schema` no PostgreSQL
- [x] Implementar ORM models em `schemas/usuario.py`
- [x] Implementar `fake_database.py` para testes
- [x] [TEST] `tests/unit/test_config.py` — validar leitura de env vars e stack
- [x] [TEST] `tests/unit/test_database.py` — validar criação de engine e session
- [x] **Documentar** config.py, database.py, schemas/usuario.py

### Fase 3: Camada de Models Pydantic (Dia 2)
- [x] Implementar `models/usuario.py`:
  - `UsuarioCreateRequest`
  - `UsuarioResponse`
  - `RecrutadorCreateRequest`
  - `CandidatoCreateRequest`
- [x] Implementar `models/auth.py`:
  - `LoginRequest`
  - `LoginResponse` (access_token, refresh_token)
  - `RefreshTokenRequest`
  - `RefreshTokenResponse`
- [x] [TEST] `tests/unit/test_models.py` — validar validação de cada schema (escrito **antes** da implementação)
- [x] **Documentar** cada modelo com docstring

### Fase 4: Camada de Repositories (Dia 2-3)
- [x] Implementar `repositories/usuario_repo.py`:
  - `UsuarioRepository.criar(usuario) → Usuario`
  - `UsuarioRepository.buscar_por_email(email) → Usuario | None`
  - `UsuarioRepository.buscar_por_id(id) → Usuario | None`
  - `UsuarioRepository.atualizar(usuario) → Usuario`
  - `UsuarioRepository.listar_ativos() → list[Usuario]`
- [x] Implementar FakeDatabase para testes
- [x] [TEST] `tests/unit/test_usuario_repo.py` — 8 testes (criar, buscar por email, buscar por id, listar ativos, atualizar)
- [ ] **Observabilidade**: cada método de I/O emite métrica de duração
- [x] **Documentar** repository com docstring

### Fase 5: Camada de Services (Dia 3-4)
- [x] Implementar `services/jwt_service.py`:
  - `criar_access_token(usuario_id) → str`
  - `criar_refresh_token(usuario_id) → str`
  - `verificar_token(token) → TokenPayload`
- [x] Implementar `services/auth_service.py`:
  - `registrar(data) → tuple[Usuario, str, str]`
  - `autenticar(data) → tuple[Usuario, str, str]`
  - `refresh(refresh_token) → tuple[str, str]`
  - `buscar_usuario(id) → Usuario`
- [x] [TEST] `tests/unit/test_jwt_service.py` — 4 testes (access, refresh, inválido, expirado)
- [x] [TEST] `tests/unit/test_auth_service.py` — 9 testes (registro, auth, refresh, busca) com FakeRepository
- [ ] **Observabilidade**: cada método loga entrada/saída + métrica de duração
- [x] **Documentar** cada método público com docstring

### Fase 6: Camada de Routes (Dia 4-5)
- [x] Implementar `routes/usuarios.py`:
  - `GET /usuarios/me` — Perfil do usuário logado
  - `PUT /usuarios/me` — Atualizar perfil
  - `GET /usuarios/{id}` — Buscar usuário
- [x] Implementar `routes/auth.py`:
  - `POST /auth/register` — Registro (com 409 para email duplicado)
  - `POST /auth/login` — Login (com 401 para credenciais inválidas)
  - `POST /auth/refresh` — Refresh token (com 401 para token inválido)
- [x] [TEST] `tests/integration/test_auth_flow.py` — 7 testes com SQLite in-memory
- [x] [TEST] `tests/integration/test_usuario_crud.py` — 2 testes (401 sem token, 404 id inexistente)
- [ ] **Observabilidade**: middleware de métricas (requisições, latência, erros)
- [x] **Documentar** cada endpoint com docstring

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
- [x] Criar `app/observability/` com:
  - `config.py` — ObservabilityConfig (stack-aware, pydantic-settings, env_prefix=OBSERVABILITY_)
  - `factory.py` — init_observability() com dispatch por stack via settings.observability_stack
  - `metrics.py` — CloudWatchMetrics (Floci/AWS, boto3) + LocalMetrics (VPS, logging)
  - `tracing.py` — XRayTracer (Floci/AWS, aws_xray_sdk) + LocalTracer (VPS, logging)
  - `logging.py` — logger estruturado JSON (python-json-logger)
- [x] Expor endpoint `/metrics` (Prometheus via prometheus-fastapi-instrumentator)
- [x] [TEST] `tests/unit/test_observability.py` — 9 testes (config, CloudWatchMetrics, LocalMetrics, logger JSON, factory dispatch)
- [x] **Documentar** cada módulo de observabilidade

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
- [ ] Fazer merge de `develop` para `staging` e de `staging` para `main`

---
