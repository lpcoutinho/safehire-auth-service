# Fase 8: Observability Layer

Execute este prompt para implementar a **Fase 8** do Auth Service.

## Pré-condições (obrigatório)
Antes de executar qualquer ação, considere documentação e regras em:
- `docs/2-principios-norteadores.md`
- `docs/3-arquitetura.md`
- `plans/3-validacao.md`

## Objetivo
Criar camada de observabilidade com suporte a Floci (dev), open-source (VPS) e CloudWatch (AWS).

## Regras
- **TEST-FIRST**: teste antes da implementação
- **Factory pattern**: criar cliente correto baseado em `OBSERVABILITY_STACK`
- **Anti-Corruption Layer**: `boto3` e `opentelemetry` encapsulados
- **Configurável**: sem hardcoded endpoints

## Tarefas

### 1. [TEST] tests/unit/test_observability.py (escrever PRIMEIRO)
Testar:
- Factory retorna `CloudWatchMetrics` quando stack=floci
- Factory retorna `LocalMetrics` quando stack=vps
- `CloudWatchMetrics.put_metric()` não levanta exceção
- Logger estruturado produz JSON válido

### 2. app/observability/config.py
```python
"""Configuração stack-aware de observabilidade."""
from pydantic_settings import BaseSettings

class ObservabilityConfig(BaseSettings):
    stack: str = "floci"
    floci_endpoint: str = "http://floci:4566"
    xray_daemon_address: str = "floci:2000"
    prometheus_url: str = "http://prometheus:9090"
    loki_url: str = "http://loki:3100"
    tempo_url: str = "http://tempo:3200"
    aws_region: str = "us-east-1"
    cloudwatch_log_group: str = "/aws/ecs/auth-service"
    log_level: str = "INFO"
    trace_sampling_rate: float = 1.0
    model_config = {"env_prefix": "OBSERVABILITY_"}

obs_config = ObservabilityConfig()
```

### 3. app/observability/factory.py
```python
"""Factory para criar clientes de observabilidade por stack (floci|vps|aws)."""

def create_metrics(stack: str, service_name: str):
    if stack in ("floci", "aws"):
        from app.observability.metrics import CloudWatchMetrics
        endpoint = obs_config.floci_endpoint if stack == "floci" else None
        return CloudWatchMetrics(f"SafeHire/{service_name}", endpoint_url=endpoint)
    return LocalMetrics(service_name)

def create_logger(stack: str, service_name: str):
    ...

def create_tracer(stack: str, service_name: str):
    ...
```

### 4. app/observability/metrics.py
Implementar:
- `CloudWatchMetrics`: encapsula `boto3.client('cloudwatch')`
- `LocalMetrics`: implementação dummy para VPS (usa logging)

### 5. app/observability/tracing.py
Implementar:
- `XRayTracer`: encapsula `aws_xray_sdk`
- `LocalTracer`: implementação dummy para VPS

### 6. app/observability/logging.py
Implementar logger estruturado JSON com campos: timestamp, level, service, trace_id, span_id.

### 7. Implementar
Depois dos testes passarem (RED), implementar os arquivos acima (GREEN).

## Critérios de Aceitação
- [ ] `pytest tests/unit/test_observability.py -v` passa
- [ ] `OBSERVABILITY_STACK=floci` usa CloudWatch via endpoint configurável
- [ ] `OBSERVABILITY_STACK=vps` usa implementação local
- [ ] `OBSERVABILITY_STACK=aws` usa CloudWatch nativo
- [ ] `mypy app/observability/` passa sem erros
- [ ] Docstring em cada módulo e função pública

## TodoList
- Revise as implementações e se tudo passou atualize:
    - `plans/2-todolist.md`
    - `plans/1-roadmap.md`
