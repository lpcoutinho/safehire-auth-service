# Fase 12: Documentação e Finalização

Execute este prompt para implementar a **Fase 12** do Auth Service.

## Pré-condições
- Fase 11 concluída (testes passando, coverage ≥ 80%)
- Consulte `docs/2-principios-norteadores.md` (documentação)

## Objetivo
Finalizar documentação do serviço: README, docs, OpenAPI, runbook.

## Regras
- **Docstrings**: WHY, não WHAT
- **README**: deve permitir que qualquer dev suba o projeto em < 5 minutos
- **docs/observability.md**: guia de troca entre stacks

## Tarefas

### 1. README.md
```markdown
# SafeHire Auth Service

Serviço central de autenticação e autorização.

## Stack
- FastAPI + SQLAlchemy async + PostgreSQL
- JWT (python-jose) + bcrypt (passlib)
- Observabilidade: Floci (dev) | Prometheus/Grafana (VPS) | CloudWatch (AWS)

## Quick Start
```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8001
curl http://localhost:8001/health
```

## Testes
```bash
pytest -v --cov=app
```

## Deploy
- Dev: `docker compose -f docker/docker-compose.yml up -d`
- VPS: `docker compose -f docker/docker-compose.vps.yml up -d`
- AWS: ECS Fargate (task definition em `docker/ecs-task-definition.json`)
```
```

### 2. docs/observability.md
Guia explicando como trocar entre stacks:
- `OBSERVABILITY_STACK=floci` (dev local, Floci emula AWS)
- `OBSERVABILITY_STACK=vps` (VPS com Prometheus/Grafana/Loki/Tempo)
- `OBSERVABILITY_STACK=aws` (produção AWS com CloudWatch + X-Ray)

### 3. OpenAPI/Swagger
Verificar que `/docs` e `/redoc` estão funcionando (FastAPI gera automaticamente).

### 4. Revisão final
- [ ] Todos os arquivos .py têm docstring no topo
- [ ] Todos os métodos públicos têm docstring
- [ ] Nenhum sufixo genérico (Handler, Manager, Data) nos nomes
- [ ] README.md cobre setup, run, test, deploy
- [ ] `docs/observability.md` documenta stacks
- [ ] `mypy app/ --strict` passa
- [ ] `black app/ tests/ --check` passa
- [ ] `isort app/ tests/ --check` passa
- [ ] `pytest -v --cov=app` → coverage ≥ 80%

## Critérios de Aceitação
- [ ] README.md completo (setup, run, test, deploy)
- [ ] docs/observability.md criado
- [ ] OpenAPI/Swagger acessível em /docs
- [ ] Peer review realizado
- [ ] Todos os critérios de `docs/6-validacao.md` atendidos
