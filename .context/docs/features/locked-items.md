---
type: doc
name: locked-items-feature
description: Work Item locking feature to prevent time entry on completed/removed items
category: features
created: 2026-01-22
status: backend-implemented
version: 1.0.0
---

# Locked Items Feature (Bloqueio de Itens Fechados)

## Overview

A feature de Bloqueio de Itens Fechados é uma trava de segurança que impede usuários de registrarem tempo em Work Items que já foram concluídos (Completed) ou cancelados (Removed). Implementa validação tanto no backend (fail-safe) quanto no frontend (UX visual).

## Business Rules

O sistema deve **bloquear qualquer entrada ou edição de tempo** se o estado atual do Work Item pertencer às categorias:

1. **`Completed`** - Work Item concluído (ex: Done, Closed, Entregue, Corrigido)
2. **`Removed`** - Work Item cancelado (ex: Removed, Cancelado, Deleted)

### UI Behavior

| Condição | Comportamento |
|----------|--------------|
| Work Item Completed | Célula bloqueada com background cinza claro |
| Work Item Removed | Célula bloqueada com background cinza claro |
| Hover sobre célula bloqueada | Tooltip: "Este item de trabalho está fechado" |
| Clique/Enter em célula bloqueada | Sem ação (eventos desabilitados) |

## State Mapping (Kanban v1.0.0)

| Nome do Estado | Categoria Azure | Comportamento |
|----------------|-----------------|---------------|
| Entregue | Completed | **Bloquear** |
| Corrigido | Completed | **Bloquear** |
| Done | Completed | **Bloquear** |
| Closed | Completed | **Bloquear** |
| Cancelado | Removed | **Bloquear** |
| Removed | Removed | **Bloquear** |
| Em Homologação | InProgress | Permitir |
| Em Testes | InProgress | Permitir |
| Active | InProgress | Permitir |

## Technical Implementation

### Backend Implementation ✅

#### 1. Azure Batch API Integration

**Method:** `AzureService.get_work_items_current_state_batch()`

```python
async def get_work_items_current_state_batch(
    self,
    work_item_ids: list[int],
    organization_name: str | None,
    project: str | None,
) -> dict[int, dict]:
```

**Azure API:** `POST https://dev.azure.com/{org}/_apis/wit/workitemsbatch?api-version=7.2`

**Payload:**
```json
{
  "ids": [123, 456, 789],
  "fields": ["System.Id", "System.State", "System.WorkItemType", "System.AssignedTo"]
}
```

**Response:**
```python
{
  123: {
    "id": 123,
    "state": "Entregue",
    "type": "Task",
    "assigned_to": {...}
  },
  456: {
    "id": 456,
    "state": "Active",
    "type": "Bug",
    "assigned_to": {...}
  }
}
```

#### 2. REST API Endpoint

**Endpoint:** `GET /api/v1/timesheet/work-items/current-state`

**Query Parameters:**
- `work_item_ids` (required): Comma-separated IDs (ex: "123,456,789")
- `organization_name` (required): Nome da organização Azure DevOps
- `project_id` (required): ID do projeto

**Example Request:**
```bash
GET /api/v1/timesheet/work-items/current-state?work_item_ids=123,456&organization_name=sefaz&project_id=MyProject
Authorization: Bearer {jwt_token}
```

**Example Response (200 OK):**
```json
{
  "work_items": {
    "123": {
      "id": 123,
      "state": "Entregue",
      "type": "Task",
      "assigned_to": {
        "id": "user-guid",
        "displayName": "Pedro Costa"
      }
    },
    "456": {
      "id": 456,
      "state": "Active",
      "type": "Bug",
      "assigned_to": null
    }
  }
}
```

**Implementation Files:**
- `app/services/azure.py` - Line ~450: `get_work_items_current_state_batch()`
- `app/services/timesheet_service.py` - Line ~745: `get_work_items_current_state()`
- `app/routers/timesheet.py` - Line ~195: Endpoint definition
- `app/schemas/timesheet.py` - Line ~215: Schemas `WorkItemCurrentState`, `WorkItemsCurrentStateResponse`

#### 3. Validation on Create/Update Apontamento

**Method:** `ApontamentoService._validate_work_item_state()`

```python
async def _validate_work_item_state(
    self,
    work_item_id: int,
    organization: str,
    project: str,
) -> None:
```

**Validation Logic:**
1. Fetch current state via Batch API
2. Check if state is in `state_categories_completed` or `state_categories_removed`
3. Raise `HTTPException(422)` if blocked

**Error Response (422 Unprocessable Entity):**
```json
{
  "detail": "Não é possível lançar horas em Work Item fechado (estado: Entregue)"
}
```

**Integration Points:**
- Called in `ApontamentoService.criar_apontamento()` - Before creating record
- Called in `ApontamentoService.atualizar_apontamento()` - Before updating record
- Prevents database write if validation fails

**State Mapping (Hardcoded):**
```python
state_categories_completed = {
    "Done", "Closed", "Entregue", "Corrigido", "Concluído", "Completo"
}
state_categories_removed = {
    "Removed", "Cancelado", "Deleted", "Excluído"
}
```

> **Note:** Future improvement would use Process API to get dynamic state→category mapping

**Files Modified:**
- `app/services/apontamento_service.py` - Lines 182-257: Validation method and integration

### Frontend Implementation ⏳

**Status:** Backend complete, frontend pending

#### Algorithm (Pseudo-code from spec)

```typescript
function isEditAllowed(workItemId, currentStateMap, processMetadata) {
  const currentState = currentStateMap[workItemId].state;
  const category = processMetadata[currentState];

  if (category === 'Completed' || category === 'Removed') {
    return {
      allowed: false,
      reason: "Item fechado ou cancelado"
    };
  }

  return { allowed: true };
}
```

#### Planned Frontend Files

1. **`client/src/lib/locked-items-logic.ts`**
   - Function `isWorkItemLocked(state: string, stateMap: ProcessStateMap): boolean`
   - Returns true if state category is Completed or Removed

2. **`client/src/hooks/use-locked-items.ts`**
   - Hook `useWorkItemsCurrentState(workItemIds: number[])` - React Query
   - Hook `useLockedItems(workItemIds: number[], stateMap: ProcessStateMap)` - Combines state + category
   - Cache: 2 minutes (states can change frequently)

3. **`client/src/styles/locked-cells.css`**
   ```css
   .locked-cell {
     background-color: #F3F3F3;
     cursor: not-allowed;
     opacity: 0.7;
   }
   
   .locked-cell:hover {
     background-color: #E8E8E8;
   }
   ```

4. **Component Modifications:**
   - `CelulaApontamento.tsx` - Add `isLocked` prop, disable events, show tooltip
   - `WorkItemRow.tsx` - Fetch locked state and pass to cells
   - `FolhaDeHoras.tsx` - Provide state map context

#### UI Components

**Locked Cell Visual:**
- Background: `#F3F3F3` (light gray)
- Cursor: `not-allowed`
- Opacity: 0.7
- No hover highlight
- Tooltip on hover: "Este item de trabalho está fechado"

**Event Handling:**
- `onDoubleClick` → Disabled
- `onKeyDown` (Enter/Tab) → Disabled
- `onClick` → Show tooltip briefly

## Performance Considerations

### Caching Strategy

| Data Type | Cache Duration | Rationale |
|-----------|----------------|-----------|
| Work Item Current States | 2 minutes | Can change when users edit in Azure DevOps |
| Process State Mapping | 1 hour | Rarely changes (reuse from Blue Cells) |

### Optimization Techniques

1. **Batch API**: Fetch all visible Work Items in single request
2. **Conditional Fetch**: Only fetch if not cached or stale
3. **Parallel Queries**: Fetch states and process mapping in parallel
4. **Fail-Soft**: Don't block UI if validation API fails (backend validates anyway)

### Expected Load

- **API Call Frequency**: Once per page load + every 2 minutes (refetch)
- **Batch Size**: ~10-50 Work Items per timesheet page
- **Response Time**: < 500ms (Azure Batch API is fast)

## Testing Recommendations

### Manual Testing Checklist

Backend:
- [ ] GET endpoint returns correct current states
- [ ] POST apontamento blocked for Completed Work Item (422 error)
- [ ] POST apontamento blocked for Removed Work Item (422 error)
- [ ] POST apontamento allowed for InProgress Work Item
- [ ] Error message is clear and helpful

Frontend (pending):
- [ ] Locked cells have gray background
- [ ] Tooltip shows on hover
- [ ] Double-click disabled on locked cells
- [ ] Keyboard navigation skips locked cells
- [ ] Backend validation catches edge cases

### Unit Testing

**Backend:**
```bash
pytest tests/test_apontamento_service.py -v -k locked
```

**Frontend:**
```bash
npm test -- locked-items-logic.test.ts
```

## Deployment History

| Date | Environment | Component | Commit | Status |
|------|-------------|-----------|--------|--------|
| 2026-01-22 | Staging | Backend | `e80ef0f` | ✅ Deployed |
| TBD | Staging | Frontend | - | ⏳ Pending |
| TBD | Production | Backend | - | ⏳ Pending |
| TBD | Production | Frontend | - | ⏳ Pending |

**Backend Commit:** `e80ef0f` - feat(timesheet): implementa bloqueio de itens fechados

## Known Issues & Limitations

1. **Hardcoded State Names**: Backend uses hardcoded Portuguese/English state names
   - **Impact**: May not work with custom state names in other languages
   - **Solution**: Integrate with Process API to get dynamic state→category mapping

2. **Race Condition**: State can change between validation and save
   - **Mitigation**: Backend validates again before save (fail-safe)
   - **Impact**: User might see success but backend rejects (rare)

3. **Cache Staleness**: Frontend cache might show stale state for 2 minutes
   - **Mitigation**: Backend always validates with fresh data
   - **Impact**: UI shows unlocked but save fails (acceptable UX)

4. **Network Failure**: If Batch API fails, validation is skipped
   - **Rationale**: Don't block legitimate work due to network issues
   - **Risk**: User might successfully save on locked item (very rare)

## Security Considerations

- ✅ **Backend Validation**: Primary security layer (cannot be bypassed)
- ✅ **PAT Authentication**: Uses backend PAT, not user token
- ✅ **HTTP 422**: Clear error code for locked items
- ⚠️ **Frontend Bypass**: Frontend lock is UX only (backend validates)

## Related Documentation

- [Blue Cells Feature](./blue-cells.md) - Similar state validation pattern
- [Data Flow](../data-flow.md) - Azure DevOps integration architecture
- [Changelog](../changelog.md) - Feature history

## API References

- [Azure DevOps Work Items Batch API](https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/work-items/get-work-items-batch?view=azure-devops-rest-7.2)
- [Process States API](https://learn.microsoft.com/en-us/rest/api/azure/devops/processes/states/list?view=azure-devops-rest-7.1)

## Authors & Contributors

- **Implementation**: GitHub Copilot + Pedro Costa
- **Backend Status**: ✅ Complete (commit e80ef0f)
- **Frontend Status**: ⏳ Pending implementation
- **Specification**: Untitled-2 document

## Migration Notes

When deploying to production:

1. ✅ Backend changes are backward compatible
2. ⚠️ Frontend must be deployed together (not independently)
3. ✅ No database migration required
4. ✅ No configuration changes needed
5. ⚠️ Update state mapping if using custom process template
