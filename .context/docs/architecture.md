---
type: doc
name: architecture
description: System architecture, layers, patterns, and design decisions
category: architecture
generated: 2026-01-26
status: filled
scaffoldVersion: "2.0.0"
---
## Architecture Notes

O Sistema Aponta segue uma arquitetura de API REST com separação clara de responsabilidades, integrado ao ecossistema Azure DevOps.

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        Azure DevOps                              │
│  ┌─────────────────┐                                            │
│  │  Extensão Aponta │◄──── vss-extension.json                   │
│  │  (timesheet.html)│                                            │
│  └────────┬────────┘                                            │
│           │ iframe                                               │
│           ▼                                                      │
│  ┌─────────────────┐                                            │
│  │ Frontend React  │◄──── https://staging-aponta.treit.com.br   │
│  │ (Vite + TS)     │                                            │
│  └────────┬────────┘                                            │
└───────────┼─────────────────────────────────────────────────────┘
            │ HTTPS (App Token JWT)
            ▼
┌─────────────────────────────────────────────────────────────────┐
│                        VPS (92.112.178.252)                      │
│                                                                  │
│  ┌─────────────────┐     ┌─────────────────┐                    │
│  │     Nginx       │────▶│  API FastAPI    │                    │
│  │  (Proxy Reverso)│     │  (Python 3.12)  │                    │
│  └─────────────────┘     └────────┬────────┘                    │
│                                   │                              │
│                          ┌────────┴────────┐                    │
│                          ▼                 ▼                    │
│                   ┌──────────┐      ┌──────────────┐            │
│                   │PostgreSQL│      │ Azure DevOps │            │
│                   │   (DB)   │      │     API      │            │
│                   └──────────┘      └──────────────┘            │
│                                     (via PAT)                    │
└─────────────────────────────────────────────────────────────────┘
```

## Architectural Layers

| Layer | Purpose | Directory |
|-------|---------|-----------|
| **Routers** | HTTP endpoints, request/response handling | `app/routers/` |
| **Services** | Business logic, Azure DevOps integration | `app/services/` |
| **Repositories** | Data access abstraction | `app/repositories/` |
| **Models** | SQLAlchemy ORM definitions | `app/models/` |
| **Schemas** | Pydantic validation | `app/schemas/` |

> See [`codebase-map.json`](./codebase-map.json) for complete symbol counts and dependency graphs.

## Detected Design Patterns

| Pattern | Confidence | Locations | Description |
|---------|------------|-----------|-------------|
| Repository | 95% | `app/repositories/` | Abstração de acesso a dados |
| Service Layer | 95% | `app/services/` | Lógica de negócio isolada |
| Dependency Injection | 90% | `Depends()` FastAPI | Injeção de dependências |
| DTO/Schema | 90% | `app/schemas/` | Validação e serialização |

## Entry Points

- [`app/main.py`](../../app/main.py#L1) — FastAPI app initialization, CORS, routers
- [`app/auth.py`](../../app/auth.py#L1) — Authentication middleware (JWT + PAT)
- [`alembic/env.py`](../../alembic/env.py#L1) — Migration environment

## Public API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/timesheet` | GET | Grade semanal de apontamentos |
| `/api/v1/apontamentos` | CRUD | Gerenciamento de apontamentos |
| `/api/v1/atividades` | CRUD | Tipos de atividades |
| `/api/v1/projetos` | CRUD | Projetos cadastrados |
| `/api/v1/work-items/search` | GET | Busca Work Items no Azure |
| `/api/v1/user` | GET | Perfil do usuário autenticado |

## External Service Dependencies

| Service | Purpose | Auth Method |
|---------|---------|-------------|
| **Azure DevOps API** | Work Items, WIQL, User Profile | PAT (Basic Auth) |
| **PostgreSQL** | Data persistence | Connection string |

## Key Decisions & Trade-offs

### App Token JWT vs PAT
- **App Token JWT**: Usado apenas para identificar o usuário (não pode chamar APIs do Azure)
- **PAT do Backend**: Usado para todas as chamadas à API do Azure DevOps

### Schema por Ambiente
- Staging usa `aponta_sefaz_staging`
- Produção usa `aponta_sefaz`
- Configurado via `DATABASE_SCHEMA` environment variable

## Docker Containers

| Container | Image | Port | Purpose |
|-----------|-------|------|---------|
| `api-aponta-staging` | `staging-api:latest` | 8001 | Backend Staging |
| `api-aponta-prod` | `production-api:latest` | 8000 | Backend Produção |
| `postgres-aponta` | `postgres:15-alpine` | 5432 | Database |
| `nginx-aponta` | `nginx:alpine` | 80/443 | Proxy Reverso |

## Database Schema

### Tabelas Principais

| Tabela | Descrição |
|--------|-----------|
| `apontamentos` | Registros de horas apontadas |
| `atividades` | Tipos de atividades (Planning, Development, etc.) |
| `projetos` | Projetos cadastrados |
| `atividade_projeto` | Relação N:N entre atividades e projetos |
| `alembic_version` | Controle de migrações |

## CI/CD Pipeline

O deploy e 100% automatizado via **GitHub Actions**. NAO faca deploy manual.

```
GitHub Repository
    │
    ├─── develop branch ──> Deploy Staging (automatico)
    │
    └─── main branch ──> Deploy Production (automatico)
```

### Workflows

| Workflow | Trigger | Ambiente |
|----------|---------|----------|
| `deploy-staging.yml` | Push em `develop` | Staging |
| `deploy-production.yml` | Push em `main` | Producao |
| `rollback.yml` | Manual | Ambos |

### Secrets Management

Secrets sao gerenciados em **GitHub > Settings > Secrets and variables > Actions**.

| Secret | Scope | Descricao |
|--------|-------|-----------|
| `VPS_HOST` | Repository | IP do servidor |
| `VPS_USER` | Repository | Usuario SSH |
| `VPS_SSH_PRIVATE_KEY` | Repository | Chave SSH privada |
| `DATABASE_PASSWORD` | Environment | Senha PostgreSQL |
| `AZURE_DEVOPS_PAT` | Environment | PAT Azure DevOps |
| `AZURE_EXTENSION_SECRET` | Environment | Secret da extensao |

Os arquivos `.env` sao gerados automaticamente durante o deploy a partir dos GitHub Secrets.

> **Documentacao completa de deploy:** [docs/DEPLOY.md](../../docs/DEPLOY.md)

## Related Resources

- [project-overview.md](./project-overview.md)
- [security.md](./security.md)
- [data-flow.md](./data-flow.md)
- [docs/DEPLOY.md](../../docs/DEPLOY.md)
