---
type: doc
name: project-overview
description: High-level overview of the project, its purpose, and key components
category: overview
generated: 2026-01-22
status: filled
scaffoldVersion: "2.0.0"
---
## Project Overview

O **Sistema Aponta** é uma aplicação de apontamento de horas integrada ao Azure DevOps, desenvolvida para a **SEFAZ Ceará**. Permite que desenvolvedores registrem suas horas trabalhadas diretamente em Work Items do Azure DevOps através de uma extensão integrada.

## Codebase Reference

> **Detailed Analysis**: For complete symbol counts, architecture layers, and dependency graphs, see [`codebase-map.json`](./codebase-map.json).

## Quick Facts

- **Root**: `/home/pedroctdev/apps/api-aponta-vps`
- **Languages**: Python (100%), FastAPI backend
- **Entry**: `app/main.py`
- **Full analysis**: [`codebase-map.json`](./codebase-map.json)

## Entry Points

- [`app/main.py`](../../app/main.py) — FastAPI application entrypoint
- [`alembic/env.py`](../../alembic/env.py) — Database migrations runner
- [`scripts/start.sh`](../../scripts/start.sh) — Production startup script

## Key Exports

- **API Routers**: `apontamentos`, `atividades`, `projetos`, `timesheet`, `user`, `work_items`
- **Services**: `AzureService`, `TimesheetService`, `ApontamentoService`
- **Models**: `Apontamento`, `Atividade`, `Projeto`

## File Structure & Code Organization

- `app/` — FastAPI application source code
  - `models/` — SQLAlchemy ORM models
  - `schemas/` — Pydantic validation schemas
  - `routers/` — API endpoint definitions
  - `services/` — Business logic and Azure DevOps integration
  - `repositories/` — Data access layer
- `alembic/` — Database migration scripts
- `tests/` — Automated tests (pytest)
- `deploy/` — Deployment configurations and guides
- `scripts/` — Utility scripts (dev, deploy, metrics)
- `nginx/` — Nginx proxy configurations
- `extension/` — Azure DevOps extension manifest

## Technology Stack Summary

| Layer | Technology |
|-------|------------|
| **Runtime** | Python 3.12 |
| **Framework** | FastAPI |
| **ORM** | SQLAlchemy 2.0 |
| **Database** | PostgreSQL 15 |
| **Migrations** | Alembic |
| **Auth** | JWT (App Token) + PAT (Azure API) |
| **HTTP Client** | httpx (async) |
| **Containerization** | Docker + Docker Compose |
| **Proxy** | Nginx |

## Core Framework Stack

- **Backend**: FastAPI com SQLAlchemy para ORM
- **Validação**: Pydantic para schemas de request/response
- **Autenticação**: PyJWT para validação de App Tokens
- **Azure Integration**: httpx para chamadas assíncronas à API do Azure DevOps

## External Service Dependencies

- **Azure DevOps API** — Busca de Work Items, WIQL queries, perfil de usuário
- **PostgreSQL** — Armazenamento de apontamentos, atividades, projetos

## Getting Started Checklist

1. Clone o repositório e configure o `.env` (ver `.env.example`)
2. Instale dependências: `pip install -r requirements.txt`
3. Execute migrações: `alembic upgrade head`
4. Inicie o servidor: `uvicorn app.main:app --reload`
5. Acesse a documentação: `http://localhost:8000/docs`

## Environments

| Ambiente | URL | Schema DB |
|----------|-----|-----------|
| Staging | https://staging-aponta.treit.com.br | `aponta_sefaz_staging` |
| Produção | https://aponta.treit.com.br | `aponta_sefaz` |

## Related Resources

- [architecture.md](./architecture.md)
- [development-workflow.md](./development-workflow.md)
- [security.md](./security.md)
- [tooling.md](./tooling.md)
- [codebase-map.json](./codebase-map.json)
