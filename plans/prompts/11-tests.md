# Fase 11: Testes e Validação

Execute este prompt para implementar a **Fase 11** do Auth Service.

## Pré-condições
- Fases 1-10 concluídas
- Consulte `docs/6-validacao.md` (critérios completos)

## Objetivo
Garantir cobertura de testes > 80% e validação completa do serviço.

## Regras
- **F.I.R.S.T**: Fast, Independent, Repeatable, Self-validating, Timely
- **Mocks**: usar fakes para I/O externo (nunca inline stubs)
- **Coverage**: mínimo 80%

## Tarefas

### 1. Revisar testes unitários existentes
Garantir que cada módulo tem seu arquivo de teste:
- [ ] `tests/unit/test_config.py`
- [ ] `tests/unit/test_database.py`
- [ ] `tests/unit/test_models.py`
- [ ] `tests/unit/test_usuario_repo.py`
- [ ] `tests/unit/test_jwt_service.py`
- [ ] `tests/unit/test_auth_service.py`
- [ ] `tests/unit/test_middleware_auth.py`
- [ ] `tests/unit/test_observability.py`

### 2. Revisar testes de integração
- [ ] `tests/integration/test_auth_flow.py` — fluxo completo registro → login → refresh
- [ ] `tests/integration/test_usuario_crud.py` — buscar me, buscar por id
- [ ] `tests/integration/test_health.py` — /health, /docs, /metrics

### 3. Testes de segurança
- [ ] SQL injection via SQLAlchemy (binding automático — validar que não usa f-strings)
- [ ] Token inválido retorna 401
- [ ] Token expirado retorna 401
- [ ] Senha nunca aparece em logs (verificar logger)

### 4. Verificações
```bash
pytest tests -v --cov=app --cov-report=term-missing
mypy app/ --strict
black app/ tests/ --check
isort app/ tests/ --check
```

### 5. Corrigir
Se coverage < 80% ou mypy/black/isort falharem, corrigir antes de prosseguir.

## Critérios de Aceitação
- [ ] `pytest -v --cov=app --cov-report=term-missing` → coverage ≥ 80%
- [ ] `mypy app/ --strict` → sem erros
- [ ] `black app/ tests/ --check` → OK
- [ ] `isort app/ tests/ --check` → OK
- [ ] Testes são F.I.R.S.T
- [ ] Nenhum teste depende de outro (independência)
- [ ] Fakes implementados para todo I/O externo
