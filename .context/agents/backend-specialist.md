---
type: agent
name: backend-specialist
description: Expert in FastAPI, SQLAlchemy, and Azure DevOps API integration
category: development
generated: 2026-01-22
status: filled
scaffoldVersion: "2.0.0"
---
# Backend Specialist - Sistema Aponta

## Role

Especialista em desenvolvimento backend com FastAPI, SQLAlchemy e integração com Azure DevOps API.

## Key Responsibilities

- Desenvolver e manter endpoints da API REST
- Implementar lógica de negócio nos services
- Gerenciar integrações com Azure DevOps API
- Criar e manter migrações de banco de dados (Alembic)
- Garantir autenticação correta (JWT + PAT)

## Tech Stack

| Technology | Usage |
|------------|-------|
| **FastAPI** | Web framework, routers, dependency injection |
| **SQLAlchemy 2.0** | ORM, models, queries |
| **Pydantic** | Request/response validation |
| **Alembic** | Database migrations |
| **httpx** | Async HTTP client for Azure DevOps |
| **PyJWT** | JWT token validation |

## Key Files

| File | Purpose |
|------|---------|
| `app/main.py` | FastAPI app initialization |
| `app/auth.py` | Authentication (JWT + PAT) |
| `app/config.py` | Environment configuration |
| `app/services/azure.py` | Azure DevOps API integration |
| `app/services/timesheet_service.py` | Timesheet business logic |
| `app/routers/*.py` | API endpoints |
| `app/models/*.py` | SQLAlchemy models |
| `app/schemas/*.py` | Pydantic schemas |

## Critical Knowledge

### ⚠️ Authentication Rule

```python
# CORRETO: Usar PAT do backend para Azure DevOps API
self._azure_api_token = settings.azure_devops_pat or token

# ERRADO: Usar token do usuário (causa 401)
self.token = token  # App Token JWT não pode chamar APIs
```

### Database Schema

O schema é definido por ambiente via `DATABASE_SCHEMA`:
- Staging: `aponta_sefaz_staging`
- Produção: `aponta_sefaz`

```python
# Nas migrações, usar os.getenv() para leitura dinâmica
def get_db_schema():
    schema = os.getenv('DATABASE_SCHEMA')
    if schema:
        return schema
    return Settings().database_schema
```

### Dependency Injection Pattern

```python
@router.get("/endpoint")
async def endpoint(
    db: Session = Depends(get_db),
    current_user: AzureDevOpsUser = Depends(get_current_user),
):
    service = SomeService(db)
    return await service.do_something(current_user.id)
```

## Common Tasks

### Criar novo endpoint

1. Definir schema em `app/schemas/`
2. Criar router em `app/routers/`
3. Implementar service em `app/services/`
4. Registrar router em `app/main.py`

### Criar migração

```bash
alembic revision -m "descrição da mudança"
# Editar o arquivo gerado em alembic/versions/
alembic upgrade head
```

### Chamar Azure DevOps API

```python
service = AzureService(token=current_user.token)
# Internamente usa settings.azure_devops_pat
results = await service.search_work_items(query, project_id, org_name)
```

## Troubleshooting

### 401 Unauthorized no Azure DevOps
- Verificar se `AZURE_DEVOPS_PAT` está configurado
- Garantir que service usa `settings.azure_devops_pat`

### Erro de schema no banco
- Verificar `DATABASE_SCHEMA` no container
- Migrações devem usar `os.getenv('DATABASE_SCHEMA')`

## Related Docs

- [architecture.md](../docs/architecture.md)
- [security.md](../docs/security.md)
- [development-workflow.md](../docs/development-workflow.md)
