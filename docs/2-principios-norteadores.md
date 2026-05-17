# Plano de Execução — Princípios Norteadores

## Princípios Norteadores

### 1. Test-First (TDD)
Antes de implementar qualquer método novo, **deve existir um teste que falhe** e que:
- Defina o comportamento esperado do método
- Cubra o caso feliz (happy path)
- Cubra pelo menos um caso de erro (edge case)
- Use `pytest` com fixtures apropriadas

> `RED → GREEN → REFACTOR`: escreva o teste (RED), implemente o mínimo para passar (GREEN), refine (REFACTOR).

### 2. Documentação em Todo Arquivo e Método
- **Todo arquivo** deve ter docstring no topo explicando sua responsabilidade.
- **Todo método público** deve ter docstring com:
  - Descrição da intenção (WHY, não WHAT)
  - Exemplo de uso (uma linha)
  - Tipos documentados (já garantidos por type hints + mypy strict)
- **Todo método privado** deve ter docstring se sua lógica não for óbvia.

### 3. Observabilidade First
Todo método que envolva I/O (DB, cache, rede, filesystem) **deve**:
- Emitir métrica de duração
- Logar entrada/saída em structured JSON
- Propagar trace_id/span_id via OpenTelemetry

### 4. Dual-Stack Deploy (AWS + VPS)
O serviço deve ser deployável em ambos os cenários sem mudança de código:
- **VPS** (ex: Hostinger): Docker Compose com PostgreSQL, OpenTelemetry → Prometheus/Loki/Tempo
- **AWS**: ECS Fargate com CloudWatch Logs, X-Ray sidecar, Secrets Manager

### 5. Clean Code & Design

#### 5.1 Injeção de Dependências
- Toda dependência externa (DB, cache, serviços) deve ser injetada via parâmetros do construtor ou FastAPI `Depends`
- Nada de imports diretos em lógica profunda ou globais `from x import y` no meio de funções de negócio
- Bibliotecas terceiras (ex: `python-jose`, `passlib`, `boto3`) devem ser envolvidas em uma interface fina própria do projeto
  - `JWTService` encapsula `jose.jwt`
  - `AuthService` encapsula `passlib`
  - `CloudWatchMetrics` encapsula `boto3.client('cloudwatch')`

#### 5.2 Princípio da Responsabilidade Única (SRP)
- **Um módulo, uma responsabilidade**: `repositories/` só acessa dados, `services/` só tem lógica de negócio, `routes/` só orquestra HTTP
- **Uma função, uma coisa**: se a função faz validação + cálculo + persistência, divida
- **Arquivos < 500 linhas**, **funções 4-20 linhas**

#### 5.3 Nomes Específicos e Únicos
- Evite sufixos genéricos como `Handler`, `Manager`, `Data`, `Utils`, `Helper`
- Prefira nomes que retornem < 5 resultados no grep no código todo
- Exemplo: em vez de `UserManager`, use `UsuarioRepository`; em vez de `AuthHandler`, use `AuthService`

#### 5.4 Tipos Explícitos e Estritos
- Sem `Any` — use tipos específicos: `UUID`, `str`, `Usuario`, `list[Usuario]`
- Sem `dict` genérico — prefira schemas Pydantic tipados
- `mypy strict` deve passar sem erros
- Union types explícitos: `Usuario | None`, não `Optional[Usuario]`

#### 5.5 Idempotência
- **`POST /auth/register`**: idempotente — se o email já existe, retorna erro 409 consistente, nunca cria duplicata
- **`POST /auth/refresh`**: com o mesmo refresh token, produz o mesmo efeito (novo par de tokens)
- **`POST /auth/logout`**: revogar refresh token é idempotente — chamadas repetidas têm o mesmo efeito
- Evite mutação de parâmetros recebidos; prefira `frozenset` a `set` em APIs públicas

#### 5.6 Early Returns e Imports no Topo
- Máximo 2 níveis de indentação aninhada
- Early returns em vez de `if/else` aninhados
- Todos os `import` no topo do arquivo, nunca dentro de funções

#### 5.7 Zero Duplicidade (DRY)
- Toda lógica repetida em 2+ lugares deve ser extraída para função/módulo compartilhado
- Constantes mágicas (timeouts, limites) devem ser configuráveis via `Settings`, nunca literais espalhados

#### 5.8 Mensagens de Erro Descritivas
- Exceções devem incluir o **valor ofensivo** e o **formato esperado**
  - ✅ `raise ValueError(f"Email já cadastrado: {email}")`
  - ❌ `raise ValueError("Email já existe")`

#### 5.9 Anti-Corruption Layer (Bibliotecas Terceiras)
- Toda biblioteca externa encapsulada atrás de interface própria do projeto:
  - `JWTService` → `python-jose`
  - `AuthService` → `passlib` / `bcrypt`
  - `CloudWatchMetrics` → `boto3`
  - `XRayTracer` → `aws_xray_sdk`
- Se a biblioteca mudar, só a interface fina muda
- Nenhum import direto de terceiros fora dos módulos de serviço/infra



### 6. Git Flow

Toda implementação segue a estratégia de branches definida em `plans/git-flow.md`:

- **Branches permanentes**: `main` (produção), `staging` (pré-produção), `develop` (integração)
- **Branches temporárias**: `feature/*` (novas funcionalidades), `fix/*` (correções), `hotfix/*` (urgentes)
- **Fluxo de merge**: `feature/*` → `develop` → `staging` → `main`
- **Proteção**: `main` e `staging` são protegidas (PR + CI + approval)
- **Cada fase do roadmap** vira uma `feature/*` branch
- **PR template** em `.github/PULL_REQUEST_TEMPLATE.md` obrigatório

Este fluxo garante que:
- `main` nunca recebe código não testado
- `staging` serve como ambiente de QA antes de produção
- `develop` é a branch de integração contínua
- Features são isoladas até completas e validadas

---
