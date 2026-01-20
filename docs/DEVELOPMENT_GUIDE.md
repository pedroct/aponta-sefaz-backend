# Gestão de Apontamentos - Guia de Desenvolvimento e Deploy

## 📋 Visão Geral

Este documento descreve o fluxo de desenvolvimento, testes e deploy do sistema de Gestão de Apontamentos.

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────────┐
│                         AZURE DEVOPS                                │
│  ┌─────────────────┐              ┌─────────────────┐              │
│  │  sefaz-ceara    │              │ sefaz-ceara-lab │              │
│  │   (Produção)    │              │    (Staging)    │              │
│  └────────┬────────┘              └────────┬────────┘              │
└───────────┼────────────────────────────────┼────────────────────────┘
            │                                │
            ▼                                ▼
┌───────────────────────┐      ┌───────────────────────┐
│   aponta.treit.com.br │      │staging-aponta.treit.  │
│      (Produção)       │      │    com.br (Staging)   │
├───────────────────────┤      ├───────────────────────┤
│  Frontend (React)     │      │  Frontend (React)     │
│  API (FastAPI)        │      │  API (FastAPI)        │
│  Schema: api_aponta   │      │  Schema: api_aponta_  │
│                       │      │          staging      │
└───────────────────────┘      └───────────────────────┘
            │                                │
            └────────────┬───────────────────┘
                         ▼
              ┌─────────────────────┐
              │  PostgreSQL 15      │
              │  (aponta-shared)    │
              │  IP: 92.112.178.252 │
              └─────────────────────┘
```

## 🔄 Fluxo de Branches

```
main (produção)
  │
  └── develop (staging)
        │
        ├── feature/nova-funcionalidade
        ├── fix/correcao-bug
        └── hotfix/correcao-urgente
```

## 📁 Estrutura de Repositórios (GitHub)

### Opção 1: Repositórios Separados (Recomendado)
```
github.com/sefaz-ce/
├── aponta-api/              # Backend FastAPI
│   ├── app/
│   ├── alembic/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── aponta-frontend/         # Frontend React + Extensão
│   ├── src/
│   ├── public/
│   ├── extension/           # Manifest da extensão
│   ├── Dockerfile
│   └── package.json
│
└── aponta-infra/            # Infraestrutura (opcional)
    ├── nginx/
    ├── docker-compose/
    └── scripts/
```

### Opção 2: Monorepo
```
github.com/sefaz-ce/aponta/
├── backend/
├── frontend/
├── infra/
└── .github/workflows/
```

## 🖥️ Ambiente Local

### Pré-requisitos
- Python 3.12+
- Node.js 20+
- Docker Desktop
- Git

### Setup Inicial

```bash
# 1. Clonar repositórios
git clone https://github.com/sefaz-ce/aponta-api.git
git clone https://github.com/sefaz-ce/aponta-frontend.git

# 2. Backend
cd aponta-api
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
pip install -r requirements.txt

# Criar .env local
cat > .env << EOF
AUTH_ENABLED=false
AZURE_DEVOPS_PAT=seu_pat_aqui
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/sefaz-ceara-lab
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=gestao_projetos
DATABASE_USER=aponta_user
DATABASE_PASSWORD=senha_local
DATABASE_SCHEMA=api_aponta_local
EOF

# Iniciar banco local
docker run -d --name postgres-local \
  -e POSTGRES_USER=aponta_user \
  -e POSTGRES_PASSWORD=senha_local \
  -e POSTGRES_DB=gestao_projetos \
  -p 5432:5432 postgres:15-alpine

# Rodar migrations
alembic upgrade head

# Iniciar API
uvicorn app.main:app --reload --port 8000

# 3. Frontend (outro terminal)
cd aponta-frontend
npm install
npm run dev
```

### URLs Locais
- **API:** http://localhost:8000
- **Swagger:** http://localhost:8000/docs
- **Frontend:** http://localhost:5173

## 🧪 Testes

```bash
# Backend - testes unitários
cd aponta-api
pytest tests/ -v

# Frontend - testes
cd aponta-frontend
npm test
```

## 🚀 Deploy

### Deploy Manual (SSH)

```bash
# Deploy Staging
./deploy/upload-backend.sh staging

# Deploy Produção
./deploy/upload-backend.sh production
```

### Deploy Automático (CI/CD)

O deploy é automatizado via GitHub Actions:

| Branch | Ambiente | Trigger |
|--------|----------|---------|
| `develop` | Staging | Push automático |
| `main` | Produção | Push (após merge) |

### Fluxo de Deploy

```
1. Desenvolver feature
   └── git checkout -b feature/minha-feature

2. Commit e Push
   └── git push origin feature/minha-feature

3. Criar Pull Request → develop
   └── Code Review + Testes automáticos

4. Merge → develop
   └── 🚀 Deploy automático para STAGING

5. Testar em Staging
   └── https://staging-aponta.treit.com.br
   └── Extensão na org: sefaz-ceara-lab

6. Criar Pull Request → main
   └── Aprovação necessária

7. Merge → main
   └── 🚀 Deploy automático para PRODUÇÃO
```

## 🔐 Secrets do GitHub

Configure no repositório (Settings > Secrets):

| Secret | Descrição |
|--------|-----------|
| `VPS_SSH_KEY` | Chave SSH privada para acesso à VPS |
| `VPS_HOST` | IP da VPS (92.112.178.252) |

## 📦 Extensão Azure DevOps

### Publicação da Extensão

```bash
# 1. Build do frontend
cd aponta-frontend
npm run build

# 2. Criar pacote da extensão
tfx extension create --manifest-globs vss-extension.json

# 3. Publicar no Marketplace
# - Staging: Publicar como "private" para sefaz-ceara-lab
# - Produção: Publicar como "public" ou "private" para sefaz-ceara
```

### Ambientes da Extensão

| Ambiente | Publisher | Organização | API URL |
|----------|-----------|-------------|---------|
| Staging | sefaz-staging | sefaz-ceara-lab | https://staging-aponta.treit.com.br/api |
| Produção | sefaz | sefaz-ceara | https://aponta.treit.com.br/api |

## 🗄️ Banco de Dados

### Schemas

| Ambiente | Schema | Descrição |
|----------|--------|-----------|
| Local | `api_aponta_local` | Desenvolvimento |
| Staging | `api_aponta_staging` | Homologação |
| Produção | `api_aponta` | Produção |

### Migrations

```bash
# Criar nova migration
alembic revision --autogenerate -m "descricao_da_mudanca"

# Aplicar migrations
alembic upgrade head

# Reverter última migration
alembic downgrade -1
```

## 📊 Monitoramento

### Logs

```bash
# Ver logs da API de produção
ssh root@92.112.178.252 "docker logs api-aponta-prod -f"

# Ver logs do staging
ssh root@92.112.178.252 "docker logs api-aponta-staging -f"
```

### Health Checks

```bash
# Produção
curl https://aponta.treit.com.br/api/v1

# Staging
curl https://staging-aponta.treit.com.br/api/v1
```

## 📞 Contatos

- **Desenvolvedor:** Pedro Teixeira
- **Email:** pedro.teixeira@sefaz.ce.gov.br

## 📝 Changelog

Ver [CHANGELOG.md](docs/release/CHANGELOG.md) para histórico de versões.
