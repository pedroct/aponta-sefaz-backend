# Documentation Index - Sistema Aponta

Bem-vindo à base de conhecimento do Sistema Aponta. Comece pelo overview do projeto e depois explore os guias específicos conforme necessário.

## Core Guides

| Guide | Description |
|-------|-------------|
| [Project Overview](./project-overview.md) | Visão geral, stack tecnológico, estrutura |
| [Architecture](./architecture.md) | Arquitetura do sistema, camadas, padrões |
| [Security](./security.md) | Autenticação JWT/PAT, secrets, troubleshooting |
| [Development Workflow](./development-workflow.md) | CI/CD, branching, comandos úteis |
| [Testing Strategy](./testing-strategy.md) | Estratégia de testes, pytest |
| [Data Flow](./data-flow.md) | Fluxo de dados, integrações |
| [Tooling](./tooling.md) | Ferramentas de desenvolvimento |
| [Glossary](./glossary.md) | Termos e conceitos do domínio |
| [Changelog](./changelog.md) | 📝 Histórico de mudanças e features |

## Features Documentation

| Feature | Description | Status |
|---------|-------------|--------|
| [Blue Cells](./features/blue-cells.md) | Destaque visual de células baseado em histórico de Work Items | ✅ Deployed Staging |
| [Locked Items](./features/locked-items.md) | Bloqueio de lançamento de horas em Work Items fechados | 🔄 Backend Complete |
| [Toolbar Button](./features/toolbar-button-spec.md) | Botão "Aponta Tempo" na toolbar do Work Item | ✅ Deployed Staging |

## Quick Reference

### Environments

| Ambiente | URL | Container | Schema |
|----------|-----|-----------|--------|
| Staging | https://staging-aponta.treit.com.br | `api-aponta-staging` | `aponta_sefaz_staging` |
| Produção | https://aponta.treit.com.br | `api-aponta-prod` | `aponta_sefaz` |

### VPS Access

```bash
ssh root@92.112.178.252
```

### Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI entrypoint |
| `app/auth.py` | JWT + PAT authentication |
| `app/services/azure.py` | Azure DevOps API integration |
| `app/services/timesheet_service.py` | Timesheet business logic |
| `alembic/versions/` | Database migrations |

## Repository Structure

```
api-aponta-vps/
├── app/                    # FastAPI application
│   ├── models/            # SQLAlchemy ORM models
│   ├── schemas/           # Pydantic schemas
│   ├── routers/           # API endpoints
│   ├── services/          # Business logic
│   └── repositories/      # Data access
├── alembic/               # Database migrations
├── tests/                 # Pytest tests
├── deploy/                # Deployment configs
├── scripts/               # Utility scripts
├── nginx/                 # Nginx configurations
├── extension/             # Azure DevOps extension
├── .github/workflows/     # CI/CD pipelines
└── .context/              # AI context documentation
```

## Authentication Quick Reference

⚠️ **Regra de Ouro**:
- **App Token JWT** → Apenas para identificar o usuário
- **PAT do backend** → Para TODAS as chamadas à API do Azure DevOps

## Document Map

| Guide | File | Primary Inputs |
|-------|------|----------------|
| Project Overview | `project-overview.md` | README, stack, estrutura |
| Architecture | `architecture.md` | Diagrams, patterns, decisions |
| Security | `security.md` | Auth flow, secrets, troubleshooting |
| Development Workflow | `development-workflow.md` | CI/CD, branching, deploy |
| Testing Strategy | `testing-strategy.md` | pytest, fixtures, coverage |
| Data Flow | `data-flow.md` | Azure DevOps integration |
| Tooling | `tooling.md` | Docker, scripts, IDE |
| Glossary | `glossary.md` | Domain terms, Work Items |
