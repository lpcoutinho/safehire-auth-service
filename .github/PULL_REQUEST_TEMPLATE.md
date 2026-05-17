# Pull Request

## Descrição
<!-- Descreva o que este PR implementa ou corrige. -->

## Tipo de Mudança

- [ ] Nova funcionalidade (`feature/`)
- [ ] Correção de bug (`fix/`)
- [ ] Hotfix (`hotfix/`)
- [ ] Documentação
- [ ] Refatoração
- [ ] CI/CD

## Fase do Roadmap
<!-- Ex: Fase 2: Config + Database -->

## Checklist de Validação

### Código
- [ ] Testes escritos **antes** da implementação (RED → GREEN)
- [ ] `pytest -v` passa sem erros
- [ ] `mypy app/` passa sem erros
- [ ] `black --check app/ tests/` passa
- [ ] `isort --check app/ tests/` passa
- [ ] Cobertura de testes ≥ 80%

### Documentação
- [ ] Docstring no topo de cada arquivo novo
- [ ] Docstring em todo método público (WHY, não WHAT)
- [ ] `plans/1-roadmap.md` atualizado
- [ ] `plans/2-todolist.md` atualizado

### Git Flow
- [ ] Branch nomeada corretamente (`feature/*`, `fix/*`, `hotfix/*`)
- [ ] Branch criada a partir da branch correta
- [ ] PR destinado à branch correta
- [ ] Commits são atômicos e mensagens claras

## Referências
<!-- Issues relacionadas: Closes #N -->

---

_Após aprovação, faça squash merge para manter histórico limpo._
