---
type: doc
name: data-flow
description: How data moves through the system and external integrations
category: data-flow
generated: 2026-01-22
updated: 2026-01-22
status: filled
scaffoldVersion: "2.0.0"
---
## Data Flow & Integrations

O Sistema Aponta integra-se com Azure DevOps para buscar Work Items e registrar apontamentos de horas. O fluxo de dados envolve autenticação JWT, chamadas à API do Azure DevOps usando PAT, e persistência em PostgreSQL.

## High-level Flow

```
┌──────────────┐
│   Frontend   │ (React + Vite + TypeScript)
│  (Extensão)  │
└──────┬───────┘
       │ 1. App Token JWT
       │    (identifica usuário)
       ▼
┌──────────────────────────────────────────────────────────┐
│                    Backend FastAPI                        │
│                                                           │
│  ┌─────────────────────────────────────────────────┐    │
│  │              Camada de Routers                   │    │
│  │  /timesheet, /apontamentos, /work-items, etc.   │    │
│  └─────────────────┬───────────────────────────────┘    │
│                    │                                      │
│  ┌─────────────────▼───────────────────────────────┐    │
│  │           Camada de Services                     │    │
│  │  TimesheetService, AzureService, etc.           │    │
│  └─────────────────┬───────────────────────────────┘    │
│                    │                                      │
│         ┌──────────┴──────────┐                          │
│         ▼                     ▼                          │
│  ┌─────────────┐      ┌──────────────┐                  │
│  │ Repository  │      │ Azure DevOps │                  │
│  │   (ORM)     │      │     API      │                  │
│  └──────┬──────┘      └──────┬───────┘                  │
│         │                    │ 2. PAT do Backend         │
│         │                    │    (todas as chamadas)    │
└─────────┼────────────────────┼───────────────────────────┘
          ▼                    ▼
   ┌─────────────┐      ┌──────────────┐
   │ PostgreSQL  │      │ Azure DevOps │
   │   Database  │      │   REST API   │
   └─────────────┘      └──────────────┘
```

## Module Dependencies

<!-- List cross-module dependencies showing which modules depend on which. -->

- **src/** → `utils`, `config`
- **services/** → `utils`

## Service Layer

O backend utiliza uma arquitetura em camadas com serviços especializados:

### AzureService (`app/services/azure.py`)
- **Responsabilidade**: Integração com Azure DevOps REST API
- **Métodos Principais**:
  - `get_user_info()` - Perfil do usuário
  - `get_user_projects()` - Lista de projetos
  - `get_work_items_by_wiql()` - Query WIQL para Work Items
  - `get_work_item_details()` - Detalhes de um Work Item específico
  - `get_work_item_revisions()` - Histórico de revisões (Blue Cells)
  - `get_process_work_item_states()` - Mapeamento de estados (Blue Cells)
- **Autenticação**: PAT (Personal Access Token) do backend

### TimesheetService (`app/services/timesheet_service.py`)
- **Responsabilidade**: Lógica de negócio para timesheet
- **Métodos Principais**:
  - `get_timesheet_week()` - Dados da semana de timesheet
  - `get_work_item_revisions()` - Wrapper para AzureService (Blue Cells)
  - `get_process_states()` - Wrapper para AzureService (Blue Cells)
- **Integrações**: AzureService, Repositories

### ApontamentoService (`app/services/apontamento_service.py`)
- **Responsabilidade**: Gerenciamento de apontamentos de horas
- **Métodos Principais**:
  - `create_apontamento()` - Criar apontamento
  - `update_apontamento()` - Atualizar apontamento
  - `delete_apontamento()` - Excluir apontamento
- **Integrações**: ApontamentoRepository, PostgreSQL

## Data Flow Examples

### Example 1: Blue Cells Feature (Work Item State History)

**User Action**: Frontend carrega timesheet da semana

**Flow**:
1. Frontend faz request para cada Work Item visível
   ```
   GET /api/v1/timesheet/work-item/123/revisions?organization_name=sefaz&project_id=MyProject
   ```

2. Backend (TimesheetService) chama AzureService
   ```python
   revisions = await azure_service.get_work_item_revisions(
       work_item_id=123,
       organization_name="sefaz", 
       project="MyProject"
   )
   ```

3. AzureService faz request ao Azure DevOps
   ```
   GET https://dev.azure.com/sefaz/MyProject/_apis/wit/workitems/123/revisions?api-version=7.2-preview.3
   Authorization: Basic {base64(PAT)}
   ```

4. Azure DevOps retorna array de revisões com histórico completo

5. Backend serializa para Pydantic schema e retorna JSON

6. Frontend usa algoritmo em `blue-cells-logic.ts` para determinar células azuis:
   - Filtra revisões até data da célula
   - Verifica se estado era "InProgress" 
   - Verifica se estava atribuído ao usuário
   - Aplica CSS class `.blue-cell` se true

**Caching**:
- Frontend: React Query cache (5 min para revisions, 1h para process states)
- Backend: Sem cache (stateless, delega ao frontend)

### Example 2: Creating Apontamento (Time Entry)

**User Action**: Usuário registra 4 horas em um Work Item

**Flow**:
1. Frontend envia POST com App Token JWT
   ```
   POST /api/v1/apontamentos
   Authorization: Bearer {jwt_token}
   Body: {
     "work_item_id": 123,
     "data": "2026-01-22",
     "duracao": 4.0,
     "descricao": "Desenvolvimento feature X"
   }
   ```

2. Backend valida JWT e extrai user_id

3. ApontamentoService cria registro
   ```python
   apontamento = await apontamento_service.create_apontamento(
       user_id=user_id,
       work_item_id=123,
       data=date(2026, 1, 22),
       duracao=4.0,
       descricao="Desenvolvimento feature X"
   )
   ```

4. Repository persiste em PostgreSQL via SQLAlchemy
   ```sql
   INSERT INTO apontamentos (user_id, work_item_id, data, duracao, descricao, criado_em)
   VALUES (?, ?, ?, ?, ?, NOW())
   ```

5. Backend retorna 201 Created com objeto criado

6. Frontend atualiza UI e invalida cache do React Query

## Observability & Failure Modes

### Logging

- **FastAPI Middleware**: Logs automáticos de requests/responses
- **Exception Handlers**: Stack traces para erros 500
- **Azure API Calls**: Logs de requests feitos ao Azure DevOps

### Health Checks

- **Endpoint**: `GET /api/v1/health`
- **Checks**: Database connectivity, Azure DevOps API availability
- **Response**: JSON com status de cada dependency

### Common Failure Modes

| Failure | Symptom | Recovery |
|---------|---------|----------|
| PAT expirado | 401 em chamadas Azure | Atualizar PAT no backend .env |
| Database down | 500 em endpoints que usam DB | Restart PostgreSQL container |
| Azure API down | Timeout em requests | Retry automático via httpx |
| Rate limit Azure | 429 Too Many Requests | Exponential backoff |
| JWT inválido | 401 Unauthorized | Frontend reautentica usuário |

### Monitoring

- **Docker**: `docker ps` para verificar containers healthy
- **Logs**: `docker logs api-aponta-staging --tail 100`
- **Database**: Queries diretas via psql para debug

## External Integrations

### Azure DevOps REST API

**Base URL**: `https://dev.azure.com/{organization}`

**Authentication**: Personal Access Token (PAT) via `Authorization: Basic` header

**Key Endpoints Used:**

| Endpoint | Purpose | API Version |
|----------|---------|-------------|
| `_apis/profile/profiles/me` | Get user profile | 6.0 |
| `_apis/projects` | List projects | 7.1 |
| `_apis/wit/wiql` | Query Work Items | 7.1 |
| `_apis/wit/workitems` | Get Work Item details | 7.1 |
| `_apis/wit/workitems/{id}/revisions` | Get revision history | 7.2-preview.3 |
| `_apis/work/processes/{processId}/workitemtypes/{witRefName}/states` | Get state categories | 7.1-preview.1 |

**Rate Limiting**: Azure DevOps has rate limits per PAT
- **Strategy**: Cache responses when possible (React Query frontend, in-memory backend)
- **Retry Strategy**: Exponential backoff with httpx retry configuration

**Error Handling**:
- `401 Unauthorized` → PAT inválido ou expirado
- `403 Forbidden` → PAT sem permissões necessárias
- `404 Not Found` → Work Item não existe ou não acessível
- `429 Too Many Requests` → Rate limit atingido (retry com backoff)

### PostgreSQL Database

**Connection**: Via SQLAlchemy async engine

**Schemas**:
- `aponta_sefaz_staging` - Ambiente de staging
- `aponta_sefaz` - Ambiente de produção

**Main Tables**:
- `apontamentos` - Registro de horas apontadas
- `atividades` - Atividades do projeto
- `projetos` - Projetos SEFAZ
- `alembic_version` - Controle de migrações

**Migration Strategy**: Alembic para versionamento de schema

## Observability & Failure Modes

<!-- Describe metrics, traces, or logs that monitor the flow. Note backoff, dead-letter, or compensating actions. -->

_Add descriptive content here (optional)._

## Related Resources

- [architecture.md](./architecture.md) - Arquitetura em camadas do sistema
- [security.md](./security.md) - Autenticação JWT e PAT
- [features/blue-cells.md](./features/blue-cells.md) - Feature Blue Cells completa
- [Azure DevOps REST API Docs](https://learn.microsoft.com/en-us/rest/api/azure/devops/)
