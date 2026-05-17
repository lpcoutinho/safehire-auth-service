# SafeHire Auth Service

Serviço central de autenticação e autorização da plataforma SafeHire AI.

## Stack

- **Framework:** FastAPI (async)
- **Banco de Dados:** PostgreSQL (schema `auth_schema`)
- **ORM:** SQLAlchemy 2.0
- **Validação:** Pydantic v2
- **Auth:** JWT (python-jose) + bcrypt

## Endpoints

### Auth
- `POST /auth/register` — Registro de usuário
- `POST /auth/login` — Login
- `POST /auth/logout` — Logout
- `POST /auth/refresh` — Refresh token

### Usuários
- `GET /usuarios/me` — Perfil do usuário logado
- `PUT /usuarios/me` — Atualizar perfil
- `GET /usuarios/{id}` — Buscar usuário por ID

## Desenvolvimento

```bash
# Instalar dependências
pip install -r requirements.txt

# Rodar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001

# Testes
pytest -v

# Formatação
black app/ tests/
isort app/ tests/
```
