# Plano de Execução — Validação

## Validação e Critérios de Aceitação

### Test-First
- [ ] Todo método novo tem um teste que falha antes da implementação
- [ ] Commits separam `RED (teste)` de `GREEN (implementação)`
- [ ] Cobertura de testes > 80%
- [ ] Testes são F.I.R.S.T

### Documentação
- [ ] Todo arquivo `.py` tem docstring no topo
- [ ] Todo método público tem docstring com intenção + exemplo
- [ ] Docstrings explicam WHY, não WHAT
- [ ] README.md cobre setup, run, test, deploy
- [ ] `docs/observability.md` documenta stacks

### Observabilidade
- [ ] `ENV=development` usa Floci (CloudWatch + X-Ray emulado)
- [ ] `ENV=vps` usa Prometheus + Grafana + Loki + Tempo
- [ ] `ENV=production` usa CloudWatch + X-Ray nativo
- [ ] Endpoint `/metrics` expõe métricas Prometheus
- [ ] Endpoint `/health` responde 200
- [ ] Logs são estruturados em JSON com `timestamp`, `level`, `service`, `trace_id`
- [ ] Métricas de duração emitidas para toda operação de I/O
- [ ] Tracing distribuído propagado via OpenTelemetry / X-Ray

### Funcional
- [ ] Usuário pode se registrar com email e senha válidos
- [ ] Senha é hasheada com bcrypt antes de armazenar
- [ ] Login retorna access_token e refresh_token
- [ ] Access token expira em 30 minutos
- [ ] Refresh token pode renovar access token
- [ ] Logout invalida refresh token
- [ ] Dados de usuário são isolados no `auth_schema`
- [ ] Validação de email único funciona
- [ ] Validação de senha forte (mínimo 8 caracteres)

### Deploy
- [ ] Docker Compose funciona em VPS (Hostinger)
- [ ] ECS Fargate deployável na AWS
- [ ] Health checks configurados nos dois ambientes
- [ ] Variáveis de ambiente determinam stack sem mudar código

### Técnico
- [ ] Endpoints respondem em < 200ms
- [ ] Database connection pool funciona corretamente
- [ ] Async operations não bloqueiam
- [ ] Requisições concorrentes são tratadas
- [ ] Schema Pydantic valida entrada
- [ ] Erros retornam formato padronizado
- [ ] mypy strict passa sem erros

### Segurança
- [ ] Senhas nunca são expostas em logs
- [ ] JWT tokens são assinados corretamente
- [ ] Token inválido retorna 401
- [ ] Token expirado retorna 401
- [ ] SQL injection prevenido via SQLAlchemy
- [ ] Secrets gerenciados via AWS Secrets Manager (prod) ou `.env` (dev/vps)

### Código (Clean Code)
- [ ] Funções têm 4-20 linhas
- [ ] Arquivos têm < 500 linhas
- [ ] Nomes únicos (< 5 grep hits)
- [ ] Sem sufixos genéricos (Handler, Manager, Data, Utils)
- [ ] Tipo estrito (mypy strict) — sem `Any`, sem `dict` genérico
- [ ] Early returns — max 2 níveis de indentação
- [ ] DRY — zero código duplicado, constantes em Settings
- [ ] Injeção de dependências via construtor/Depends
- [ ] Anti-corruption layer — bibliotecas terceiras encapsuladas
- [ ] Mensagens de erro com valor ofensivo + formato esperado
- [ ] Idempotência em endpoints de mutação (register, refresh, logout)
- [ ] Docstrings em funções públicas (WHY, não WHAT)
- [ ] Imports no topo do arquivo
- [ ] black e isort configurados

---
