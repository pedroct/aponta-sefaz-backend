# 🔗 BACKEND INTEGRATION CHECKLIST

**Frontend Status**: ✅ Pronto (21 deps, 10 componentes, build otimizado)  
**Backend Status**: ⏳ Aguardando implementação  
**Integration Status**: ⏸️ Pausado (aguardando backend)

---

## 📋 Pré-Requisitos Backend

### Tecnologia Recomendada

Escolha uma das seguintes stacks:

#### Option 1: Python (Recomendado)
```
- FastAPI 0.100+
- SQLAlchemy 2.0+ (ORM)
- Pydantic v2 (Validation)
- azure-devops-python-api
- psycopg2 (PostgreSQL driver)
- Python 3.10+
```

#### Option 2: Node.js/Express
```
- Express 4.18+
- TypeScript 5.0+
- Prisma (ORM)
- Zod (Validation)
- azure-devops-node-api
- pg (PostgreSQL driver)
- Node.js 18+
```

#### Option 3: Go
```
- Gin or Echo framework
- GORM (ORM)
- azure-devops-go-api
- pgx (PostgreSQL driver)
- Go 1.20+
```

---

## 🔧 Backend Implementation Phases

### Phase 1: Project Setup (1 dia)

- [ ] Criar novo repositório backend
- [ ] Setup projeto com framework escolhido
- [ ] Configurar variáveis de ambiente
- [ ] Setup banco de dados (SQLite para dev, PostgreSQL para prod)
- [ ] Setup Git com .gitignore apropriado
- [ ] Setup CI/CD pipeline básico

**Entregável**: Projeto com estrutura básica rodando em `localhost:8000`

---

### Phase 2: Database Schema (2-3 dias)

#### Tabelas Necessárias

**1. apontamentos** (time entries)
```sql
CREATE TABLE apontamentos (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  work_item_id INTEGER NOT NULL,
  project_id VARCHAR(50) NOT NULL,
  organization_name VARCHAR(100) NOT NULL,
  data_apontamento DATE NOT NULL,
  duracao TIME NOT NULL,
  duracao_horas DECIMAL(5,2) NOT NULL,
  id_atividade VARCHAR(50) NOT NULL,
  comentario TEXT,
  usuario_id VARCHAR(100) NOT NULL,
  usuario_nome VARCHAR(200) NOT NULL,
  usuario_email VARCHAR(200),
  azure_sync_status VARCHAR(20) DEFAULT 'pending',
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(work_item_id, data_apontamento, usuario_id)
);

CREATE INDEX idx_apontamentos_work_item ON apontamentos(work_item_id);
CREATE INDEX idx_apontamentos_usuario ON apontamentos(usuario_id);
CREATE INDEX idx_apontamentos_data ON apontamentos(data_apontamento);
CREATE INDEX idx_apontamentos_sync_status ON apontamentos(azure_sync_status);
```

**2. atividades** (activity types)
```sql
CREATE TABLE atividades (
  id VARCHAR(50) PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  descricao TEXT,
  ativo BOOLEAN DEFAULT true,
  order INTEGER,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO atividades (id, nome, descricao, order) VALUES
  ('dev-001', 'Desenvolvimento', 'Desenvolvimento de features', 1),
  ('doc-001', 'Documentação', 'Escrita e atualização de documentação', 2),
  ('reuniao-001', 'Reunião', 'Participação em reuniões', 3),
  ('review-001', 'Review', 'Code review e análise', 4),
  ('outro-001', 'Outro', 'Outras atividades', 5);
```

**3. sync_queue** (para retry de Azure syncs)
```sql
CREATE TABLE sync_queue (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  apontamento_id UUID NOT NULL REFERENCES apontamentos(id),
  operation VARCHAR(20), -- 'create', 'update', 'delete'
  tentativas INTEGER DEFAULT 0,
  max_tentativas INTEGER DEFAULT 3,
  proximo_retry TIMESTAMP,
  erro_mensagem TEXT,
  criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sync_queue_status ON sync_queue(proximo_retry);
```

- [ ] Schema criado em banco de dados
- [ ] Migrations configuradas (Alembic para Python, Flyway para Java, etc.)
- [ ] Seed data inserido (atividades, etc.)
- [ ] Backups configurados
- [ ] Testes de conexão passando

**Entregável**: Schema pronto com dados iniciais

---

### Phase 3: API Endpoints (3-5 dias)

#### 3.1 User Endpoint

- [ ] Implementar `GET /api/v1/user`
  - [ ] Retornar user autenticado
  - [ ] Incluir id, displayName, emailAddress
  - [ ] Gerenciar autenticação (JWT/Session/API Key)

**Test**:
```bash
curl -X GET http://localhost:8000/api/v1/user \
  -H "Authorization: Bearer {token}"
```

#### 3.2 Activity Types Endpoint

- [ ] Implementar `GET /api/v1/atividades`
  - [ ] Retornar todas as atividades
  - [ ] Filtrar por `ativo` parameter
  - [ ] Ordenar por `order` field
  - [ ] Cache resultados (mudança rara)

**Test**:
```bash
curl http://localhost:8000/api/v1/atividades
```

#### 3.3 Work Items Search Endpoint

- [ ] Implementar `GET /api/v1/work-items/search`
  - [ ] Conectar Azure DevOps API
  - [ ] Implementar WIQL query
  - [ ] Buscar por ID ou título
  - [ ] Paginação
  - [ ] Cache com React Query

**Test**:
```bash
curl "http://localhost:8000/api/v1/work-items/search?query=dashboard&limit=10"
```

#### 3.4 Create Apontamento Endpoint (CRÍTICO)

- [ ] Implementar `POST /api/v1/apontamentos`
  - [ ] Validar request body
  - [ ] Salvar em banco de dados
  - [ ] **Sincronizar com Azure DevOps**:
    - [ ] Buscar work item em Azure
    - [ ] Atualizar `CompletedWork += duracao_horas`
    - [ ] Atualizar `RemainingWork = max(0, RemainingWork - duracao_horas)`
    - [ ] PATCH work item em Azure
  - [ ] Gerenciar erros de Azure sync
  - [ ] Retornar dados salvos

**Test**:
```bash
curl -X POST http://localhost:8000/api/v1/apontamentos \
  -H "Content-Type: application/json" \
  -d '{
    "data_apontamento": "2026-01-18",
    "duracao": "02:30",
    "duracao_horas": 2.5,
    "id_atividade": "dev-001",
    "comentario": "Teste",
    "work_item_id": 1234,
    "project_id": "DEV",
    "organization_name": "sefaz-ceara-lab",
    "usuario_id": "user-123",
    "usuario_nome": "Test User",
    "usuario_email": "test@example.com"
  }'
```

#### 3.5 List/Get Apontamentos Endpoints

- [ ] Implementar `GET /api/v1/apontamentos/{id}`
  - [ ] Retornar um apontamento específico
  
- [ ] Implementar `GET /api/v1/apontamentos/work-item/{id}`
  - [ ] Listar apontamentos de um work item
  - [ ] Paginação
  
- [ ] Implementar `GET /api/v1/apontamentos/work-item/{id}/resumo`
  - [ ] Retornar estatísticas agregadas
  - [ ] Total de horas
  - [ ] Por atividade
  - [ ] Por usuário

**Test**:
```bash
curl "http://localhost:8000/api/v1/apontamentos/work-item/1234/resumo?project_id=DEV"
```

**Checklist Endpoints**:
- [ ] ✅ GET /api/v1/user
- [ ] ✅ GET /api/v1/atividades
- [ ] ✅ GET /api/v1/work-items/search
- [ ] ✅ POST /api/v1/apontamentos
- [ ] ✅ GET /api/v1/apontamentos/{id}
- [ ] ✅ GET /api/v1/apontamentos/work-item/{id}
- [ ] ✅ GET /api/v1/apontamentos/work-item/{id}/resumo
- [ ] ✅ PUT /api/v1/apontamentos/{id} (optional)
- [ ] ✅ DELETE /api/v1/apontamentos/{id} (optional)

**Entregável**: Todos os endpoints implementados e testados

---

### Phase 4: Azure DevOps Integration (2-3 dias)

- [ ] Configurar Azure DevOps SDK/API
- [ ] Implementar autenticação (PAT token)
- [ ] Implementar `getWorkItem(id)`
- [ ] Implementar `updateWorkItem(id, delta)`
- [ ] Implementar `searchWorkItems(WIQL)`
- [ ] Implementar `getCurrentUser()`
- [ ] Error handling para Azure API failures
- [ ] Logging para debug

**IMPORTANTE**: 
- Azure DevOps update **NÃO deve ser síncrono** — usar fila de retry
- Se Azure falhar, salvar em `sync_queue` para retry automático
- Implementar exponential backoff (1s, 2s, 4s, 8s)

**Test**:
```bash
# Verificar que CompletedWork foi atualizado em Azure DevOps
# após criar apontamento via backend
```

---

### Phase 5: CORS & Security (1 dia)

- [ ] Configurar CORS headers:
  ```
  Access-Control-Allow-Origin: http://localhost:5000
  Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
  Access-Control-Allow-Headers: Content-Type, Authorization
  Access-Control-Allow-Credentials: true
  ```

- [ ] Implementar autenticação (JWT recomendado)
- [ ] HTTPS em produção
- [ ] Rate limiting
- [ ] Input validation com Pydantic/Zod
- [ ] SQL injection prevention
- [ ] CSRF protection

**Entregável**: Backend seguro e pronto para produção

---

### Phase 6: Testing (2-3 dias)

#### Unit Tests
- [ ] Tests para cada service
- [ ] Tests para validação de input
- [ ] Tests para cálculos de delta de horas
- [ ] Tests para error handling

#### Integration Tests
- [ ] Tests para endpoints com banco de dados real
- [ ] Tests para Azure DevOps integration (mock)
- [ ] Tests para sync queue retry logic
- [ ] Tests para CORS headers

#### E2E Tests (com Frontend)
- [ ] Rodar frontend em localhost:5000
- [ ] Rodar backend em localhost:8000
- [ ] Teste de criar apontamento (end-to-end)
- [ ] Verificar que Azure DevOps foi atualizado
- [ ] Verificar toast notification

**Comando**:
```bash
# Terminal 1: Backend
python -m pytest tests/ -v --cov

# Terminal 2: Frontend
npm run test

# Terminal 3: Frontend app
npm run dev

# Terminal 4: Backend app
python main.py
```

---

## 🧪 Testes de Integração (Com Frontend)

### Teste Manual Completo

1. **Abrir Frontend**
   ```bash
   npm run dev  # http://localhost:5000
   ```

2. **Abrir Backend**
   ```bash
   # Em outro terminal
   python main.py  # http://localhost:8000
   ```

3. **No navegador (http://localhost:5000)**
   - [ ] Página abre sem erros
   - [ ] Clica em "Apontar Tempo"
   - [ ] Modal abre com sucesso

4. **Preencher formulário**
   - [ ] Campo "Usuário" mostra nome correto (GET /user)
   - [ ] Digita "dashboard" em Tarefa → autocomplete funciona (GET /work-items/search)
   - [ ] Seleciona data no calendar
   - [ ] Digita duração
   - [ ] Dropdown "Tipo Atividade" mostra opções (GET /atividades)

5. **Submeter formulário**
   - [ ] Clica "Salvar"
   - [ ] POST /apontamentos enviado
   - [ ] Toast de sucesso aparece
   - [ ] Modal fecha
   - [ ] Nenhum erro no console

6. **Verificar Azure DevOps**
   - [ ] Abrir Azure DevOps
   - [ ] Ver work item #1234
   - [ ] CompletedWork foi incrementado
   - [ ] RemainingWork foi decrementado

---

## 🚀 Deployment Phases

### Staging Deployment
- [ ] Backend deployed em staging server
- [ ] Frontend deployed em staging CDN
- [ ] HTTPS configurado
- [ ] Monitoring/Logging setup
- [ ] QA testing

### Production Deployment
- [ ] Same as staging
- [ ] Backup strategy
- [ ] Rollback plan
- [ ] Post-deployment verification

---

## 📊 Success Criteria

**Backend Implementation Complete When**:

- [ ] ✅ All 6 core endpoints implemented
- [ ] ✅ Azure DevOps integration working
- [ ] ✅ Database schema created
- [ ] ✅ CORS configured
- [ ] ✅ Unit tests: >80% coverage
- [ ] ✅ Integration tests passing
- [ ] ✅ Manual E2E test successful
- [ ] ✅ Error handling for all scenarios
- [ ] ✅ Logging/Monitoring implemented
- [ ] ✅ Documentation complete

---

## 📞 Communication Protocol

### Daily Standup (Sync)
- What was completed yesterday
- What will be completed today
- Blockers/Issues

### Weekly Demo
- Show working features
- Test with frontend
- Gather feedback

### Code Review
- PR review before merge
- Frontend and backend collaborate

---

## 📚 Reference Documents

**Para Backend Team**:
1. [BACKEND_CONTEXT.md](BACKEND_CONTEXT.md) ← **COMECE AQUI**
2. [docs/migration/BACKEND_MIGRATION_GUIDE.md](docs/migration/BACKEND_MIGRATION_GUIDE.md)
3. [docs/migration/ARCHITECTURE.md](docs/migration/ARCHITECTURE.md)
4. [docs/migration/PRODUCT_SPECIFICATION.md](docs/migration/PRODUCT_SPECIFICATION.md)

**Para Frontend Team**:
1. [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
2. [client/src/hooks/use-api.ts](client/src/hooks/use-api.ts)
3. [CLEANUP_FINAL_REPORT.md](CLEANUP_FINAL_REPORT.md)

**Para DevOps**:
1. [docs/migration/ARCHITECTURE.md](docs/migration/ARCHITECTURE.md) - Deployment section
2. Criar CI/CD pipelines para ambos
3. Setup monitoring/alerting

---

## ✅ Sign-Off Checklist

**Backend Team Lead**: _________________ Data: _______

- [ ] Documentação entendida
- [ ] Timeline acordado
- [ ] Recursos alocados
- [ ] Tecnologia escolhida
- [ ] Primeira reunião de planejamento feita

**Frontend Team Lead**: ________________ Data: _______

- [ ] Frontend operacional
- [ ] Documentação revista
- [ ] Pronto para integração
- [ ] Testes automatizados configurados

**Project Manager**: __________________ Data: _______

- [ ] Timeline acordado
- [ ] Comunicação estabelecida
- [ ] Riscos identificados
- [ ] Plano de contingência

---

## 🎯 Timeline Estimado

```
Semana 1:    Phase 1-2 (Setup + Database)
Semana 2-3:  Phase 3-4 (Endpoints + Azure)
Semana 4:    Phase 5-6 (Security + Testing)
Semana 5:    Integration with Frontend
Semana 6:    Staging Deployment + QA
Semana 7-8:  Production Deployment
```

**Total**: ~8 semanas para completo

---

**Status**: ✅ Frontend Pronto  
**Próximo**: Backend Implementation  
**Data**: 18 de janeiro de 2026
