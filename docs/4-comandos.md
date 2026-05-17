# Plano de Execução — Comandos e Referências

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

### Git Flow Commands

```bash
# Criar feature branch a partir de develop
git checkout develop && git pull origin develop
git checkout -b feature/02-config-database develop

# Sincronizar feature branch com develop (rebase)
git checkout feature/02-config-database
git fetch origin develop
git rebase origin/develop

# Publicar branch e criar PR
git push origin feature/02-config-database
gh pr create --base develop --title "Fase 2: Config + Database" --body ""

# Atualizar após merge do PR
git checkout develop && git pull origin develop
git branch -d feature/02-config-database

# Fluxo develop → staging → main (via PR no GitHub)
# gh pr create --base staging --title "Release v0.1.0" --body ""
# gh pr create --base main --title "Release v0.1.0" --body ""
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
