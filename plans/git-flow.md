# Git Flow — Estratégia de Branches

## Estrutura de Branches

```
main       ──●──────────────────●──  (produção, protegida)
              \                /
staging        ●──────────────●──    (pré-produção, protegida)
                \            /
develop          ●──────────●──      (integração, branch base para features)
                 |    |     |
feature/*  ──●──┘     |     └──●──  (features: feature/02-config-database)
fix/*       ──────●───┘            (hotfixes/correções)
```

## Nomenclatura

| Prefixo | Uso | Base | Merge para |
|---------|-----|------|------------|
| `feature/` | Novas funcionalidades | `develop` | `develop` |
| `fix/` | Correções de bugs | `develop` | `develop` |
| `hotfix/` | Correções urgentes em produção | `main` | `main` + `develop` |
| `main` | Produção (protegida) | — | — |
| `staging` | Pré-produção (protegida) | `develop` | `main` |
| `develop` | Integração contínua | `main` | `staging` |

## Regras de Merge

### feature/* → develop
1. Crie a branch a partir de `develop`: `git checkout -b feature/meu-feature develop`
2. Implemente seguindo as fases do roadmap
3. Para cada fase nova (config, models, services, etc.), faça commit atômico
4. Abra um Pull Request para `develop`
5. CI deve passar (lint + types + test + build)
6. PR deve ser aprovado por 1 reviewer
7. Faça merge (preferência: squash merge para manter histórico limpo)

### develop → staging
1. Quando um conjunto de features estiver completo, abra PR de `develop` para `staging`
2. CI deve passar
3. PR deve ser aprovado por 1 reviewer
4. Faça merge (merge commit)

### staging → main
1. Quando a versão estiver pronta para produção, abra PR de `staging` para `main`
2. CI deve passar
3. PR deve ser aprovado por 1 reviewer
4. CD manual via `workflow_dispatch`
5. Faça merge (merge commit)

### hotfix/* → main
1. Crie a branch a partir de `main`
2. Corrija o bug
3. Abra PR para `main`
4. Após merge em `main`, faça cherry-pick para `develop` e `staging`

## Proteção de Branches (GitHub Settings)

### main
- [ ] Requerer Pull Request antes de merge
- [ ] Requerer 1 aprovação
- [ ] Requerer status checks passarem (CI)
- [ ] Não permitir push direto

### staging
- [ ] Requerer Pull Request antes de merge
- [ ] Requerer 1 aprovação
- [ ] Requerer status checks passarem (CI)
- [ ] Não permitir push direto

### develop
- [ ] Requerer Pull Request antes de merge (opcional — recomendado para equipes)
- [ ] Não permitir push direto (opcional)

## Fluxo de Trabalho Diário

```bash
# 1. Sincronizar develop
git checkout develop
git pull origin develop

# 2. Criar feature branch
git checkout -b feature/02-config-database develop

# 3. Implementar (RED → GREEN → REFACTOR)
# ... código ...

# 4. Commits atômicos
git add -A && git commit -m "fase 2: implementa config.py"

# 5. Publicar branch
git push origin feature/02-config-database

# 6. Abrir PR no GitHub via CLI
gh pr create --base develop --title "Fase 2: Config + Database" --body "## Descrição\n\nImplementa camada de configuração e database.\n\n## Validação\n\n- [ ] CI passou\n- [ ] Testes unitários escritos antes do código\n- [ ] Docstrings em todo método público\n\nCloses #2"

# 7. Após aprovação e merge, atualizar docs
git checkout develop
git pull origin develop
git branch -d feature/02-config-database

# 8. Atualizar plans
#   - plans/1-roadmap.md: marcar fase como concluída
#   - plans/2-todolist.md: marcar itens como concluídos
```

## Integração com CI/CD

### CI (GitHub Actions)
- Dispara em: `push` para `develop`, `staging`, `main` + `pull_request` para todas
- Jobs: lint → types → test (com PostgreSQL service) → build (push GHCR)
- Cobertura mínima: 80%

### CD (GitHub Actions)
- Dispara em: `workflow_dispatch` manual apenas
- Preparado para: VPS (SSH + Docker Compose) e AWS (ECS Fargate)

## Checklist PR

Antes de abrir um Pull Request, verifique:

- [ ] Branch está atualizada com `develop` (`git merge develop`)
- [ ] CI passa localmente (`pytest -v`, `mypy app/`, `black --check`, `isort --check`)
- [ ] Testes escritos antes da implementação (RED → GREEN)
- [ ] Docstrings em todo método público
- [ ] Observabilidade adicionada em operações de I/O
- [ ] plans/1-roadmap.md e plans/2-todolist.md atualizados
