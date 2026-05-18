# Observabilidade — Stacks

O SafeHire Auth Service suporta três stacks de observabilidade definidas pela variável `OBSERVABILITY_STACK`.

## Escolha da Stack

| Stack | Ambiente | Métricas | Tracing | Logs |
|-------|----------|----------|---------|------|
| `floci` | Desenvolvimento local | CloudWatch (LocalStack) | X-Ray (LocalStack) | JSON stdout |
| `vps` | VPS / Self-hosted | Prometheus | OpenTelemetry | JSON stdout → Loki |
| `aws` | Produção AWS | CloudWatch | X-Ray (AWS) | CloudWatch Logs |

## Configuração

A stack é definida em `OBSERVABILITY_STACK` (padrão: `floci`). Campos adicionais:

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `FLOCI_ENDPOINT` | `http://floci:4566` | Endpoint LocalStack |
| `XRAY_DAEMON_ADDRESS` | `localhost:2000` | Endpoint do daemon X-Ray |
| `PROMETHEUS_URL` | `http://localhost:9090` | Endpoint Prometheus |
| `LOKI_URL` | `http://localhost:3100` | Endpoint Loki |
| `TEMPO_URL` | `http://localhost:3200` | Endpoint Tempo |
| `LOG_LEVEL` | `INFO` | Nível de log |
| `LOG_FORMAT` | `json` | Formato (json ou text) |

## Floci (Dev)

Usa LocalStack para emular AWS CloudWatch e X-Ray localmente.

```bash
docker compose -f docker/docker-compose.yml up -d
```

- Métricas → CloudWatch via `http://floci:4566`
- Tracing → X-Ray via daemon em `floci:2000`
- Logs → JSON estruturado no stdout

## VPS (Open Source)

Usa stack open-source auto-hospedada.

```bash
docker compose -f docker/docker-compose.vps.yml up -d
```

- Métricas → Prometheus (`http://prometheus:9090`)
- Tracing → OpenTelemetry Collector → Tempo
- Logs → JSON → Loki via Promtail
- Dashboard → Grafana (`http://localhost:3000`, admin/admin)

## AWS (Produção)

Usa serviços gerenciados AWS.

- Métricas → CloudWatch Metrics
- Tracing → AWS X-Ray
- Logs → CloudWatch Logs

Deploy via ECS Fargate (task definition em `docker/ecs-task-definition.json`).

## Health Check

Todas as stacks expõem:

```bash
curl http://localhost:8001/health   # {"status": "ok", "service": "SafeHire Auth Service"}
curl http://localhost:8001/metrics  # métricas Prometheus
curl http://localhost:8001/docs     # Swagger UI
```
