# Estrutura de Repositórios para o Projeto Aponta

## Repositórios no GitHub/GitLab

Recomendo criar os seguintes repositórios:

```
sefaz-ce/
├── aponta-api            # Este repositório (Backend FastAPI)
├── aponta-frontend       # Frontend React + Extensão Azure DevOps
└── aponta-docs           # (Opcional) Documentação centralizada
```

---

## 1. aponta-api (Backend)

**Branch Strategy:**
```
main ────────────────────────────────────────────────► Produção
  │
  └── develop ───────────────────────────────────────► Staging
        │
        ├── feature/timesheet-semanal
        ├── feature/relatorios
        ├── fix/autenticacao
        └── hotfix/correcao-urgente
```

**Estrutura:**
```
aponta-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── auth.py
│   ├── database.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   └── repositories/
├── alembic/
│   ├── versions/
│   └── env.py
├── tests/
├── deploy/
├── docs/
├── .github/
│   └── workflows/
│       ├── deploy-staging.yml
│       └── deploy-production.yml
├── Dockerfile
├── requirements.txt
├── pytest.ini
└── README.md
```

---

## 2. aponta-frontend (Frontend + Extensão)

**Estrutura:**
```
aponta-frontend/
├── src/
│   ├── components/
│   ├── hooks/
│   ├── services/
│   ├── pages/
│   └── App.tsx
├── public/
│   └── static/
├── extension/                    # Configs da extensão Azure DevOps
│   ├── vss-extension.json        # Manifest
│   ├── overview.md
│   └── images/
├── .github/
│   └── workflows/
│       ├── deploy-staging.yml
│       └── deploy-production.yml
├── Dockerfile
├── nginx.conf
├── package.json
├── vite.config.ts
└── README.md
```

---

## Fluxo de Trabalho Completo

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              DESENVOLVIMENTO                                │
└─────────────────────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 1. DESENVOLVER LOCALMENTE                                                    │
│    ─────────────────────                                                    │
│    • Backend: uvicorn app.main:app --reload --port 8000                     │
│    • Frontend: npm run dev (localhost:5173)                                 │
│    • Banco: PostgreSQL local ou Docker                                      │
│    • Auth: AUTH_ENABLED=false (mock user)                                   │
└─────────────────────────────────────────────────────────────────────────────┘
     │
     │ git push origin feature/minha-feature
     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 2. PULL REQUEST → develop                                                    │
│    ─────────────────────────                                                │
│    • Code Review                                                            │
│    • Testes automáticos (GitHub Actions)                                    │
│    • Aprovação necessária                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
     │
     │ Merge aprovado
     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 3. DEPLOY AUTOMÁTICO → STAGING                                               │
│    ───────────────────────────                                              │
│    • GitHub Actions executa deploy                                          │
│    • URL: https://staging-aponta.treit.com.br                               │
│    • Schema: api_aponta_staging                                             │
│    • Organização: sefaz-ceara-lab                                           │
└─────────────────────────────────────────────────────────────────────────────┘
     │
     │ Testes de homologação
     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 4. TESTES EM STAGING                                                         │
│    ────────────────────                                                     │
│    • Testar extensão na org sefaz-ceara-lab                                 │
│    • Validar funcionalidades                                                │
│    • Testes de integração                                                   │
│    • Aprovação do usuário                                                   │
└─────────────────────────────────────────────────────────────────────────────┘
     │
     │ git checkout main && git merge develop
     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 5. PULL REQUEST → main                                                       │
│    ───────────────────                                                      │
│    • Aprovação obrigatória                                                  │
│    • Testes automáticos                                                     │
│    • Review final                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
     │
     │ Merge aprovado
     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│ 6. DEPLOY AUTOMÁTICO → PRODUÇÃO                                              │
│    ─────────────────────────────                                            │
│    • GitHub Actions executa deploy                                          │
│    • URL: https://aponta.treit.com.br                                       │
│    • Schema: api_aponta                                                     │
│    • Organização: sefaz-ceara                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Comandos Úteis

### Desenvolvimento Local
```bash
# Iniciar ambiente local
cd aponta-api
source venv/bin/activate
uvicorn app.main:app --reload

# Rodar testes
pytest tests/ -v

# Criar migration
alembic revision --autogenerate -m "descricao"

# Aplicar migrations
alembic upgrade head
```

### Deploy Manual
```bash
# Deploy para staging
./deploy.sh staging

# Deploy para produção
./deploy.sh production

# Deploy para ambos
./deploy.sh all
```

### Monitoramento
```bash
# Logs de produção
ssh root@92.112.178.252 "docker logs api-aponta-prod -f"

# Logs de staging
ssh root@92.112.178.252 "docker logs api-aponta-staging -f"

# Status dos containers
ssh root@92.112.178.252 "docker ps"
```

---

## Configuração do GitHub

### 1. Criar Repositórios
```bash
# Via GitHub CLI
gh repo create sefaz-ce/aponta-api --public --description "API Backend - Gestão de Apontamentos"
gh repo create sefaz-ce/aponta-frontend --public --description "Frontend React - Gestão de Apontamentos"
```

### 2. Configurar Secrets
No GitHub, vá em **Settings > Secrets and variables > Actions**:

| Secret | Valor |
|--------|-------|
| `VPS_SSH_KEY` | Chave SSH privada |
| `VPS_HOST` | `92.112.178.252` |

### 3. Configurar Environments
Crie dois environments em **Settings > Environments**:
- `staging` - Deploy automático
- `production` - Requer aprovação manual

### 4. Proteção de Branches
Em **Settings > Branches > Branch protection rules**:

**Branch `main`:**
- ✅ Require pull request before merging
- ✅ Require approvals (1)
- ✅ Require status checks to pass
- ✅ Require branches to be up to date

**Branch `develop`:**
- ✅ Require pull request before merging
- ✅ Require status checks to pass

---

## Extensão Azure DevOps

### Publicação

1. **Build do Frontend**
   ```bash
   cd aponta-frontend
   npm run build
   ```

2. **Criar Pacote**
   ```bash
   tfx extension create --manifest-globs vss-extension.json
   ```

3. **Publicar**
   - **Staging:** Publicar como privada para `sefaz-ceara-lab`
   - **Produção:** Publicar como privada para `sefaz-ceara`

### Ambientes da Extensão

| Arquivo | Ambiente | API_URL |
|---------|----------|---------|
| `vss-extension.staging.json` | Staging | `https://staging-aponta.treit.com.br/api` |
| `vss-extension.json` | Produção | `https://aponta.treit.com.br/api` |
