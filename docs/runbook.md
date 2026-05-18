# Runbook — Auth Service Troubleshooting

Guia de diagnóstico e resolução de problemas comuns no SafeHire Auth Service.

## 1. Serviço não sobe

### Sintoma
`uvicorn app.main:app` falha com erro de importação.

### Diagnóstico
```bash
# Verificar dependências
pip list | grep -iE "fastapi|sqlalchemy|pydantic|jose|passlib"

# Verificar sintaxe
python -c "import app.main; print('OK')"

# Verificar mypy
mypy app/ --strict
```

### Causas comuns
- Dependência faltando: `pip install -r requirements.txt`
- Erro de sintaxe: executar `black app/` e `isort app/`

---

## 2. Banco de dados

### Sintoma
`FATAL: database "safehire_auth" does not exist`

### Solução
```bash
createdb safehire_auth
psql -d safehire_auth -f migrations/001_create_auth_schema.sql
```

### Sintoma
`psycopg2.OperationalError: connection to server on socket "/var/run/postgresql/.s.PGSQL.5432"`

### Diagnóstico
```bash
systemctl status postgresql
pg_isready
```

---

## 3. Testes falhando

### Sintoma
`FAILED tests/unit/test_*.py`

### Diagnóstico
```bash
# Rodar testes isoladamente
pytest tests/unit/test_models.py -v

# Com coverage
pytest --cov=app --cov-report=term-missing

# Verificar logs detalhados
pytest -v --tb=long --log-cli-level=DEBUG
```

---

## 4. JWT / Autenticação

### Sintoma
`401 Unauthorized` em toda requisição

### Causas comuns
- `SECRET_KEY` diferente entre emissão e verificação
- Token expirado (access token: 30 min, refresh: 7 dias)
- Header `Authorization: Bearer <token>` mal formatado

### Verificação manual
```bash
# Decodificar token (sem verificar assinatura)
python -c "import jwt; print(jwt.decode('SEU_TOKEN', options={'verify_signature': False}))"
```

---

## 5. Métricas / Observabilidade

### Sintoma
`/metrics` retorna 404

### Solução
Verificar se `setup_observability_middleware(app)` é chamado em `app/main.py`.

### Sintoma
Métricas não aparecem no Prometheus

### Diagnóstico
```bash
# Verificar se o endpoint está vivo
curl http://localhost:8001/metrics | head -20
```

---

## 6. Docker

### Sintoma
Container auth-service não consegue conectar ao PostgreSQL

### Diagnóstico
```bash
docker compose -f docker/docker-compose.yml logs auth-service
docker compose -f docker/docker-compose.yml exec postgres pg_isready -U user
```

---

## 7. Stack de Observabilidade

### Troca de stack
```bash
# Dev (Floci)
OBSERVABILITY_STACK=floci uvicorn app.main:app

# VPS (Open Source)
OBSERVABILITY_STACK=vps uvicorn app.main:app

# AWS
OBSERVABILITY_STACK=aws uvicorn app.main:app
```
