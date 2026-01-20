# ⚡ QUICK REFERENCE CARD

## Comece aqui! (escolha seu caminho)

### 🎯 Qual é seu rol

```
👨‍💻 Backend Dev?
   └─> Leia: BACKEND_MIGRATION_GUIDE.md (30 min)
   └─> Implemente: 11 endpoints em /api/v1
   └─> Teste: CRUD + Azure sync + retry

🎨 Frontend Dev?
   └─> Leia: MIGRATION_INSTRUCTIONS.md (10 min)
   └─> Execute: npm install && npm run dev
   └─> Aguarde: Backend estar 50% pronto

🏗️ Arquiteto?
   └─> Leia: ARCHITECTURE.md (15 min)
   └─> Entenda: Diagramas e fluxos
   └─> Valide: Design decisions

👔 Manager?
   └─> Leia: PRODUCT_SPECIFICATION.md (15 min)
   └─> Entenda: Features, roadmap, timeline
   └─> Coordene: Dev teams

🧪 QA?
   └─> Leia: VERIFICATION_CHECKLIST.md (10 min)
   └─> Crie: Plano de testes
   └─> Valide: Sincronização Azure

🔧 DevOps?
   └─> Leia: MIGRATION_INSTRUCTIONS.md + ARCHITECTURE.md
   └─> Setup: Pipelines de deploy
   └─> Monitor: Frontend + Backend
```

---

## 🔑 Palavras-chave

### Endpoints Backend (11 total)
```
POST   /api/v1/apontamentos
GET    /api/v1/apontamentos/{id}
PUT    /api/v1/apontamentos/{id}
DELETE /api/v1/apontamentos/{id}
GET    /api/v1/apontamentos/work-item/{id}
GET    /api/v1/apontamentos/work-item/{id}/resumo
GET    /api/v1/apontamentos/work-item/{id}/azure-info
GET    /api/v1/work-items/search
GET    /api/v1/user
GET    /api/v1/atividades
GET    /api/v1/atividades/{id}
```

### Frontend Tech Stack
```
React 19 + Vite + TanStack Query + shadcn/ui + Tailwind CSS
```

### Backend Tech Stack (choose one)
```
FastAPI / Django / Express.js / Nest.js
```

### Database Tables (3)
```
apontamentos → time entries
atividades   → activity types
sync_queue   → retry failures
```

### Azure DevOps Integration
```
- GET work item info
- PATCH CompletedWork
- PATCH RemainingWork
- WIQL search queries
```

---

## ⚙️ Setup Rápido (5 min)

### Frontend
```bash
npm install
echo "VITE_API_URL=http://localhost:8000/api/v1" > .env.local
npm run dev  # http://localhost:5000
```

### Backend
```bash
# Escolha: FastAPI / Django / Express
# Implemente: 11 endpoints conforme BACKEND_MIGRATION_GUIDE.md
# Configure: CORS para localhost:5000
# Rode em: http://localhost:8000
```

---

## 📊 Números Importantes

```
Endpoints:     11
Dependencies:  37 (era 62, -40%)
Documentos:    10
Tabelas DB:    3
Timeline:      4-6 semanas
Team Size:     3-5 developers
```

---

## 🚀 Roadmap (60 dias)

### Semanas 1-3: Backend
```
[ ] Endpoints implementados
[ ] Azure sync funcionando
[ ] Database setup
[ ] Testes unitários
```

### Semana 2-3: Integration
```
[ ] Frontend + Backend integrados
[ ] E2E tests
[ ] Sincronização validada
```

### Semana 4: Staging
```
[ ] Deploy em staging
[ ] Load testing
[ ] User acceptance testing
```

### Semana 5-6: Production
```
[ ] Deploy em produção
[ ] Monitoring ativo
[ ] Support ready
```

---

## 📖 Documentos (10 total)

| # | Nome | Tempo | Tipo |
|---|------|-------|------|
| 1 | SUMMARY.md | 10m | Overview |
| 2 | README_MIGRATION.md | 5m | Summary |
| 3 | DOCUMENTATION_INDEX.md | 5m | Index |
| 4 | QUICK_REFERENCE.md | 2m | Este arquivo |
| 5 | PRODUCT_SPECIFICATION.md | 15m | Spec |
| 6 | BACKEND_MIGRATION_GUIDE.md | 30m | Spec técnica |
| 7 | ARCHITECTURE.md | 15m | Design |
| 8 | MIGRATION_INSTRUCTIONS.md | 10m | How-to |
| 9 | VERIFICATION_CHECKLIST.md | 10m | Checklist |
| 10 | MIGRATION_COMPLETE.md | 10m | Status |

---

## ✅ Checklist Crítico

- [x] Frontend atualizado (aponta :8000)
- [x] Package.json limpo
- [x] Documentação completa
- [ ] Backend implementado (próx.)
- [ ] Testes E2E (próx.)
- [ ] Deploy produção (próx.)

---

## 🆘 Ajuda Rápida

### Erro: "Cannot connect to :8000"
```
Backend não está rodando
→ Certifique que localhost:8000 está ativo
```

### Erro: "CORS blocked"
```
Backend sem CORS configurado
→ Adicionar: CORS_ORIGINS=http://localhost:5000
```

### Erro: "API 404"
```
Endpoint não implementado no backend
→ Verificar BACKEND_MIGRATION_GUIDE.md
```

---

## 🎯 Success Criteria

✅ Frontend roda em :5000
✅ Backend roda em :8000
✅ CRUD de apontamentos funciona
✅ Sincronização com Azure funciona
✅ Retry automático funciona
✅ Testes E2E passam
✅ Deploy em produção OK

---

## 📞 Próximo Passo

1. **Backend Team**
   - Leia: BACKEND_MIGRATION_GUIDE.md
   - Implemente: Primeiro endpoint

2. **Frontend Team**
   - Leia: MIGRATION_INSTRUCTIONS.md
   - Execute: npm install

3. **QA Team**
   - Leia: VERIFICATION_CHECKLIST.md
   - Crie: Plano de testes

4. **DevOps Team**
   - Setup: CI/CD pipelines
   - Monitor: Health checks

---

**Status**: ✅ PRONTO  
**Data**: 18 de janeiro de 2026  
**Versão**: 1.0

---

## 📚 Índice Completo

```
QUICK_REFERENCE.md (você está aqui)
├─ Comece aqui!
├─ Palavras-chave
├─ Setup rápido
├─ Números
├─ Roadmap
├─ Documentos
├─ Checklist
└─ Ajuda rápida

DOCUMENTATION_INDEX.md
├─ Índice de documentação
├─ Mapa de documentação
├─ Leitura recomendada
├─ Checklist de leitura
├─ Busca rápida
└─ Estatísticas

Documentação Técnica
├─ PRODUCT_SPECIFICATION.md (features, roadmap)
├─ BACKEND_MIGRATION_GUIDE.md (11 endpoints)
├─ ARCHITECTURE.md (diagramas, componentes)
├─ MIGRATION_INSTRUCTIONS.md (setup)
└─ VERIFICATION_CHECKLIST.md (validação)

Sumários
├─ SUMMARY.md (conclusão final)
├─ README_MIGRATION.md (overview)
├─ MIGRATION_COMPLETE.md (o que foi feito)
└─ FRONTEND_ONLY.md (status atual)
```

---

🚀 **Vamos começar!**
