# Plano de Execução — Arquitetura

## Arquitetura do Serviço

```
auth-service/
├── app/
│   ├── __init__.py
│   ├── main.py                  # Entry point FastAPI + observability init
│   ├── config.py                # Configurações (env vars + observability stack)
│   ├── database.py              # Conexão PostgreSQL
│   ├── models/                  # Pydantic models
│   │   ├── __init__.py
│   │   ├── usuario.py           # Request/Response schemas
│   │   └── auth.py              # Token schemas
│   ├── schemas/                 # SQLAlchemy ORM
│   │   ├── __init__.py
│   │   └── usuario.py           # Usuario ORM model
│   ├── repositories/            # Data access layer
│   │   ├── __init__.py
│   │   └── usuario_repo.py      # UsuarioRepository
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Auth business logic
│   │   └── jwt_service.py       # JWT operations
│   ├── routes/                  # API endpoints
│   │   ├── __init__.py
│   │   ├── usuarios.py          # Usuario CRUD endpoints
│   │   └── auth.py              # Auth endpoints
│   ├── middleware/              # Custom middleware
│   │   ├── __init__.py
│   │   ├── auth.py              # Auth middleware
│   │   └── observability.py     # Metrics + tracing + logging middleware
│   └── observability/           # Observability layer
│       ├── __init__.py
│       ├── config.py            # ObservabilityConfig (stack-aware)
│       ├── factory.py           # Factory: dev(floci) / vps(otel) / aws(cloudwatch)
│       ├── metrics.py           # Padrão: CloudWatch via boto3 / Prometheus
│       ├── tracing.py           # Padrão: X-Ray via Floci / OpenTelemetry
│       └── logging.py           # Logger estruturado JSON
├── tests/
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── unit/                    # Unit tests
│   │   ├── __init__.py
│   │   ├── test_jwt_service.py
│   │   ├── test_password_hash.py
│   │   ├── test_models.py
│   │   ├── test_auth_service.py
│   │   └── test_observability.py
│   ├── integration/             # Integration tests
│   │   ├── __init__.py
│   │   ├── test_auth_flow.py
│   │   └── test_usuario_crud.py
│   └── fakes/                   # Fake implementations
│       ├── __init__.py
│       ├── fake_database.py
│       └── fake_postgres.py
├── docker/                      # Docker configs
│   ├── docker-compose.yml       # Dev stack (Floci + PostgreSQL + app)
│   ├── docker-compose.vps.yml   # VPS stack (Grafana/Prometheus/Loki/Tempo)
│   └── ecs-task-definition.json # AWS ECS Fargate
├── Dockerfile
├── requirements.txt
├── .env.example
├── pyproject.toml               # black, isort, pytest, mypy configs
├── README.md
└── CLAUDE.md
```

---

## Triple-Stack Observability

```
              ┌─────────────────────┐
              │   Auth Service       │
              │   (FastAPI + OTEL)   │
              └──────────┬──────────┘
                         │
     ┌───────────────────┼───────────────────┐
     │                   │                   │
     ▼                   ▼                   ▼
┌────────────┐   ┌──────────────┐   ┌──────────────┐
│ DEV (Floci) │   │ VPS (Self)   │   │ PROD (AWS)   │
│ :4566       │   │ :9090/:3001   │   │ CloudWatch   │
├────────────┤   ├──────────────┤   ├──────────────┤
│ CloudWatch │   │ Prometheus   │   │ CloudWatch   │
│ Metrics    │   │ Grafana      │   │ Metrics+Logs │
│ Logs       │   │ Loki         │   │ X-Ray        │
│ X-Ray      │   │ Tempo        │   │ Synthetics   │
└────────────┘   └──────────────┘   └──────────────┘
```

A variável `OBSERVABILITY_STACK=floci|vps|aws` determina a stack ativa sem mudar código.

---
