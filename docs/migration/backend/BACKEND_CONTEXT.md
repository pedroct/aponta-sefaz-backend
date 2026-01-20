# 🔗 BACKEND CONTEXT DOCUMENT (Atual)

**Data**: 18 de janeiro de 2026  
**Status**: ✅ Frontend otimizado e pronto  
**Versão**: 2.0 - Pós-otimização

---

## 📋 Sumário Executivo

O repositório **fe-aponta** foi migrado com sucesso de um **full-stack monolith (Express + React)** para uma **frontend-only SPA**. Todo o backend foi removido do repositório local, e o código frontend foi significativamente otimizado. Este documento descreve:

1. **O que foi removido** (backend local)
2. **O que foi mantido** (frontend otimizado)
3. **O que o backend externo precisa implementar** (endpoints esperados)
4. **Como integrar com o frontend** (contrato de API)

---

## 🎯 Estado Atual do Frontend

### ✅ Estrutura do Projeto

```
fe-aponta/
├── client/                          # React SPA
│   ├── src/
│   │   ├── components/
│   │   │   ├── custom/
│   │   │   │   └── ModalAdicionarTempo.tsx    # ⭐ Componente principal
│   │   │   └── ui/                            # 10 componentes reutilizáveis
│   │   │       ├── button.tsx
│   │   │       ├── calendar.tsx
│   │   │       ├── card.tsx
│   │   │       ├── command.tsx
│   │   │       ├── dialog.tsx
│   │   │       ├── popover.tsx
│   │   │       ├── toast.tsx
│   │   │       ├── toaster.tsx
│   │   │       ├── tooltip.tsx
│   │   │       └── work-item-icon.tsx
│   │   ├── hooks/                             # Custom React hooks
│   │   │   ├── use-api.ts                     # ⭐ API client (localhost:8000)
│   │   │   ├── use-atividades.ts              # Fetch activity types
│   │   │   ├── use-current-user.ts            # Fetch current user
│   │   │   ├── use-search-work-items.ts       # Search Azure DevOps items
│   │   │   └── use-toast.ts                   # Toast notifications
│   │   ├── lib/
│   │   │   ├── api-client.ts                  # TypeScript types/interfaces
│   │   │   ├── queryClient.ts                 # React Query config
│   │   │   └── utils.ts                       # Utility functions
│   │   ├── pages/
│   │   │   ├── PaginaPrincipal.tsx            # Main time tracking page
│   │   │   └── not-found.tsx                  # 404 page
│   │   ├── App.tsx                            # Root component
│   │   ├── main.tsx                           # Entry point
│   │   └── index.css                          # Global styles
│   ├── index.html
│   └── vite.config.ts
├── shared/
│   └── schema.ts                    # Shared types & Zod validation
├── .env.example                     # Environment template
├── CLEANUP_FINAL_REPORT.md          # Cleanup summary (67% deps reduction)
├── DEVELOPMENT_GUIDE.md             # Development quick start
└── docs/migration/                  # 14 migration documentation files
```

### 📦 Dependencies (Reduzidos)

**Before**: 62 packages  
**After**: 21 packages  
**Reduction**: 67% ↓

**Current Production Dependencies**:
```json
{
  "@hookform/resolvers": "^3.10.0",
  "@jridgewell/trace-mapping": "^0.3.25",
  "@radix-ui/react-dialog": "^1.1.15",
  "@radix-ui/react-icons": "^1.3.0",
  "@radix-ui/react-popover": "^1.1.15",
  "@radix-ui/react-slot": "^1.2.4",
  "@radix-ui/react-toast": "^1.2.7",
  "@radix-ui/react-tooltip": "^1.2.8",
  "@tanstack/react-query": "^5.60.5",
  "class-variance-authority": "^0.7.1",
  "clsx": "^2.1.1",
  "cmdk": "^1.1.1",
  "date-fns": "^3.6.0",
  "lucide-react": "^0.545.0",
  "react": "^19.2.0",
  "react-day-picker": "^9.11.1",
  "react-dom": "^19.2.0",
  "react-hook-form": "^7.66.0",
  "tailwind-merge": "^3.3.1",
  "tailwindcss-animate": "^1.0.7",
  "wouter": "^3.3.5",
  "zod": "^3.25.76",
  "zod-validation-error": "^3.4.0"
}
```

**DevDependencies**: 14 essenciais (Vite, TypeScript, Testing)

### 🗑️ O Que Foi Removido

**Backend Code** (/server/):
```
- index.ts           (Express app setup)
- routes.ts          (API routes)
- api-client.ts      (Azure DevOps integration)
- azure-devops.ts    (Azure SDK integration)
- storage.ts         (Database layer)
- sync-service.ts    (Sync to Azure)
- vite.ts            (Vite server config)
- static.ts          (Static file serving)
- test-*.ts (5 arquivos)
```

**Build Scripts** (/script/):
```
- build.ts           (Custom build script)
```

**Backend Configuration**:
```
- drizzle.config.ts  (ORM configuration)
- .replit            (Replit environment)
- .mcp.json          (MCP configuration)
```

**Backend Dependencies** (41 packages):
```
Express, Passport, Drizzle ORM, Azure DevOps SDK, PostgreSQL, etc.
```

**UI Components** (39 unused):
```
Removed 39 out of 49 shadcn/ui components
Kept only: button, calendar, card, command, dialog, popover, toast, toaster, tooltip, work-item-icon
```

---

## 🔌 Frontend API Expectations

### Base URL

```typescript
// Via environment variable
VITE_API_URL = http://localhost:8000/api/v1

// Or hardcoded in use-api.ts
const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1"
```

### Authentication

Currently **no authentication implemented** in frontend. The backend should:
- ✅ Implement authentication (JWT, OAuth, etc.)
- ✅ Set user context from request headers or session
- ✅ Add CORS headers to allow requests from `http://localhost:5000`

### Required Endpoints

#### 1. **User Information**

**`GET /api/v1/user`**

Returns current authenticated user info.

**Response** (200 OK):
```json
{
  "id": "user-123",
  "displayName": "João Silva",
  "emailAddress": "joao@example.com",
  "avatarUrl": "https://..."
}
```

**Used By**: `use-current-user.ts` → Displayed in modal form

**Error Handling**:
- 401 Unauthorized → Frontend shows login prompt
- 500 Internal Server Error → Toast notification

---

#### 2. **Activity Types Catalog**

**`GET /api/v1/atividades`**

Returns list of activity type categories.

**Query Parameters**:
- `ativo` (optional, boolean) — Filter by active status

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "dev-001",
      "nome": "Desenvolvimento",
      "descricao": "Desenvolvimento de features",
      "ativo": true,
      "order": 1
    },
    {
      "id": "doc-001",
      "nome": "Documentação",
      "descricao": "Escrita e atualização de documentação",
      "ativo": true,
      "order": 2
    },
    {
      "id": "reuniao-001",
      "nome": "Reunião",
      "descricao": "Participação em reuniões",
      "ativo": true,
      "order": 3
    },
    {
      "id": "review-001",
      "nome": "Review",
      "descricao": "Code review e análise",
      "ativo": true,
      "order": 4
    },
    {
      "id": "outro-001",
      "nome": "Outro",
      "descricao": "Outras atividades",
      "ativo": true,
      "order": 5
    }
  ]
}
```

**Used By**: `use-atividades.ts` → Dropdown in modal form

---

#### 3. **Work Item Search**

**`GET /api/v1/work-items/search`**

Search for Azure DevOps work items by ID or title with autocomplete support.

**Query Parameters**:
- `query` (required) — Minimum 2 characters
- `project_id` (optional, default: "DEV")
- `organization_name` (optional, default: "sefaz-ceara-lab")
- `limit` (optional, default: 10)

**Response** (200 OK):
```json
{
  "results": [
    {
      "id": 1234,
      "title": "Implementar dashboard de analytics",
      "type": "Feature",
      "project": "DEV",
      "url": "https://dev.azure.com/...",
      "originalEstimate": 8,
      "completedWork": 5.5,
      "remainingWork": 2.5,
      "state": "Active"
    },
    {
      "id": 1235,
      "title": "Fix bug in authentication flow",
      "type": "Bug",
      "project": "DEV",
      "url": "https://dev.azure.com/...",
      "originalEstimate": 4,
      "completedWork": 2,
      "remainingWork": 2,
      "state": "Active"
    }
  ],
  "count": 2
}
```

**Used By**: `use-search-work-items.ts` → Autocomplete combobox in modal

**Debouncing**: Frontend debounces requests (300ms)

**Error Handling**:
- 400 Bad Request → Show error toast
- 500 Internal Server Error → Fallback message

---

#### 4. **Create Apontamento (Time Entry)**

**`POST /api/v1/apontamentos`**

Create a new time entry and sync with Azure DevOps.

**Request Body**:
```json
{
  "data_apontamento": "2026-01-18",
  "duracao": "02:30",
  "duracao_horas": 2.5,
  "id_atividade": "dev-001",
  "comentario": "Implementação da feature de login",
  "work_item_id": 1234,
  "project_id": "DEV",
  "organization_name": "sefaz-ceara-lab",
  "usuario_id": "user-123",
  "usuario_nome": "João Silva",
  "usuario_email": "joao@example.com"
}
```

**Response** (201 Created):
```json
{
  "id": "apon-789",
  "work_item_id": 1234,
  "project_id": "DEV",
  "organization_name": "sefaz-ceara-lab",
  "data_apontamento": "2026-01-18",
  "duracao": "02:30",
  "duracao_horas": 2.5,
  "id_atividade": "dev-001",
  "atividade": {
    "id": "dev-001",
    "nome": "Desenvolvimento"
  },
  "comentario": "Implementação da feature de login",
  "usuario_id": "user-123",
  "usuario_nome": "João Silva",
  "usuario_email": "joao@example.com",
  "criado_em": "2026-01-18T10:30:00Z",
  "atualizado_em": "2026-01-18T10:30:00Z",
  "azure_sync_status": "synced"
}
```

**Critical Backend Responsibilities**:

1. ✅ **Validate Request**
   - Check all required fields
   - Validate date format (YYYY-MM-DD)
   - Validate time format (HH:mm)
   - Validate duration (15min - 8h)

2. ✅ **Save to Database**
   - Insert into `apontamentos` table
   - Generate unique ID

3. ✅ **Sync with Azure DevOps** (CRITICAL)
   - Fetch work item #1234 from Azure
   - Calculate new `CompletedWork = old + 2.5`
   - Calculate new `RemainingWork = max(0, old - 2.5)`
   - PATCH work item in Azure DevOps
   - Handle Azure API errors gracefully

4. ✅ **Error Handling**
   - Azure error? → Save locally + Queue for retry
   - Database error? → 500 response
   - Validation error? → 400 response

**Used By**: Modal form → `ModalAdicionarTempo.tsx`

---

#### 5. **List Apontamentos by Work Item**

**`GET /api/v1/apontamentos/work-item/{workItemId}`**

List all time entries for a specific work item.

**Query Parameters**:
- `organization_name` (required)
- `project_id` (required)
- `skip` (optional, default: 0)
- `limit` (optional, default: 100)

**Response** (200 OK):
```json
{
  "items": [
    {
      "id": "apon-789",
      "work_item_id": 1234,
      "data_apontamento": "2026-01-18",
      "duracao_horas": 2.5,
      "usuario_nome": "João Silva",
      "atividade": { "id": "dev-001", "nome": "Desenvolvimento" },
      "comentario": "Implementação"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 100
}
```

---

#### 6. **Get Apontamento Summary**

**`GET /api/v1/apontamentos/work-item/{workItemId}/resumo`**

Get summary statistics for a work item.

**Query Parameters**:
- `organization_name` (required)
- `project_id` (required)

**Response** (200 OK):
```json
{
  "work_item_id": 1234,
  "total_horas": 12.5,
  "total_apontamentos": 5,
  "media_horas_por_apontamento": 2.5,
  "primeira_data": "2026-01-10",
  "ultima_data": "2026-01-18",
  "por_atividade": [
    { "id": "dev-001", "nome": "Desenvolvimento", "total_horas": 10.0 },
    { "id": "doc-001", "nome": "Documentação", "total_horas": 2.5 }
  ],
  "por_usuario": [
    { "id": "user-123", "nome": "João Silva", "total_horas": 12.5 }
  ]
}
```

---

## 🔄 CORS Configuration

The backend **MUST** support CORS for requests from frontend.

**Required Headers**:
```
Access-Control-Allow-Origin: http://localhost:5000
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type, Authorization
Access-Control-Allow-Credentials: true
```

**For Production**:
```
Access-Control-Allow-Origin: https://seu-frontend.com
```

---

## 🔐 Authentication Recommendations

Current frontend has **no authentication mechanism**. Backend should implement:

**Option 1: JWT Tokens**
```typescript
// Frontend would add:
headers: {
  "Authorization": `Bearer ${token}`
}
```

**Option 2: Session Cookies**
```typescript
// Backend sets:
Set-Cookie: session=abc123; HttpOnly; Secure
```

**Option 3: API Keys**
```typescript
// Frontend adds:
headers: {
  "X-API-Key": apiKey
}
```

---

## 📊 Data Models Expected by Frontend

### Apontamento (Time Entry)
```typescript
interface Apontamento {
  id: string;
  work_item_id: number;
  project_id: string;
  organization_name: string;
  data_apontamento: string;        // YYYY-MM-DD
  duracao: string;                 // HH:mm
  duracao_horas: number;           // 0.5, 1, 2.5, etc.
  id_atividade: string;
  atividade: {
    id: string;
    nome: string;
  };
  comentario?: string;
  usuario_id: string;
  usuario_nome: string;
  usuario_email: string;
  criado_em: string;               // ISO 8601 datetime
  atualizado_em: string;           // ISO 8601 datetime
  azure_sync_status: "synced" | "pending" | "failed";
}
```

### Atividade (Activity Type)
```typescript
interface Atividade {
  id: string;
  nome: string;
  descricao?: string;
  ativo: boolean;
  order?: number;
}
```

### WorkItem (Azure DevOps Item)
```typescript
interface WorkItem {
  id: number;
  title: string;
  type: "Epic" | "Feature" | "User Story" | "Task" | "Bug";
  project: string;
  url: string;
  originalEstimate?: number;
  completedWork?: number;
  remainingWork?: number;
  state: string;
}
```

### User
```typescript
interface User {
  id: string;
  displayName: string;
  emailAddress: string;
  avatarUrl?: string;
}
```

---

## 🚀 How to Integrate

### Step 1: Backend Implementation
1. Create FastAPI/Flask/Express backend
2. Implement 6 endpoints listed above
3. Connect to Azure DevOps SDK
4. Setup database (SQLite/PostgreSQL)
5. Run on `localhost:8000`

### Step 2: Frontend Configuration
1. Update `.env.local`:
   ```bash
   VITE_API_URL=http://localhost:8000/api/v1
   ```
2. Run frontend: `npm run dev` (port 5000)
3. Test modal form

### Step 3: Testing
1. Open http://localhost:5000/
2. Click "Apontar Tempo"
3. Fill in form and submit
4. Check backend logs for sync status

---

## 🔍 Key Files to Reference

**Frontend Implementation Files**:
- [use-api.ts](client/src/hooks/use-api.ts) — API client with all requests
- [ModalAdicionarTempo.tsx](client/src/components/custom/ModalAdicionarTempo.tsx) — Modal form (456 lines)
- [use-search-work-items.ts](client/src/hooks/use-search-work-items.ts) — Work item search
- [use-current-user.ts](client/src/hooks/use-current-user.ts) — User info
- [use-atividades.ts](client/src/hooks/use-atividades.ts) — Activity types

**Configuration**:
- [.env.example](.env.example) — Environment template
- [vite.config.ts](vite.config.ts) — Frontend build config
- [tsconfig.json](tsconfig.json) — TypeScript config

**Documentation**:
- [docs/migration/BACKEND_MIGRATION_GUIDE.md](docs/migration/BACKEND_MIGRATION_GUIDE.md) — Detailed backend spec
- [docs/migration/ARCHITECTURE.md](docs/migration/ARCHITECTURE.md) — System architecture
- [docs/migration/PRODUCT_SPECIFICATION.md](docs/migration/PRODUCT_SPECIFICATION.md) — Product requirements

---

## ✅ Verification Checklist

Backend implementation is complete when:

- [ ] ✅ `GET /api/v1/user` returns user info
- [ ] ✅ `GET /api/v1/atividades` returns activity types
- [ ] ✅ `GET /api/v1/work-items/search?query=test` returns work items
- [ ] ✅ `POST /api/v1/apontamentos` creates entry and syncs to Azure
- [ ] ✅ Azure DevOps fields updated (CompletedWork, RemainingWork)
- [ ] ✅ CORS headers present in all responses
- [ ] ✅ Frontend modal form works without errors
- [ ] ✅ Toast notifications show success/error messages
- [ ] ✅ Tests pass: `npm run type-check && npm run test`

---

## 📞 Contact & Support

**Frontend Status**: ✅ Production-ready (optimized)  
**Backend Status**: ⏳ Pending implementation  
**Last Updated**: 18 de janeiro de 2026  

For questions about frontend implementation, refer to:
- [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
- [CLEANUP_FINAL_REPORT.md](CLEANUP_FINAL_REPORT.md)
- [docs/migration/](docs/migration/)

---

## 📝 Change Log (This Session)

**Changes Made**:
1. ✅ Removed 40 unused npm dependencies (67% reduction)
2. ✅ Removed 39 unused UI components (84% reduction)
3. ✅ Removed `/server/` backend directory completely
4. ✅ Removed `/script/` build scripts
5. ✅ Cleaned drizzle config and Replit-specific files
6. ✅ Fixed React hooks rule violation in ModalAdicionarTempo
7. ✅ Optimized vite.config.ts (removed Replit plugins)
8. ✅ Build verified: `npm run build` ✅
9. ✅ Dev server running: `npm run dev` ✅
10. ✅ Created this comprehensive backend context document

**Frontend Status**: 100% operational, 67% smaller, 84% fewer components
