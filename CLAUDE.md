# Auth Service - CLAUDE.md

## Stack Tecnológica
- **Framework:** FastAPI (Python 3.11+)
- **Banco de Dados:** PostgreSQL (esquema isolado `auth_schema`)
- **Autenticação:** JWT tokens (HttpOnly cookies via frontend)
- **ORM:** SQLAlchemy com Pydantic v2 para schemas
- **Formatação:** `black` e `isort`

## Responsabilidades
- Gerenciamento de usuários (recrutadores e candidatos)
- Emissão e validação de tokens JWT
- Autenticação e autorização

## Comandos de Desenvolvimento

### Instalar dependências
```bash
pip install -r requirements.txt
```

### Rodar em modo de desenvolvimento
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

### Rodar testes
```bash
pytest -v
```

### Formatar código
```bash
black app/ tests/
isort app/ tests/
```

## Regras de Code Style
- Funções entre 4 e 20 linhas
- Arquivos com menos de 500 linhas
- Nomes específicos (evite sufixos genéricos como `Handler`, `Manager`)
- Tipagem estrita (proibido `any`)
- Early returns, máximo 2 níveis de indentação
- Exceções semânticas com valor ofensivo e formato esperado
- Preservar comentários existentes
- Docstrings em funções públicas