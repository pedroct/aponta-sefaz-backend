# Plano de Implementação - Blue Cells Feature

## Status: Backend Completo ✅ | Frontend Parcial ⏳

## 1. Backend (Completo ✅)

### Implementado:
- ✅ `AzureService.get_work_item_revisions()` - Busca histórico de revisões de Work Items
- ✅ `AzureService.get_process_work_item_states()` - Busca mapeamento de estados do processo
- ✅ Novos schemas Pydantic: `WorkItemRevisionsResponse`, `ProcessStateMapping`
- ✅ Endpoints REST:
  - `GET /api/v1/timesheet/work-item/{id}/revisions` 
  - `GET /api/v1/timesheet/process-states`
- ✅ Métodos no `TimesheetService` para integrar com Azure DevOps API

### Commit:
```
feat(timesheet): add blue cells API endpoints for historical work item states
- Add get_work_item_revisions() method to AzureService to fetch WI revision history
- Add get_process_work_item_states() to map state names to categories
- Create new endpoints: /timesheet/work-item/{id}/revisions and /timesheet/process-states
- Add Pydantic schemas: WorkItemRevisionsResponse and ProcessStateMapping
- Implement service methods to support blue cells feature in frontend
```

## 2. Frontend (Staging VPS - Parcial ⏳)

### Arquivos Criados na VPS:
- ✅ `/client/src/lib/blue-cells-logic.ts` - Lógica para determinar células azuis
- ✅ `/client/src/hooks/use-blue-cells.ts` - Hooks React Query para buscar revisões
- ✅ `/client/src/styles/blue-cells.css` - Estilos CSS para células azuis
- ✅ Tipos adicionados em `/client/src/lib/timesheet-types.ts`

### Pendente:
1. **Modificar `CelulaApontamento.tsx`**:
   ```typescript
   // Adicionar import
   import "@/styles/blue-cells.css";
   
   // Adicionar prop
   interface CelulaApontamentoProps {
     // ... props existentes
     isBlueCell?: boolean;
   }
   
   // Usar no cn()
   const celulaClasses = cn(
     // ... classes existentes
     isBlueCell && !temApontamentos && "blue-cell",
     isBlueCell && temApontamentos && "blue-cell has-hours",
   );
   ```

2. **Modificar `FolhaDeHoras.tsx`**:
   ```typescript
   // Importar hook e contexto do usuário
   import { useBlueCells } from "@/hooks/use-blue-cells";
   import { useAzureContext } from "@/contexts/AzureDevOpsContext";
   
   // No renderWorkItemRow(), para cada Task/Bug:
   const { blueCells } = useBlueCells({
     workItemId: item.id,
     organization,
     project,
     processId: "PROCESS_ID_DO_PROJETO", // Precisa obter do contexto
     workItemType: "Microsoft.VSTS.WorkItemTypes.Task",
     weekDates: item.dias.map(d => d.data),
     userId: currentUser.id,
     enabled: isLeafItem && !isLoading,
   });
   
   // Passar para CelulaApontamento
   <CelulaApontamento
     celula={dia}
     isBlueCell={blueCells[index]}
     // ... outras props
   />
   ```

3. **Importar CSS no main.tsx ou App.tsx**:
   ```typescript
   import "@/styles/blue-cells.css";
   ```

## 3. Informações Necessárias

### Process ID
Para obter o Process ID do projeto:
```bash
curl -u ":PAT" "https://dev.azure.com/{org}/_apis/projects/{project}?api-version=7.1"
```
O campo `capabilities.processTemplate.templateTypeId` contém o GUID do processo.

### Work Item Type Reference Names
- Task: `Microsoft.VSTS.WorkItemTypes.Task`
- Bug: `Microsoft.VSTS.WorkItemTypes.Bug`
- User Story: `Microsoft.VSTS.WorkItemTypes.UserStory`
- Feature: `Microsoft.VSTS.WorkItemTypes.Feature`
- Epic: `Microsoft.VSTS.WorkItemTypes.Epic`

## 4. Otimizações Implementadas

### Cache
- **Process States**: Cache de 1 hora (raramente muda)
- **Work Item Revisions**: Cache de 5 minutos (histórico é estático)

### Performance
- Busca de revisões apenas para Tasks/Bugs visíveis
- Memoização do cálculo de células azuis
- Queries em paralelo com React Query

## 5. Tratamento de Erros

- ✅ Se API de Revisions falhar, timesheet carrega normalmente sem destaques
- ✅ Fallback para mapeamento padrão de estados se Process API falhar
- ✅ Logging de erros no backend

## 6. Próximos Passos

1. Obter o Process ID do projeto DEV no Azure DevOps
2. Modificar manualmente `CelulaApontamento.tsx` na VPS
3. Modificar manualmente `FolhaDeHoras.tsx` na VPS  
4. Testar em staging
5. Commit das mudanças do frontend
6. Deploy para produção

## 7. Testes Recomendados

### Cenário 1: Work Item em "Active" atribuído ao usuário
- **Esperado**: Célula azul (sem horas) ou azul+amarelo (com horas)

### Cenário 2: Work Item em "Closed"
- **Esperado**: Sem destaque azul, edição bloqueada

### Cenário 3: Work Item atribuído a outro usuário
- **Esperado**: Sem destaque azul

### Cenário 4: Work Item mudou de estado durante a semana
- **Esperado**: Apenas os dias onde estava "InProgress" + atribuído ficam azuis

## 8. Referências

- Especificação original: `Untitled-1` (markdown com regras de negócio)
- Inspiração: 7pace Timetracker
- Azure DevOps Process API: https://learn.microsoft.com/en-us/rest/api/azure/devops/processes/states
- Azure DevOps Revisions API: https://learn.microsoft.com/en-us/rest/api/azure/devops/wit/revisions
