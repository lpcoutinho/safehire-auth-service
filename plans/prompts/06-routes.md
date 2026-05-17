# Fase 6: Camada de Routes

Execute este prompt para implementar a **Fase 6** do Auth Service.

## Pré-condições (obrigatório)
Antes de executar qualquer ação, considere documentação e regras em:
- `docs/2-principios-norteadores.md`
- `docs/3-arquitetura.md`
- `plans/3-validacao.md`
- `plans/git-flow.md`

## Objetivo
Implementar endpoints HTTP de autenticação e CRUD de usuários.

## Regras
- **TEST-FIRST**: teste de integração antes dos endpoints
- **Injeção**: `Depends(get_session)` para DB, `Depends(_auth_service)` para lógica
- **Idempotência**: POST /auth/register com email duplicado → 409
- **Erros descritivos**: incluir valor ofensivo na resposta

## Tarefas

### 1. [TEST] tests/integration/test_auth_flow.py (escrever PRIMEIRO)
Testes com AsyncClient:
- `POST /auth/register`: 201 + usuário no response
- `POST /auth/register` (email duplicado): 409
- `POST /auth/register` (senha curta): 422
- `POST /auth/login`: 200 + access_token + refresh_token
- `POST /auth/login` (senha errada): 401
- `POST /auth/refresh`: 200 + novo par de tokens
- `POST /auth/refresh` (token inválido): 401

### 2. [TEST] tests/integration/test_usuario_crud.py (escrever PRIMEIRO)
- `GET /usuarios/me` sem token: 401
- `GET /usuarios/{id}` inexistente: 404

### 3. app/routes/auth.py
```python
"""Endpoints de autenticação (/auth/register, /login, /refresh, /logout)."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_session
from app.models.auth import LoginRequest, RefreshRequest, TokenResponse
from app.models.usuario import UsuarioCreate, UsuarioResponse
from app.repositories.usuario_repo import UsuarioRepository
from app.services.auth_service import AuthService
from app.services.jwt_service import JWTService

router = APIRouter()

def _auth_service(session: AsyncSession = Depends(get_session)) -> AuthService:
    return AuthService(UsuarioRepository(session), JWTService())

@router.post("/register", response_model=UsuarioResponse, status_code=201)
async def register(data: UsuarioCreate, auth: AuthService = Depends(_auth_service)):
    try:
        usuario, _, _ = await auth.registrar(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    return usuario

@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest, auth: AuthService = Depends(_auth_service)):
    try:
        _, access, refresh = await auth.autenticar(data)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return TokenResponse(access_token=access, refresh_token=refresh)

@router.post("/refresh", response_model=TokenResponse)
async def refresh(data: RefreshRequest, auth: AuthService = Depends(_auth_service)):
    try:
        access, refresh = await auth.refresh(data.refresh_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    return TokenResponse(access_token=access, refresh_token=refresh)
```

### 4. app/routes/usuarios.py
```python
"""Endpoints de CRUD de usuários (/usuarios/me, /{id})."""
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from app.middleware.auth import get_usuario_atual
from app.models.usuario import UsuarioResponse
from app.schemas.usuario import Usuario
from app.database import get_session
from app.repositories.usuario_repo import UsuarioRepository
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()

@router.get("/me", response_model=UsuarioResponse)
async def me(usuario: Usuario = Depends(get_usuario_atual)):
    return usuario

@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def buscar(usuario_id: UUID, session: AsyncSession = Depends(get_session)):
    repo = UsuarioRepository(session)
    usuario = await repo.buscar_por_id(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail=f"Usuário não encontrado: {usuario_id}")
    return usuario
```

### 5. Implementar
Depois dos testes passarem (RED), implementar os arquivos acima (GREEN).

## Critérios de Aceitação
- [ ] `pytest tests/integration/test_auth_flow.py -v` passa
- [ ] `pytest tests/integration/test_usuario_crud.py -v` passa
- [ ] Endpoints retornam status codes corretos (201, 200, 401, 404, 409, 422)
- [ ] `mypy app/routes/` passa sem erros
- [ ] Docstring em cada arquivo e endpoint

## TodoList
- Revise as implementações e se tudo passou atualize:
    - `plans/2-todolist.md`
    - `plans/1-roadmap.md`
- Crie um PR da sua branch para `develop` e atualize os plans após o merge
