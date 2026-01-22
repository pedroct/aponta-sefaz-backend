---
type: doc
name: blue-cells-feature
description: Blue Cells feature for highlighting timesheet cells based on work item state history
category: features
created: 2026-01-22
status: implemented
version: 1.0.0
---

# Blue Cells Feature

## Overview

Blue Cells é uma funcionalidade de destaque visual no timesheet que indica automaticamente em quais dias o usuário deveria ter registrado horas, baseado no histórico de estados dos Work Items do Azure DevOps.

## Business Rules

Uma célula é destacada em azul quando:

1. **Estado do Work Item**: Na data da célula, o Work Item estava em estado categorizado como "InProgress"
2. **Atribuição**: Na data da célula, o Work Item estava atribuído ao usuário logado
3. **Existe Apontamento**: Se o usuário já registrou horas, a célula mostra um gradiente azul-amarelo

## Visual Behavior

| Condição | Cor de Fundo | Border |
|----------|--------------|--------|
| Blue Cell sem horas | `#DEECF9` (azul claro) | `1px solid #0078D4` |
| Blue Cell com horas | Gradiente `#FFF4CE` → `#DEECF9` | `1px solid #0078D4` |
| Célula normal | Branco | Cinza padrão |

## Technical Implementation

### Backend Endpoints

#### `GET /api/v1/timesheet/work-item/{id}/revisions`

Retorna o histórico completo de revisões de um Work Item.

**Query Parameters:**
- `organization_name` (required): Nome da organização Azure DevOps
- `project_id` (required): ID ou nome do projeto

**Response:**
```json
{
  "work_item_id": 123,
  "revisions": [
    {
      "rev": 1,
      "fields": {
        "System.ChangedDate": "2026-01-15T10:00:00Z",
        "System.State": "New",
        "System.AssignedTo": {
          "id": "user-guid",
          "displayName": "Pedro Costa"
        }
      }
    },
    {
      "rev": 2,
      "fields": {
        "System.ChangedDate": "2026-01-16T14:30:00Z",
        "System.State": "Active",
        "System.AssignedTo": {
          "id": "user-guid",
          "displayName": "Pedro Costa"
        }
      }
    }
  ]
}
```

**Implementation:**
- File: `app/routers/timesheet.py` (line ~136)
- Service: `app/services/timesheet_service.py` → `get_work_item_revisions()`
- Azure API: `app/services/azure.py` → `get_work_item_revisions()`
- Azure API Endpoint: `https://dev.azure.com/{org}/{project}/_apis/wit/workitems/{id}/revisions?api-version=7.2-preview.3`

#### `GET /api/v1/timesheet/process-states`

Retorna o mapeamento de estados para categorias (New, InProgress, Resolved, Completed, Removed).

**Query Parameters:**
- `organization_name` (required): Nome da organização
- `project_id` (required): ID do projeto
- `process_id` (required): ID do processo do projeto
- `work_item_type` (required): Tipo do Work Item (Task, Bug, etc.)

**Response:**
```json
{
  "state_map": {
    "New": "Proposed",
    "Active": "InProgress",
    "Resolved": "Resolved",
    "Closed": "Completed",
    "Removed": "Removed"
  }
}
```

**Implementation:**
- File: `app/routers/timesheet.py` (line ~145)
- Service: `app/services/timesheet_service.py` → `get_process_states()`
- Azure API: `app/services/azure.py` → `get_process_work_item_states()`
- Azure API Endpoint: `https://dev.azure.com/{org}/_apis/work/processes/{processId}/workitemtypes/{witRefName}/states?api-version=7.1-preview.1`

### Frontend Implementation

#### Core Algorithm

**File:** `client/src/lib/blue-cells-logic.ts`

```typescript
export function isBlueCell(
  revisions: WorkItemRevision[],
  cellDate: string,
  userId: string,
  stateMap: ProcessStateMap
): boolean
```

**Algorithm Steps:**
1. Filtra revisões até a data da célula (`System.ChangedDate <= cellDate`)
2. Ordena por data decrescente e pega a mais recente (estado ativo naquele dia)
3. Valida se o estado existe e busca a categoria no `stateMap`
4. Verifica se categoria === "InProgress" AND usuário está atribuído
5. Retorna `true` se ambas condições satisfeitas

#### React Hooks

**File:** `client/src/hooks/use-blue-cells.ts`

**Hook 1:** `useWorkItemRevisions()`
- Busca revisões de um Work Item específico
- Cache: 5 minutos (staleTime)
- Garbage collection: 30 minutos

**Hook 2:** `useProcessStates()`
- Busca mapeamento de estados do processo
- Cache: 1 hora (staleTime) - muda raramente
- Garbage collection: 24 horas

**Hook 3:** `useBlueCells()`
- Hook agregador que combina os dois anteriores
- Calcula array de 7 booleanos (um por dia da semana)
- Usa `React.useMemo` para evitar recálculos desnecessários

#### CSS Styles

**File:** `client/src/styles/blue-cells.css`

```css
.blue-cell {
  background-color: #DEECF9;
  border: 1px solid #0078D4;
  transition: background-color 0.2s ease;
}

.blue-cell.has-hours {
  background: linear-gradient(135deg, #FFF4CE 0%, #DEECF9 100%);
}
```

#### Component Integration

**Status:** ⏳ Pending Implementation

Components to modify:
1. `CelulaApontamento.tsx` - Add `isBlueCell` prop and apply CSS class
2. `WorkItemRowCells.tsx` - Create wrapper component to manage Blue Cells per Work Item
3. `FolhaDeHoras.tsx` - Use `useBlueCells` hook and pass data to cells

See: `docs/BLUE_CELLS_FRONTEND_INSTRUCTIONS.md` for step-by-step integration guide.

## Performance Considerations

### Caching Strategy

| Data Type | Cache Duration | Rationale |
|-----------|----------------|-----------|
| Work Item Revisions | 5 minutes | Muda quando WI é editado |
| Process State Mapping | 1 hour | Raramente muda |
| Blue Cells Calculation | Memoized | Recalcula apenas quando deps mudam |

### Optimization Techniques

1. **Batch Queries**: Buscar revisões apenas quando necessário (enabled flag)
2. **Memoization**: `React.useMemo` para evitar recálculos da lógica de Blue Cells
3. **Parallel Fetch**: React Query executa ambos hooks em paralelo
4. **Smart Re-fetching**: Apenas refetch quando staleTime expirar

### Expected Load

- **Staging**: ~10 usuários, ~100 Work Items
- **Production**: ~50 usuários, ~500 Work Items
- **API Calls per Page Load**: 
  - Initial: 1x process-states + N x work-item-revisions (N = work items on screen)
  - Subsequent: Served from cache

## Testing Recommendations

### Manual Testing Checklist

- [ ] Work Item em estado "Active" (InProgress) atribuído ao usuário → célula azul
- [ ] Work Item em estado "New" (Proposed) → célula branca
- [ ] Work Item atribuído a outro usuário → célula branca
- [ ] Célula azul com horas registradas → gradiente amarelo-azul
- [ ] Troca de semana → recalcula Blue Cells corretamente
- [ ] Work Item sem revisões → não quebra

### Unit Testing

**Backend:**
```bash
pytest tests/test_timesheet.py -v -k blue_cells
```

**Frontend:**
```bash
npm test -- blue-cells-logic.test.ts
```

## Deployment History

| Date | Environment | Commit | Status |
|------|-------------|--------|--------|
| 2026-01-22 22:15 | Staging Backend | `afe6f33`, `5a7c19a` | ✅ Deployed |
| 2026-01-22 22:21 | Staging Frontend | `6eea0a6`, `67b3a0f`, `025df25` | ✅ Deployed |
| TBD | Production | - | ⏳ Pending |

## Known Issues & Limitations

1. **Process ID Required**: Frontend needs to obtain Process ID from project metadata
   - **Workaround**: Hardcode common state mappings as fallback
   - **Solution**: Add endpoint to fetch project process ID

2. **Large Revision History**: Work Items com 100+ revisões podem ser lentos
   - **Mitigation**: Caching de 5 minutos reduz calls repetidas
   - **Future**: Implementar paginação na API de revisões

3. **Timezone Handling**: Datas são comparadas em UTC
   - **Impact**: Pode haver inconsistência em horários próximos à meia-noite
   - **Solution**: Normalizar todas datas para início do dia UTC

## Related Documentation

- `docs/BLUE_CELLS_IMPLEMENTATION_PLAN.md` - Plano de implementação completo
- `docs/BLUE_CELLS_FRONTEND_INSTRUCTIONS.md` - Guia de integração no frontend
- `.context/docs/data-flow.md` - Fluxo de dados completo do sistema
- `.context/docs/architecture.md` - Arquitetura geral

## Azure DevOps API References

- [Work Item Revisions API](https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/revisions/list?view=azure-devops-rest-7.2)
- [Process Work Item Types States API](https://learn.microsoft.com/en-us/rest/api/azure/devops/processes/states/list?view=azure-devops-rest-7.1)

## Authors & Contributors

- **Implementation**: GitHub Copilot + Pedro Costa
- **Review**: Pending
- **Specification**: `docs/BLUE_CELLS_FEATURE.md`
