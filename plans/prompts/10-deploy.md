# Fase 10: Deploy e Containerização

Execute este prompt para implementar a **Fase 10** do Auth Service.

## Pré-condições (obrigatório)
Antes de executar qualquer ação, considere documentação e regras em:
- `docs/2-principios-norteadores.md`
- `docs/3-arquitetura.md`
- `plans/3-validacao.md`

## Objetivo
Criar configs de deploy para dev (Floci), VPS (open-source) e AWS (ECS).

## Regras
- **Dual-stack**: mesmo código, stack definida por `OBSERVABILITY_STACK`
- **Health check**: configurado em todos os ambientes
- **Segurança**: secrets via .env (dev/vps) ou Secrets Manager (AWS)

## Tarefas

### 1. docker/docker-compose.yml (dev)
```yaml
services:
  floci:
    image: localstack/localstack:latest
    environment:
      SERVICES: cloudwatch,logs,xray
      AWS_ACCESS_KEY_ID: test
      AWS_SECRET_ACCESS_KEY: test
    ports: ["4566:4566"]
  
  otel-collector:
    image: otel/opentelemetry-collector-contrib:latest
    environment:
      AWS_ACCESS_KEY_ID: test
      AWS_SECRET_ACCESS_KEY: test
      AWS_REGION: us-east-1
      AWS_ENDPOINT_URL: http://floci:4566
  
  postgres:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: safehire_auth
      POSTGRES_PASSWORD: postgres
    ports: ["5432:5432"]
  
  auth-service:
    build: ..
    ports: ["8000:8000"]
    environment:
      OBSERVABILITY_STACK: floci
      FLOCI_ENDPOINT: http://floci:4566
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/safehire_auth
    depends_on: [postgres, floci]
```

### 2. docker/docker-compose.vps.yml
Prometheus + Grafana + Loki + Tempo + PostgreSQL + Auth Service.

### 3. docker/ecs-task-definition.json
- Auth Service container (port 8000)
- X-Ray Daemon sidecar (port 2000 UDP)
- CloudWatch Logs config
- Secrets Manager references for DATABASE_URL e JWT_SECRET_KEY
- Health check: `CMD-SHELL curl -f http://localhost:8000/health`

### 4. Documentar
Adicionar docstring no topo de cada arquivo de configuração.

## Critérios de Aceitação
- [ ] `docker compose -f docker/docker-compose.yml up -d` sobe sem erros
- [ ] `curl http://localhost:8000/health` → 200 dentro do container
- [ ] `curl http://localhost:4566/_localstack/health` → Floci ativo
- [ ] Task definition ECS é válida JSON
- [ ] Variáveis de ambiente determinam stack sem mudar código

## TodoList
- Revise as implementações e se tudo passou atualize:
    - `plans/2-todolist.md`
    - `plans/1-roadmap.md`
