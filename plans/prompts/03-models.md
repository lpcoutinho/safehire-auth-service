# Fase 3: Camada de Models Pydantic

Execute este prompt para implementar a **Fase 3** do Auth Service.

## Pré-condições (obrigatório)
Antes de executar qualquer ação, considere documentação e regras em:
- `docs/2-principios-norteadores.md`
- `docs/3-arquitetura.md`
- `plans/3-validacao.md`
- `plans/git-flow.md`

## Objetivo
Implementar schemas Pydantic de request/response para usuários e autenticação.

## Regras
- **TEST-FIRST**: teste antes do código
- **Sem `Any`**, sem `dict` genérico — tipos específicos
- **Nomes únicos**: sem sufixos `Handler`, `Manager`, `Data`
- **Mensagens de erro** com valor ofensivo + formato esperado

## Tarefas

### 1. [TEST] tests/unit/test_models.py (escrever PRIMEIRO)
Testes para:
- `UsuarioCreate`: valida email, senha >= 8 chars, tipo enum válido
- `UsuarioResponse`: serialização a partir de ORM (from_attributes)
- `UsuarioUpdate`: campos opcionais funcionam
- `LoginRequest`: valida email
- `LoginResponse`: campos obrigatórios
- `RefreshTokenRequest`: token não vazio
- `TokenPayload`: construção a partir de dict

### 2. app/models/usuario.py
```python
"""Schemas Pydantic para Usuario (request/response)."""
from datetime import datetime
from enum import Enum
from uuid import UUID
from pydantic import BaseModel, EmailStr, field_validator

class TipoUsuario(str, Enum):
    recrutador = "recrutador"
    candidato = "candidato"

class UsuarioCreate(BaseModel):
    nome: str
    email: EmailStr
    senha: str
    tipo: TipoUsuario

    @field_validator("senha")
    @classmethod
    def senha_deve_ter_no_minimo_8_caracteres(cls, v):
        if len(v) < 8:
            raise ValueError(f"senha deve ter no mínimo 8 caracteres, recebido: {len(v)}")
        return v

class UsuarioResponse(BaseModel):
    id: UUID
    nome: str
    email: EmailStr
    tipo: TipoUsuario
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime
    model_config = {"from_attributes": True}

class UsuarioUpdate(BaseModel):
    nome: str | None = None
    email: EmailStr | None = None
    senha: str | None = None
```

### 3. app/models/auth.py
```python
"""Schemas Pydantic para autenticação (login, tokens)."""
from uuid import UUID
from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str

class TokenPayload(BaseModel):
    sub: UUID
    exp: int
    tipo: str = "access"
```

### 4. Implementar
Depois dos testes passarem (RED), implementar os arquivos acima (GREEN).

## Critérios de Aceitação
- [ ] `pytest tests/unit/test_models.py -v` passa
- [ ] Validação de email rejeita strings inválidas
- [ ] Validação de senha rejeita < 8 caracteres com mensagem descritiva
- [ ] `mypy app/models/` passa sem erros
- [ ] Docstring no topo de cada arquivo
- [ ] Docstring em cada classe pública

## TodoList
- Revise as implementações e se tudo passou atualize:
    - `plans/2-todolist.md`
    - `plans/1-roadmap.md`
- Crie um PR da sua branch para `develop` e atualize os plans após o merge
