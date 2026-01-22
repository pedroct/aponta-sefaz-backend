# Instruções Finais - Implementação Blue Cells no Frontend

## Arquivos Já Criados na VPS Staging ✅

1. `/home/ubuntu/aponta-sefaz/staging/frontend/client/src/lib/blue-cells-logic.ts`
2. `/home/ubuntu/aponta-sefaz/staging/frontend/client/src/hooks/use-blue-cells.ts`
3. `/home/ubuntu/aponta-sefaz/staging/frontend/client/src/styles/blue-cells.css`
4. Tipos adicionados em `timesheet-types.ts`

## Modificações Pendentes (Executar Manualmente)

### 1. Modificar `CelulaApontamento.tsx`

**Localização**: `/home/ubuntu/aponta-sefaz/staging/frontend/client/src/components/custom/CelulaApontamento.tsx`

**Mudanças**:

```typescript
// NO TOPO DO ARQUIVO - Adicionar import (linha 1)
import "@/styles/blue-cells.css";

// NA INTERFACE CelulaApontamentoProps - Adicionar nova prop
interface CelulaApontamentoProps {
  celula: CelulaDia;
  workItemId: number;
  workItemTitle: string;
  podeEditar: boolean;
  podeExcluir: boolean;
  isBlueCell?: boolean;  // ← ADICIONAR ESTA LINHA
  onNovoApontamento: (workItemId: number, workItemTitle: string, data: string) => void;
  onEditarApontamento: (apontamento: ApontamentoDia, workItemId: number, workItemTitle: string, data: string) => void;
  onExcluirApontamento: (apontamentoId: string, atividadeNome: string) => void;
}

// NO DESTRUCTURING - Adicionar isBlueCell
export function CelulaApontamento({
  celula,
  workItemId,
  workItemTitle,
  podeEditar,
  podeExcluir,
  isBlueCell = false,  // ← ADICIONAR ESTA LINHA
  onNovoApontamento,
  onEditarApontamento,
  onExcluirApontamento,
}: CelulaApontamentoProps) {

// NA DEFINIÇÃO DE celulaClasses - Adicionar classes blue-cell
  const celulaClasses = cn(
    "w-full h-full py-3 cursor-pointer transition-all text-[12px] relative",
    // Blue Cell (nova feature)
    isBlueCell && !temApontamentos && "blue-cell",
    isBlueCell && temApontamentos && "blue-cell has-hours",
    // Com horas registradas
    temApontamentos && "text-[#201F1E] font-black bg-[#FFF4CE] hover:bg-[#FFE8A3] shadow-inner",
    // Dia atual sem horas
    !temApontamentos && celula.eh_hoje && "bg-[#DEECF9] hover:bg-[#C7E0F4]",
    // ... resto do código
  );
```

### 2. Modificar `FolhaDeHoras.tsx`

**Localização**: `/home/ubuntu/aponta-sefaz/staging/frontend/client/src/pages/FolhaDeHoras.tsx`

**Mudanças**:

```typescript
// NO TOPO - Adicionar import
import { useWorkItemRevisions } from "@/hooks/use-blue-cells";
import { isBlueCell } from "@/lib/blue-cells-logic";

// NO COMPONENTE FolhaDeHoras - Adicionar estado para mapeamento de estados
const [stateMap] = useState<Record<string, string>>({
  // Mapeamento hardcoded inicial (pode ser carregado dinamicamente depois)
  "New": "Proposed",
  "Active": "InProgress",
  "Committed": "InProgress",
  "Open": "InProgress",
  "Em RF": "InProgress",
  "RF Pronto": "InProgress",
  "Em Prototipação": "InProgress",
  "Em RT": "InProgress",
  "RT Pronto": "InProgress",
  "Em Desenvolvimento": "InProgress",
  "A Revisar": "InProgress",
  "Em Revisão": "InProgress",
  "A Testar": "InProgress",
  "Em Testes": "InProgress",
  "Em Homologação": "InProgress",
  "Resolved": "Resolved",
  "Closed": "Completed",
  "Done": "Completed",
  "Entregue": "Completed",
  "Corrigido": "Completed",
  "Removed": "Removed",
  "Cancelado": "Removed",
});

// NA FUNÇÃO renderWorkItemRow - Modificar a parte que renderiza células para Tasks/Bugs

// ANTES (linha ~210):
{item.dias.map((dia, index) => (
  <td key={index} className="border-r border-[#EDEBE9] text-center p-0 relative">
    {isLeafItem ? (
      <CelulaApontamento
        celula={dia}
        workItemId={item.id}
        workItemTitle={item.title}
        podeEditar={item.pode_editar}
        podeExcluir={item.pode_excluir}
        onNovoApontamento={(wId, wTitle, data) => handleNovoApontamento(wId, wTitle, data, item.pode_editar)}
        onEditarApontamento={(ap, wId, wTitle, data) => handleEditarApontamento(ap, wId, wTitle, data, item.pode_editar)}
        onExcluirApontamento={(apId, nome) => handleExcluirApontamento(apId, nome, item.pode_excluir)}
      />
    ) : (
      // ... células vazias para níveis pai
    )}
  </td>
))}

// DEPOIS (substituir por):
{item.dias.map((dia, index) => {
  // Buscar revisões para Tasks/Bugs (somente se isLeafItem)
  const { data: revisionsData } = useWorkItemRevisions({
    workItemId: item.id,
    organization,
    project,
    enabled: isLeafItem && !isLoading,
  });
  
  // Calcular se é célula azul
  const isBlueCellForDay = isLeafItem && revisionsData && currentUser?.id
    ? isBlueCell(
        revisionsData.revisions,
        dia.data,
        currentUser.id,
        stateMap
      )
    : false;
  
  return (
    <td key={index} className="border-r border-[#EDEBE9] text-center p-0 relative">
      {isLeafItem ? (
        <CelulaApontamento
          celula={dia}
          workItemId={item.id}
          workItemTitle={item.title}
          podeEditar={item.pode_editar}
          podeExcluir={item.pode_excluir}
          isBlueCell={isBlueCellForDay}  // ← ADICIONAR ESTA LINHA
          onNovoApontamento={(wId, wTitle, data) => handleNovoApontamento(wId, wTitle, data, item.pode_editar)}
          onEditarApontamento={(ap, wId, wTitle, data) => handleEditarApontamento(ap, wId, wTitle, data, item.pode_editar)}
          onExcluirApontamento={(apId, nome) => handleExcluirApontamento(apId, nome, item.pode_excluir)}
        />
      ) : (
        // Células vazias para níveis pai (Epic, Feature, Story)
        <div className={cn(
          "w-full h-full py-3",
          dia.eh_hoje && "bg-[#EFF6FC]/30",
          dia.eh_fim_semana && "bg-[#F3F2F1]/30"
        )} />
      )}
    </td>
  );
})}
```

**IMPORTANTE**: Hooks não podem ser chamados dentro de loops! A solução acima está INCORRETA.

**SOLUÇÃO CORRETA**: Usar um hook separado para cada Work Item.

Criar um componente wrapper:

```typescript
// CRIAR NOVO ARQUIVO: /home/ubuntu/aponta-sefaz/staging/frontend/client/src/components/custom/WorkItemRow.tsx

import React from "react";
import { cn } from "@/lib/utils";
import { CelulaApontamento } from "./CelulaApontamento";
import { WorkItemTimesheet } from "@/lib/timesheet-types";
import { useWorkItemRevisions } from "@/hooks/use-blue-cells";
import { isBlueCell } from "@/lib/blue-cells-logic";
import { useAzureContext } from "@/contexts/AzureDevOpsContext";

interface WorkItemRowCellsProps {
  item: WorkItemTimesheet;
  isLeafItem: boolean;
  organization: string;
  project: string;
  stateMap: Record<string, string>;
  onNovoApontamento: (wId: number, wTitle: string, data: string, podeEditar: boolean) => void;
  onEditarApontamento: (ap: any, wId: number, wTitle: string, data: string, podeEditar: boolean) => void;
  onExcluirApontamento: (apId: string, nome: string, podeExcluir: boolean) => void;
}

export function WorkItemRowCells({
  item,
  isLeafItem,
  organization,
  project,
  stateMap,
  onNovoApontamento,
  onEditarApontamento,
  onExcluirApontamento,
}: WorkItemRowCellsProps) {
  const { context } = useAzureContext();
  
  // Buscar revisões apenas para Tasks/Bugs
  const { data: revisionsData } = useWorkItemRevisions({
    workItemId: item.id,
    organization,
    project,
    enabled: isLeafItem,
  });
  
  return (
    <>
      {item.dias.map((dia, index) => {
        // Calcular se é célula azul para este dia
        const isBlueCellForDay = isLeafItem && revisionsData && context?.userId
          ? isBlueCell(
              revisionsData.revisions,
              dia.data,
              context.userId,
              stateMap
            )
          : false;
        
        return (
          <td key={index} className="border-r border-[#EDEBE9] text-center p-0 relative">
            {isLeafItem ? (
              <CelulaApontamento
                celula={dia}
                workItemId={item.id}
                workItemTitle={item.title}
                podeEditar={item.pode_editar}
                podeExcluir={item.pode_excluir}
                isBlueCell={isBlueCellForDay}
                onNovoApontamento={(wId, wTitle, data) => onNovoApontamento(wId, wTitle, data, item.pode_editar)}
                onEditarApontamento={(ap, wId, wTitle, data) => onEditarApontamento(ap, wId, wTitle, data, item.pode_editar)}
                onExcluirApontamento={(apId, nome) => onExcluirApontamento(apId, nome, item.pode_excluir)}
              />
            ) : (
              <div className={cn(
                "w-full h-full py-3",
                dia.eh_hoje && "bg-[#EFF6FC]/30",
                dia.eh_fim_semana && "bg-[#F3F2F1]/30"
              )} />
            )}
          </td>
        );
      })}
    </>
  );
}
```

Depois em `FolhaDeHoras.tsx`:

```typescript
import { WorkItemRowCells } from "@/components/custom/WorkItemRowCells";

// No renderWorkItemRow, substituir o map de item.dias por:
<WorkItemRowCells
  item={item}
  isLeafItem={isLeafItem}
  organization={organization}
  project={project}
  stateMap={stateMap}
  onNovoApontamento={handleNovoApontamento}
  onEditarApontamento={handleEditarApontamento}
  onExcluirApontamento={handleExcluirApontamento}
/>
```

## Comandos para Aplicar na VPS

```bash
# SSH na VPS
ssh -i C:\Users\pedro\.ssh\hostinger_github_deploy_key root@92.112.178.252

# Ir para o diretório do frontend
cd /home/ubuntu/aponta-sefaz/staging/frontend

# Editar os arquivos manualmente
nano client/src/components/custom/CelulaApontamento.tsx
nano client/src/pages/FolhaDeHoras.tsx

# OU criar o componente WorkItemRowCells
nano client/src/components/custom/WorkItemRowCells.tsx

# Rebuild do container
docker compose down
docker compose up --build -d

# Ver logs
docker compose logs -f
```

## Testar

1. Abrir a extensão no Azure DevOps
2. Acessar a aba Timesheet
3. Verificar se células de Tasks/Bugs atribuídos ao usuário em estado "InProgress" ficam azuis
4. Verificar se células com horas ficam azul+amarelo (gradiente)

## Fallback Se Algo Falhar

Se a API de revisões falhar, o timesheet continua funcionando normalmente, apenas sem os destaques azuis.
