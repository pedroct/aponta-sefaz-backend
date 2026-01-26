# Contexto para Frontend: Adicionar Coluna "Saldo" (S)

**Data:** 22/01/2026  
**Backend:** Implementado e deployado em staging

---

## Objetivo

Adicionar a coluna **S (Saldo )** entre as colunas **H (Histórico)** e **SEG (Segunda-feira)** na grade do timesheet.

---

## Dados do Backend

O endpoint `/api/v1/timesheet` já retorna o campo `remaining_work` em cada Work Item.

### Estrutura da Resposta (WorkItemTimesheet)

```typescript
interface WorkItemTimesheet {
  id: number;
  title: string;
  type: string;
  state: string;
  state_category: string;
  icon_url: string;
  assigned_to: string | null;
  
  // Campos de esforço do Azure DevOps
  original_estimate: number | null;  // Coluna E (Estimado)
  completed_work: number | null;      // Total de horas completadas
  remaining_work: number | null;      // Coluna S (Saldo) ⬅️ USAR ESTE
  
  // Totais da semana (apontamentos locais)
  total_semana_horas: number;         // Coluna H (Histórico)
  total_semana_formatado: string;     // H formatado HH:mm
  
  // Células dos dias
  dias: CelulaDia[];
  
  // Hierarquia
  nivel: number;
  parent_id: number | null;
  children: WorkItemTimesheet[];
  
  // Permissões
  pode_editar: boolean;
  pode_excluir: boolean;
}
```

---

## Implementação no Frontend

### 1. Adicionar nova coluna no cabeçalho

Entre a coluna **H** e **SEG**, adicionar:

```tsx
// Após a coluna H (Histórico)
<th className="...">S</th>  // Saldo
// Antes da coluna SEG
```

**Tooltip/title**: "Saldo - Trabalho Restante (Original Estimate - Completed Work)"

### 2. Adicionar célula em cada linha de Work Item

```tsx
// Na renderização de cada WorkItem
<td className="text-center text-sm">
  {workItem.remaining_work !== null 
    ? workItem.remaining_work.toFixed(2)  // ou toFixed(0) se preferir inteiro
    : '-'
  }
</td>
```

### 3. Ordem das colunas (atualizada)

| Posição | Coluna | Campo | Descrição |
|---------|--------|-------|-----------|
| 1 | **ESCOPO DE TRABALHO** | `title` | Título do Work Item |
| 2 | **E** | `original_estimate` | Estimado (Original Estimate) |
| 3 | **H** | `total_semana_horas` | Histórico da semana |
| 4 | **S** ⬅️ NOVA | `remaining_work` | Saldo (Remaining Work) |
| 5 | **SEG** | `dias[0]` | Segunda-feira |
| 6 | **TER** | `dias[1]` | Terça-feira |
| 7 | **QUA** | `dias[2]` | Quarta-feira |
| 8 | **QUI** | `dias[3]` | Quinta-feira |
| 9 | **SEX** | `dias[4]` | Sexta-feira |
| 10 | **SÁB** | `dias[5]` | Sábado |
| 11 | **DOM** | `dias[6]` | Domingo |
| 12 | **SEMANAL Σ** | soma dos dias | Total semanal |

### 4. Estilo sugerido

A coluna **S** deve ter o mesmo estilo das colunas **E** e **H**:
- Largura fixa (~40-50px)
- Texto centralizado
- Cor de fundo levemente diferenciada (como E e H)

---

## Lógica de Cálculo (Referência)

O `remaining_work` é calculado automaticamente pelo backend quando um apontamento é criado/editado/excluído:

```
remaining_work = original_estimate - completed_work
```

**Exemplo:**
- Se `original_estimate` = 8h e foram apontadas 2h:
  - `completed_work` = 2h
  - `remaining_work` = 6h (8 - 2)

---

## Exemplo Visual Esperado

```
| ESCOPO DE TRABALHO              | E | H    | S    | SEG | TER | QUA | QUI | SEX | SÁB | DOM | SEMANAL Σ |
|--------------------------------|---|------|------|-----|-----|-----|-----|-----|-----|-----|-----------|
| #4 C01. Implementar Extensão   | 8 | 2.5  | 5.5  |     |     |01:00|01:30|     |     |     | 02:30     |
| #8 Testar Apontamento          | 2 |      | 2    |     |     |     |     |     |     |     |           |
```

---

## Notas Importantes

1. O campo `remaining_work` pode ser `null` se o Work Item não tiver `OriginalEstimate` definido no Azure DevOps
2. Se for `null`, exibir "-" ou deixar vazio
3. A coluna **S** não precisa de linha de totais (diferente de **H** que soma os apontamentos)
4. O valor é atualizado automaticamente no Azure DevOps quando apontamentos são criados/editados/excluídos

---

## Endpoint de Referência

```
GET /api/v1/timesheet?organization_name={org}&project_id={project}&week_start={YYYY-MM-DD}
```

**Headers:**
```
Authorization: Bearer {app_token}
```
