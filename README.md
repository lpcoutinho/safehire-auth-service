# SafeHire Auth Service

Serviço central de autenticação e autorização da plataforma SafeHire AI.

## Stack

- **Framework:** FastAPI (async, Python 3.11+)
- **Banco:** PostgreSQL (schema `auth_schema`)
- **ORM:** SQLAlchemy 2.0 asyncio
- **Validação:** Pydantic v2
- **Auth:** JWT (python-jose) + bcrypt (passlib)
- **Observabilidade:** Floci (dev) | Prometheus/Grafana (VPS) | CloudWatch/X-Ray (AWS)

## Quick Start

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Subir servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# 3. Verificar health
curl http://localhost:8001/health

# 4. Ver documentação interativa
open http://localhost:8001/docs
```

## Endpoints

### Auth
| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/auth/register` | Registro de usuário (email único) |
| POST | `/auth/login` | Login — retorna access + refresh tokens |
| POST | `/auth/refresh` | Renova par de tokens |

### Usuários
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/usuarios/me` | Perfil do usuário logado |
| PUT | `/usuarios/me` | Atualizar perfil |
| GET | `/usuarios/{id}` | Buscar usuário por ID |

### Observabilidade
| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/health` | Health check |
| GET | `/metrics` | Métricas Prometheus |
| GET | `/docs` | Swagger UI |

## Testes

```bash
pytest -v --cov=app
mypy app/ --strict
black app/ tests/ --check
isort app/ tests/ --check
```

## Deploy

### Dev (Floci)
```bash
docker compose -f docker/docker-compose.yml up -d
```

### VPS (Open Source)
```bash
docker compose -f docker/docker-compose.vps.yml up -d
```

### AWS (ECS Fargate)
Task definition em `docker/ecs-task-definition.json`.

## Observabilidade

O serviço suporta 3 stacks de observabilidade definidas via variável `OBSERVABILITY_STACK`:

- `floci` (dev local) — usa LocalStack para emular CloudWatch + X-Ray
- `vps` — usa Prometheus + Grafana + Loki + Tempo self-hosted
- `aws` — produção AWS com CloudWatch + X-Ray

Detalhes em [`docs/observability.md`](docs/observability.md).
