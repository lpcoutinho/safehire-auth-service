# Plano de Execução — Visão Geral

## Visão Geral

O **Auth Service** é o serviço central de autenticação e autorização da plataforma SafeHire AI. Responsável por gerenciar usuários (recrutadores e candidatos), emitir tokens JWT e validar credenciais.

### Propósito
- Gerenciar o ciclo de vida de usuários (registro, login, logout)
- Emitir e validar tokens JWT
- Gerenciar refresh tokens
- Isolar dados de autenticação em schema próprio do PostgreSQL

### Stack Tecnológica
- **Framework**: FastAPI (assíncrono)
- **Linguagem**: Python 3.11+
- **Banco de Dados**: PostgreSQL (schema `auth_schema`)
- **Validação**: Pydantic v2
- **Segurança**: JWT, bcrypt para hashing de senhas
- **Observabilidade (Dev)**: Floci (emulador AWS — CloudWatch Metrics, Logs, X-Ray)
- **Observabilidade (VPS)**: OpenTelemetry Collector → Prometheus/Grafana/Loki/Tempo
- **Observabilidade (AWS)**: CloudWatch Metrics, CloudWatch Logs, AWS X-Ray
- **Coleta**: OpenTelemetry SDK + Prometheus FastAPI Instrumentator
- **Logging**: Estruturado JSON
- **Formatting**: black, isort, mypy strict

---
