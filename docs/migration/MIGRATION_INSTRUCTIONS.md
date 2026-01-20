# 🔄 MIGRATION INSTRUCTIONS: Frontend Only Mode

## Overview

Este guia descreve como converter o projeto **fe-aponta** de um projeto full-stack para **frontend-only**, removendo toda dependência do Express backend local.

---

## ✅ Checklist de Migração

### 1. Backend Externo (localhost:8000)

**Status**: ❌ Fora do escopo deste projeto
- O backend FastAPI em localhost:8000 deve implementar todos os endpoints descritos em `BACKEND_MIGRATION_GUIDE.md`
- Coordenar com o time que mantém localhost:8000

---

### 2. Frontend (este projeto)

#### Passo 1: Atualizar Configuração de API

**Arquivo**: `client/src/lib/api-client.ts`

Mudança:
```typescript
// ANTES (aponta para backend local Express)
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:3000";

// DEPOIS (aponta para backend externo FastAPI)
const API_BASE_URL = process.env.VITE_API_URL || "http://localhost:8000/api/v1";
```

#### Passo 2: Criar `.env.local` para Development

```env
# API Configuration
VITE_API_URL=http://localhost:8000/api/v1

# Azure DevOps (se necessário no frontend)
VITE_AZURE_ORG_URL=https://dev.azure.com/sefaz-ceara-lab
```

#### Passo 3: Atualizar Scripts npm

**Arquivo**: `package.json`

Remover:
```json
"dev": "cross-env NODE_ENV=development tsx server/index.ts",
"build": "tsx script/build.ts",
"start": "cross-env NODE_ENV=production node dist/index.cjs",
"db:push": "drizzle-kit push",
"test:azure": "cross-env NODE_ENV=development tsx server/test-azure-connection.ts",
```

Novos scripts:
```json
"dev": "vite dev --port 5000",
"build": "vite build",
"preview": "vite preview",
"lint": "tsc --noEmit"
```

#### Passo 4: Remover Dependências Backend

Remover do `package.json`:
```json
// devDependencies
"@types/express": "4.17.21",
"@types/express-session": "^1.18.0",
"@types/passport": "^1.0.16",
"@types/passport-local": "^1.0.38",
"@types/ws": "^8.5.13",
"drizzle-kit": "^0.31.4",
"tsx": "^4.20.5",
"@types/connect-pg-simple": "^7.0.3",

// dependencies
"azure-devops-node-api": "^13.0.0",
"connect-pg-simple": "^10.0.0",
"drizzle-orm": "^0.39.3",
"drizzle-zod": "^0.7.0",
"express": "^4.21.2",
"express-session": "^1.18.1",
"memorystore": "^1.6.7",
"passport": "^0.7.0",
"passport-local": "^1.0.0",
"pg": "^8.16.3",
"ws": "^8.18.0",
```

#### Passo 5: Deletar Diretórios Backend

```bash
rm -r server/
rm -r script/
```

#### Passo 6: Atualizar package.json

```bash
npm install  # Reinstalar com dependências limpas
npm run build  # Testar build
```

#### Passo 7: Testar Frontend

```bash
# Certificar que localhost:8000 está rodando

npm run dev
# Navegar para http://localhost:5000
# Testar fluxo completo:
# - Buscar tasks
# - Adicionar apontamento
# - Verificar sincronização
```

---

## 📝 Mudanças nos Arquivos Frontend

### `client/src/lib/api-client.ts`

**ANTES:**
```typescript
function getApiConfig() {
  const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:3000";
  const API_TOKEN = process.env.API_TOKEN || process.env.AZURE_DEVOPS_PAT || "";
  return { BACKEND_URL, API_TOKEN };
}
```

**DEPOIS:**
```typescript
function getApiConfig() {
  const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";
  return { API_BASE_URL };
}
```

---

### Hooks React - Sem Mudanças Necessárias

Os hooks em `client/src/hooks/` chamam `api-client.ts`, então funcionarão automaticamente:
- ✅ `use-api.ts`
- ✅ `use-atividades.ts`
- ✅ `use-current-user.ts`
- ✅ `use-search-work-items.ts`

---

## 🚀 Passo a Passo para Executar

### Pré-requisitos

1. **Backend localhost:8000 rodando** ✅
   ```bash
   # No projeto backend (não este)
   python main.py  # ou equivalent
   ```

2. **Node.js 18+ instalado** ✅

### Iniciar Frontend

```bash
# 1. Clonar/atualizar este projeto
cd fe-aponta

# 2. Instalar dependências (com deps backend removidas)
npm install

# 3. Criar .env.local
cat > .env.local << EOF
VITE_API_URL=http://localhost:8000/api/v1
EOF

# 4. Iniciar dev server
npm run dev

# 5. Abrir browser
# http://localhost:5000
```

---

## 🔍 Verificação Pós-Migração

### Checklist de Testes

- [ ] `npm install` completa sem erros
- [ ] `npm run dev` inicia server em porta 5000
- [ ] Frontend carrega em http://localhost:5000
- [ ] Rota `/` renderiza PaginaPrincipal
- [ ] Botão "Adicionar Apontamento" abre modal
- [ ] Search de tasks funciona (autocomplete)
- [ ] Criação de apontamento salva em localhost:8000
- [ ] Atualização/exclusão funciona
- [ ] Console não mostra erros CORS
- [ ] `npm run build` compila sem erros

### Troubleshooting

**Erro: "Cannot find module 'express'"**
- Solução: Deletar `node_modules/` e `package-lock.json`, rodar `npm install`

**Erro: CORS blocked**
- Verificar se localhost:8000 tem CORS configurado para localhost:5000
- Adicionar em backend: `CORS_ORIGINS=http://localhost:5000`

**Erro: "Cannot GET /"**
- Vite não está servindo o frontend
- Verificar se `npm run dev` está rodando corretamente

**API 404 errors**
- Backend localhost:8000 não está rodando
- Verificar se endpoints estão implementados
- Revisar `BACKEND_MIGRATION_GUIDE.md`

---

## 📁 Estrutura Final do Projeto

```
fe-aponta/
├── client/                    # ✅ Mantém
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── lib/
│   │   │   └── api-client.ts  # 📝 Modificado
│   │   ├── App.tsx
│   │   └── main.tsx
│   └── index.html
├── .env.local                 # 📝 Novo (local only)
├── .env                       # ❌ Não use em production
├── vite.config.ts            # ✅ Sem mudanças
├── package.json              # 📝 Modificado
├── PRODUCT_SPECIFICATION.md  # ✅ Novo
├── BACKEND_MIGRATION_GUIDE.md # ✅ Novo
├── MIGRATION_INSTRUCTIONS.md # ✅ Este arquivo
└── README.md                 # 📝 Atualizar
```

**Deletado:**
```
❌ server/                    # Todo o backend Express
❌ script/                    # Scripts de build backend
❌ drizzle.config.ts         # Configuração DB
❌ server files (routes, api-client backend, etc)
```

---

## 🔐 Segurança & Dados Sensíveis

### ❌ O que NÃO fazer

```env
# NUNCA commitar .env com secrets
AZURE_DEVOPS_PAT=<NUNCA_COMMITAR_SECRETS>
```

### ✅ O que fazer

1. **Backend** (localhost:8000) gerencia PAT e credentials
2. **Frontend** (este projeto) só faz requisições anônimas ou com token do backend
3. `.env` com secrets fica no `.gitignore`

---

## 📚 Documentação Relacionada

- [PRODUCT_SPECIFICATION.md](./PRODUCT_SPECIFICATION.md) — Visão geral do produto
- [BACKEND_MIGRATION_GUIDE.md](./BACKEND_MIGRATION_GUIDE.md) — O que backend precisa implementar

---

## 🤝 Próximos Passos

1. **Implementar Backend** (localhost:8000)
   - Seguir [BACKEND_MIGRATION_GUIDE.md](./BACKEND_MIGRATION_GUIDE.md)
   - Testes de cada endpoint
   - Deploy em staging

2. **Testar Integração** (fe-aponta + backend)
   - E2E tests
   - User acceptance testing
   - Performance tests

3. **Deploy em Produção**
   - Build frontend: `npm run build`
   - Upload para CDN ou servidor estático
   - Configure backend API URL em produção

---

**Versão**: 1.0
**Data**: 18 de janeiro de 2026
**Status**: Pronto para execução
