---
type: doc
name: changelog
description: Record of significant changes and features added to the system
category: project
created: 2026-01-22
status: active
---

# Sistema Aponta - Changelog

## [Unreleased]

### Pending
- Integração de componentes React para Blue Cells
- Deploy para produção da feature Blue Cells
- Testes automatizados para Blue Cells

## [2026-01-22] - Blue Cells Feature

### Added - Backend

**New Endpoints:**
- `GET /api/v1/timesheet/work-item/{id}/revisions` - Retorna histórico de revisões de Work Item
- `GET /api/v1/timesheet/process-states` - Retorna mapeamento estado → categoria

**Files Modified:**
- `app/routers/timesheet.py` - Adicionados 2 novos endpoints (linhas 136-187)
- `app/services/timesheet_service.py` - Adicionados métodos `get_work_item_revisions()` e `get_process_states()`
- `app/services/azure.py` - Adicionados métodos `get_work_item_revisions()` e `get_process_work_item_states()`
- `app/schemas/timesheet.py` - Adicionadas schemas: `WorkItemRevisionFields`, `WorkItemRevision`, `WorkItemRevisionsResponse`, `ProcessStateMappingResponse`

**Azure DevOps APIs Integrated:**
- Work Item Revisions API v7.2-preview.3
- Process Work Item Types States API v7.1-preview.1

**Commits:**
- `afe6f33` - feat(timesheet): adiciona endpoint para revisões de Work Items
- `5a7c19a` - feat(timesheet): adiciona endpoint para estados de processo

### Added - Frontend

**New Files:**
- `client/src/lib/blue-cells-logic.ts` - Algoritmo principal para determinar células azuis
  - Função `isBlueCell()` - Determina se célula individual deve ser azul
  - Função `getBlueCellsForWeek()` - Calcula array de 7 booleanos para semana
  
- `client/src/hooks/use-blue-cells.ts` - React Query hooks
  - Hook `useWorkItemRevisions()` - Busca revisões com cache de 5min
  - Hook `useProcessStates()` - Busca estados com cache de 1h
  - Hook `useBlueCells()` - Agregador com memoization
  
- `client/src/styles/blue-cells.css` - Estilos CSS para células azuis
  - Class `.blue-cell` - Background azul claro (#DEECF9)
  - Class `.blue-cell.has-hours` - Gradiente amarelo → azul

- `client/src/lib/timesheet-types.ts` - TypeScript types
  - Interface `WorkItemRevisionFields`
  - Interface `WorkItemRevision`
  - Interface `WorkItemRevisionsResponse`
  - Type `ProcessStateMap`
  - Interface `ProcessStateMappingResponse`

**Commits:**
- `6eea0a6` - feat(blue-cells): adiciona lógica e hooks para Blue Cells
- `67b3a0f` - fix(hooks): corrige URLs incompletas no use-blue-cells.ts
- `025df25` - fix(blue-cells): adiciona validação de state null/undefined

### Deployed

**Staging Backend** (2026-01-22 22:15 UTC):
- Container: `api-aponta-staging`
- Commits: `afe6f33`, `5a7c19a`
- Status: ✅ Healthy

**Staging Frontend** (2026-01-22 22:21 UTC):
- Container: `fe-aponta-staging`
- Commits: `6eea0a6`, `67b3a0f`, `025df25`
- Bundle: 535.95 KB (3098 modules)
- Status: ✅ Healthy

### Documentation

**New Documents:**
- `docs/BLUE_CELLS_IMPLEMENTATION_PLAN.md` - Plano técnico completo
- `docs/BLUE_CELLS_FRONTEND_INSTRUCTIONS.md` - Guia passo-a-passo de integração
- `.context/docs/features/blue-cells.md` - Documentação para LLMs

**Updated Documents:**
- `.context/docs/README.md` - Adicionada seção "Features Documentation"
- `.context/docs/data-flow.md` - Atualizado com fluxo Blue Cells
- `.context/docs/changelog.md` - Criado este arquivo

## [2026-01-15 to 2026-01-21] - Previous Work

### Infrastructure
- Configuração de GitHub Actions para deploy automático
- Setup de ambiente staging separado do produção
- Configuração de Nginx com SSL/TLS

### Core Features
- Sistema de apontamentos de horas
- Integração com Azure DevOps Work Items
- Autenticação JWT + PAT
- CRUD de projetos e atividades

## Version History Format

Formato baseado em [Keep a Changelog](https://keepachangelog.com/):

- **Added** - Novas features
- **Changed** - Mudanças em features existentes
- **Deprecated** - Features que serão removidas
- **Removed** - Features removidas
- **Fixed** - Bug fixes
- **Security** - Vulnerabilidades corrigidas

## Links

- **Repository Backend**: https://github.com/pedroct/aponta-sefaz-backend
- **Repository Frontend**: https://github.com/pedroct/aponta-sefaz-frontend
- **Staging URL**: https://staging-aponta.treit.com.br
- **Production URL**: https://aponta.treit.com.br
