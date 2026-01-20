# 🏗️ ARQUITETURA: Apontamentos (Frontend-Only)

## Visão Geral

```
┌────────────────────────────────────────────────────────────────┐
│                      CLIENTE (Browser)                         │
│                                                                │
│  http://localhost:5000                                         │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  React App (fe-aponta)                                   │ │
│  │  ├─ client/src/                                          │ │
│  │  │  ├─ components/                                       │ │
│  │  │  │  ├─ custom/ModalAdicionarTempo.tsx               │ │
│  │  │  │  │  └─ Formulário para adicionar apontamentos    │ │
│  │  │  │  └─ ui/                                           │ │
│  │  │  │     └─ shadcn/ui components (Button, Input, etc) │ │
│  │  │  ├─ hooks/                                           │ │
│  │  │  │  ├─ use-api.ts (IMPORTANTE: aponta para :8000)  │ │
│  │  │  │  ├─ use-atividades.ts                            │ │
│  │  │  │  ├─ use-current-user.ts                          │ │
│  │  │  │  └─ use-search-work-items.ts                     │ │
│  │  │  ├─ pages/                                           │ │
│  │  │  │  └─ PaginaPrincipal.tsx (timesheet grid)        │ │
│  │  │  └─ lib/                                             │ │
│  │  │     └─ api-client.ts (tipos TypeScript)             │ │
│  │  └─ Vite dev server :5000                              │ │
│  └──────────────────────────────────────────────────────────┘ │
└──────────────────┬─────────────────────────────────────────────┘
                   │
        HTTP REST Requests
        /api/v1/apontamentos
        /api/v1/work-items/search
        /api/v1/user
        /api/v1/atividades
                   │
                   ▼
┌────────────────────────────────────────────────────────────────┐
│                      SERVIDOR BACKEND                          │
│                                                                │
│  http://localhost:8000 (FastAPI ou equivalente)                │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  API REST (/api/v1/)                                     │ │
│  │                                                           │ │
│  │  ├─ POST /apontamentos                                   │ │
│  │  │  └─ Validação → DB → Azure Sync → Response          │ │
│  │  │                                                       │ │
│  │  ├─ GET /apontamentos/{id}                              │ │
│  │  ├─ PUT /apontamentos/{id}                              │ │
│  │  ├─ DELETE /apontamentos/{id}                           │ │
│  │  │                                                       │ │
│  │  ├─ GET /apontamentos/work-item/{id}                    │ │
│  │  ├─ GET /apontamentos/work-item/{id}/resumo             │ │
│  │  ├─ GET /apontamentos/work-item/{id}/azure-info        │ │
│  │  │                                                       │ │
│  │  ├─ GET /work-items/search                              │ │
│  │  ├─ GET /user                                           │ │
│  │  │                                                       │ │
│  │  ├─ GET /atividades                                     │ │
│  │  └─ GET /atividades/{id}                                │ │
│  │                                                           │ │
│  └──────────────────┬───────────────────────────────────────┘ │
│                     │                                         │
│  ┌──────────────────▼───────────────────────────────────────┐ │
│  │  Business Logic & Services                               │ │
│  │                                                           │ │
│  │  ├─ ApontamentoService                                   │ │
│  │  │  ├─ criar() → save DB + sync Azure + retry queue    │ │
│  │  │  ├─ atualizar() → update DB + delta sync             │ │
│  │  │  ├─ deletar() → delete DB + reverse sync             │ │
│  │  │  └─ listar()                                          │ │
│  │  │                                                       │ │
│  │  ├─ AzureDevOpsService                                   │ │
│  │  │  ├─ searchWorkItems(WIQL)                            │ │
│  │  │  ├─ updateCompletedWork()                            │ │
│  │  │  ├─ getWorkItem()                                     │ │
│  │  │  └─ getCurrentUser()                                  │ │
│  │  │                                                       │ │
│  │  ├─ SyncService                                          │ │
│  │  │  ├─ syncToAzure()                                     │ │
│  │  │  ├─ retryFailedSyncs()                               │ │
│  │  │  └─ calculateDeltas()                                 │ │
│  │  │                                                       │ │
│  │  └─ AtividadeService                                     │ │
│  │     └─ listar()                                          │ │
│  │                                                           │ │
│  └──────────────────┬───────────────────────────────────────┘ │
│                     │                                         │
│  ┌──────────────────▼───────────────────────────────────────┐ │
│  │  Data Layer                                              │ │
│  │                                                           │ │
│  │  Database (SQLite ou PostgreSQL)                          │ │
│  │  ├─ apontamentos                                          │ │
│  │  │  └─ id, work_item_id, data, duracao, atividade, etc  │ │
│  │  │                                                       │ │
│  │  ├─ atividades                                           │ │
│  │  │  └─ id, nome, descricao, ativo                       │ │
│  │  │                                                       │ │
│  │  └─ sync_queue (para retry de falhas)                   │ │
│  │     └─ apontamento_id, tentativas, proximo_retry       │ │
│  │                                                           │ │
│  └──────────────────┬───────────────────────────────────────┘ │
│                     │                                         │
└─────────────────────┼─────────────────────────────────────────┘
                      │
            PATCH: Sync com Azure DevOps
                      │
                      ▼
┌────────────────────────────────────────────────────────────────┐
│              AZURE DEVOPS CLOUD                                │
│              https://dev.azure.com                             │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  Work Items (Projects: DEV, DEMO, MODELO)               │ │
│  │                                                           │ │
│  │  ├─ Epic #1                                              │ │
│  │  │  ├─ Feature #10                                       │ │
│  │  │  │  ├─ User Story #100                               │ │
│  │  │  │  │  ├─ Task #1001                                 │ │
│  │  │  │  │  │  ├─ State: Active                           │ │
│  │  │  │  │  │  ├─ OriginalEstimate: 20h                  │ │
│  │  │  │  │  │  ├─ CompletedWork: 12.5h ◄── UPDATED       │ │
│  │  │  │  │  │  └─ RemainingWork: 7.5h ◄── UPDATED        │ │
│  │  │  │  │  └─ Task #1002                                 │ │
│  │  │  │  │     └─ ...                                      │ │
│  │  │  │  └─ User Story #101                               │ │
│  │  │  │     └─ ...                                         │ │
│  │  │  └─ Feature #11                                       │ │
│  │  │     └─ ...                                            │ │
│  │  └─ Epic #2                                              │ │
│  │     └─ ...                                               │ │
│  │                                                           │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │  REST API (v7.2-preview.3)                               │ │
│  │                                                           │ │
│  │  GET /_apis/wit/workitems/{id}                           │ │
│  │  PATCH /_apis/wit/workitems/{id}                         │ │
│  │  POST /_apis/wit/wiql (Work Item Query Language)         │ │
│  │                                                           │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

---

## 📊 Fluxo de um Apontamento (End-to-End)

```
1. USUÁRIO INTERAGE (React)
   ├─ Clica em "Adicionar Apontamento"
   ├─ Modal abre com formulário
   ├─ Busca "Implementar login" → chamada para API search
   ├─ Seleciona Task #1001
   ├─ Digita 2.5 horas
   ├─ Seleciona "Desenvolvimento"
   ├─ Clica "Salvar"
   └─ onSubmit() dispara POST request

2. FRONTEND (React Hook Form)
   ├─ Valida dados
   ├─ Constrói payload:
   │  {
   │    work_item_id: 1001,
   │    data_apontamento: "2026-01-18",
   │    duracao: "02:30",
   │    duracao_horas: 2.5,
   │    id_atividade: "dev-123",
   │    comentario: "Implementado form de login"
   │  }
   ├─ POST http://localhost:8000/api/v1/apontamentos
   └─ await response

3. BACKEND (FastAPI)
   ├─ Recebe request
   ├─ Valida schema
   ├─ Salva em banco local (INSERT into apontamentos)
   ├─ Obtém work item atual do Azure:
   │  ├─ CurrentCompletedWork: 10.0
   │  └─ CurrentRemainingWork: 10.0
   ├─ Calcula novos valores:
   │  ├─ NewCompletedWork = 10.0 + 2.5 = 12.5
   │  └─ NewRemainingWork = 10.0 - 2.5 = 7.5
   ├─ PATCH para Azure DevOps:
   │  {
   │    op: "add",
   │    path: "/fields/Microsoft.VSTS.Scheduling.CompletedWork",
   │    value: 12.5
   │  }
   ├─ Se falhar → adiciona à sync_queue para retry
   ├─ Retorna JSON com apontamento criado
   └─ response.status(201)

4. FRONTEND (React Query)
   ├─ Recebe resposta com sucesso
   ├─ Invalida cache de queries
   ├─ Refaz fetch de dados atualizado
   ├─ UI atualiza com novo apontamento
   ├─ Mostra toast "Apontamento salvo!"
   └─ Modal fecha, timesheet refresça

5. AZURE DEVOPS (Work Item)
   ├─ Task #1001 foi atualizada:
   │  ├─ CompletedWork: 10.0 → 12.5 ✅
   │  └─ RemainingWork: 10.0 → 7.5 ✅
   └─ Visível em dev.azure.com em tempo real

6. TIMESHEET EXIBE
   ├─ Linha da Task #1001 mostra 2.5h no dia 18/jan
   ├─ Total semanal incrementa
   ├─ Total da task atualiza de 10.0 → 12.5
   ├─ Parent story recalcula automaticamente
   └─ Parent epic recalcula recursivamente
```

---

## 🔄 Ciclo de Sincronização (Retry)

```
┌─ Apontamento salvo
│
├─ 1. SYNC IMEDIATO (on create)
│  ├─ GET work item do Azure
│  ├─ PATCH CompletedWork + RemainingWork
│  │  ├─ Sucesso → mark as synced
│  │  └─ Erro → add to sync_queue
│  └─ Return response
│
├─ 2. RETRY BACKGROUND (every 5 seconds)
│  ├─ SELECT * FROM sync_queue WHERE retry_at < NOW()
│  ├─ Para cada item:
│  │  ├─ Tenta PATCH novamente
│  │  ├─ Se sucesso:
│  │  │  ├─ DELETE from sync_queue
│  │  │  └─ UPDATE apontamentos.synced = true
│  │  └─ Se erro:
│  │     ├─ INCREMENT tentativas
│  │     ├─ Se tentativas < 5:
│  │     │  └─ SET proximo_retry = NOW() + exponential_backoff
│  │     └─ Se tentativas >= 5:
│  │        └─ Log error, notificar admin
│  └─ Continue
│
└─ 3. MANUAL SYNC (user triggers)
   ├─ GET lista de sync_queue pendentes
   ├─ Botão "Retry Sync"
   ├─ PATCH todos agora
   └─ Atualiza UI com resultado
```

---

## 🔐 Autenticação & Autorização

```
┌─────────────────────────────────────────┐
│ Frontend (sem secrets)                  │
│ - Nenhum token armazenado               │
│ - Nenhuma credencial                    │
│ - Requisições anônimas ou com headers   │
└──────────────┬──────────────────────────┘
               │
               │ HTTP Request
               │ (opcionalmente com Authorization header)
               │
               ▼
┌─────────────────────────────────────────┐
│ Backend (gerencia tudo)                 │
│ ├─ PAT do Azure DevOps em ENV           │
│ ├─ Database credentials em ENV          │
│ ├─ Validação de requests                │
│ └─ Rate limiting por IP                 │
└──────────────┬──────────────────────────┘
               │
               │ Autenticado com Azure
               │ using PAT token
               │
               ▼
┌─────────────────────────────────────────┐
│ Azure DevOps (API secured)              │
│ ├─ PAT token validado                   │
│ ├─ Permissões verificadas               │
│ └─ Response retornada                   │
└─────────────────────────────────────────┘
```

---

## 🔗 Componentes-Chave

### Frontend

| Componente | Localização | Responsabilidade |
|-----------|-----------|------------------|
| **PaginaPrincipal** | `pages/` | Exibe timesheet completo |
| **ModalAdicionarTempo** | `components/custom/` | Form para novo apontamento |
| **useApi** | `hooks/use-api.ts` | Chamadas CRUD via fetch |
| **useSearchWorkItems** | `hooks/use-search-work-items.ts` | Busca com debounce |
| **useAtividades** | `hooks/use-atividades.ts` | Lista de tipos de atividade |
| **useCurrentUser** | `hooks/use-current-user.ts` | Usuário logado |

### Backend

| Serviço | Responsabilidade |
|---------|------------------|
| **ApontamentoController/Router** | HTTP endpoints CRUD |
| **ApontamentoService** | Lógica de negócio |
| **AzureDevOpsService** | Integração Azure |
| **SyncService** | Sincronização + retry |
| **AtividadeService** | Gerenciar tipos de atividade |
| **Database Layer** | Persistência de dados |

---

## 📁 Arquivos Críticos

### Frontend (este projeto)

```
client/
├── src/
│   ├── App.tsx                    # App root com router
│   ├── hooks/
│   │   ├── use-api.ts ⭐ CRÍTICO (aponta :8000)
│   │   ├── use-atividades.ts
│   │   ├── use-current-user.ts
│   │   └── use-search-work-items.ts
│   ├── pages/
│   │   └── PaginaPrincipal.tsx    # Timesheet grid
│   ├── components/
│   │   ├── custom/ModalAdicionarTempo.tsx ⭐
│   │   └── ui/                     # shadcn/ui
│   └── lib/
│       └── api-client.ts           # Tipos TypeScript
├── index.html
└── vite.config.ts
```

### Backend (externo, localhost:8000)

```
backend/
├── main.py (ou app.py, server.ts, etc)
├── routers/
│   ├── apontamentos.py
│   ├── work_items.py
│   ├── atividades.py
│   └── user.py
├── services/
│   ├── apontamento_service.py
│   ├── azure_devops_service.py
│   ├── sync_service.py
│   └─ atividade_service.py
├── models/
│   ├── apontamento.py
│   ├── atividade.py
│   └── sync_queue.py
├── database.py
└── config.py (com PAT, CORS, etc)
```

---

## 🚀 Deployment

### Frontend
```
Build: npm run build → dist/
Deploy: Vercel / Netlify / AWS S3 + CloudFront
Config: VITE_API_URL=https://backend-prod.com/api/v1
```

### Backend
```
Deploy: Docker / Heroku / AWS EC2
Config: ENV vars (PAT, CORS_ORIGINS, etc)
Monitor: Logs, API metrics, sync failures
```

---

## 📊 Banco de Dados Local

### Tabelas Essenciais

#### apontamentos
```sql
id | work_item_id | project_id | data | duracao_horas | usuario_id | id_atividade | azure_sync_status
```

#### atividades
```sql
id | nome | descricao | ativo | id_projeto
```

#### sync_queue (para retry)
```sql
id | apontamento_id | tentativas | proximo_retry | erro_mensagem
```

---

## ✅ Checklist de Integração

- [ ] Backend implementou todos 11 endpoints
- [ ] CORS configurado (permite localhost:5000)
- [ ] Database criado com 3 tabelas
- [ ] Azure DevOps API integrada
- [ ] Sync automático funcionando
- [ ] Retry de falhas implementado
- [ ] Frontend `npm install` executado
- [ ] `.env.local` criado com URL backend
- [ ] `npm run dev` inicia em :5000
- [ ] Busca de tasks funciona
- [ ] CRUD de apontamentos funciona
- [ ] Sincronização visível em Azure DevOps
- [ ] Testes E2E passam
- [ ] Deploy pipeline configurado

---

**Versão**: 1.0  
**Data**: 18 de janeiro de 2026  
**Mantido por**: GitHub Copilot
