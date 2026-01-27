# Análise de Arquitetura DevOps - Sistema Aponta

**Data:** 27 de Janeiro de 2026  
**Autor:** Análise automatizada via GitHub Copilot  
**Versão:** 1.0

---

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura Atual](#arquitetura-atual)
3. [Infraestrutura](#infraestrutura)
4. [Pipeline CI/CD](#pipeline-cicd)
5. [Problemas Identificados](#problemas-identificados)
6. [Recomendações](#recomendações)
7. [Plano de Melhorias](#plano-de-melhorias)

---

## 🎯 Visão Geral

O **Sistema Aponta** é uma aplicação para registro de apontamentos de horas integrada ao Azure DevOps. Consiste em:

- **Backend**: API FastAPI (Python 3.12)
- **Frontend**: Extensão Azure DevOps (React 18 + TypeScript)
- **Banco de Dados**: PostgreSQL 15 (Supabase)
- **Infraestrutura**: VPS única com Docker + Nginx

### Stack Tecnológico

| Camada | Tecnologia | Versão |
|--------|------------|--------|
| **Backend** | FastAPI | 0.104+ |
| **ORM** | SQLAlchemy | 2.0 |
| **Migrations** | Alembic | 1.12+ |
| **Runtime** | Python | 3.12 |
| **Frontend** | React | 18.x |
| **Build Tool** | Vite | 5.x |
| **Linguagem** | TypeScript | 5.x |
| **Container** | Docker | 24.x |
| **Proxy** | Nginx | 1.25 |
| **Database** | PostgreSQL | 15 |
| **BaaS** | Supabase | Cloud |

---

## 🏗️ Arquitetura Atual

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AZURE DEVOPS                                  │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                    Extension (Frontend)                      │    │
│  │  React 18 + TypeScript + Vite + Azure DevOps SDK            │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                │
                                │ HTTPS
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      VPS (92.112.178.252)                           │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │                      Nginx Reverse Proxy                     │    │
│  │  - SSL Termination (Let's Encrypt)                          │    │
│  │  - aponta.sefaz.ce.gov.br → :8080 (production)              │    │
│  │  - staging.aponta.sefaz.ce.gov.br → :8081 (staging)         │    │
│  └─────────────────────────────────────────────────────────────┘    │
│                    │                      │                         │
│                    ▼                      ▼                         │
│  ┌──────────────────────┐  ┌──────────────────────┐                │
│  │  Docker: Production  │  │   Docker: Staging    │                │
│  │  aponta-production   │  │   aponta-staging     │                │
│  │  Port: 8080          │  │   Port: 8081         │                │
│  │  FastAPI + Uvicorn   │  │   FastAPI + Uvicorn  │                │
│  └──────────────────────┘  └──────────────────────┘                │
│              │                        │                             │
└──────────────┼────────────────────────┼─────────────────────────────┘
               │                        │
               └───────────┬────────────┘
                           │ PostgreSQL Connection
                           ▼
               ┌───────────────────────┐
               │      Supabase         │
               │   PostgreSQL Cloud    │
               │   (Managed Service)   │
               └───────────────────────┘
```

### Estrutura de Diretórios no VPS

```
/opt/
├── aponta-production/          # Ambiente de produção
│   ├── app/                    # Código fonte
│   ├── .env                    # Variáveis de ambiente
│   ├── docker-compose.yml      # Configuração Docker
│   └── Dockerfile              # Build da imagem
│
├── aponta-staging/             # Ambiente de staging
│   ├── app/                    # Código fonte
│   ├── .env                    # Variáveis de ambiente
│   ├── docker-compose.yml      # Configuração Docker
│   └── Dockerfile              # Build da imagem
│
└── backups/                    # Backups (recomendado criar)
```

### Repositórios Git

| Repositório | Branch Default | Descrição |
|-------------|----------------|-----------|
| `pedroct/aponta-sefaz-backend` | develop | Backend API |
| `pedroct/aponta-sefaz-frontend` | main | Frontend Extension |

---

## 🔧 Infraestrutura

### VPS - Especificações

| Item | Valor |
|------|-------|
| **IP** | 92.112.178.252 |
| **Usuário SSH** | ubuntu |
| **SO** | Ubuntu 22.04 LTS |
| **Docker** | 24.x |
| **Docker Compose** | 2.x |

### Portas e Serviços

| Serviço | Porta Interna | Porta Externa | Domínio |
|---------|---------------|---------------|---------|
| Nginx | 80/443 | 80/443 | - |
| Production | 8080 | - | aponta.sefaz.ce.gov.br |
| Staging | 8081 | - | staging.aponta.sefaz.ce.gov.br |

### Variáveis de Ambiente Críticas

```env
# Banco de Dados
DATABASE_URL=postgresql://user:pass@host:5432/db
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx...

# Azure DevOps
AZURE_DEVOPS_PAT=xxxx              # ⚠️ Deve estar em GitHub Secrets
AZURE_DEVOPS_ORGANIZATION=org-name

# Aplicação
ENVIRONMENT=production|staging
JWT_SECRET_KEY=xxx
CORS_ORIGINS=https://...
```

---

## 🚀 Pipeline CI/CD

### Workflow: Deploy Staging

**Arquivo:** `.github/workflows/deploy-staging.yml`  
**Trigger:** Push para branch `develop`

```yaml
# Fluxo resumido
1. Checkout código
2. SSH para VPS
3. cd /opt/aponta-staging
4. git pull origin develop
5. docker-compose down
6. docker-compose up -d --build
7. Health check
```

### Workflow: Deploy Production

**Arquivo:** `.github/workflows/deploy-production.yml`  
**Trigger:** Push para branch `main`

```yaml
# Fluxo resumido
1. Checkout código
2. SSH para VPS
3. cd /opt/aponta-production
4. git pull origin main
5. docker-compose down
6. docker-compose up -d --build
7. Health check
```

### GitHub Secrets Necessários

| Secret | Descrição | Status |
|--------|-----------|--------|
| `VPS_HOST` | IP do servidor | ✅ Configurado |
| `VPS_USER` | Usuário SSH | ✅ Configurado |
| `VPS_SSH_KEY` | Chave privada SSH | ✅ Configurado |
| `AZURE_DEVOPS_PAT` | PAT do Azure DevOps | ✅ Configurado |
| `DATABASE_URL` | Connection string | ✅ Configurado |
| `SUPABASE_KEY` | Chave do Supabase | ✅ Configurado |

### Diagrama de Deploy

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Develop   │     │    Main     │     │   Release   │
│   Branch    │     │   Branch    │     │    Tags     │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │ push              │ push/merge        │ tag
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   GitHub    │     │   GitHub    │     │   GitHub    │
│   Actions   │     │   Actions   │     │   Actions   │
│  (staging)  │     │ (production)│     │  (release)  │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │ SSH + deploy      │ SSH + deploy      │
       ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Staging   │     │  Production │     │   Backup    │
│   Server    │     │   Server    │     │  + Deploy   │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## ⚠️ Problemas Identificados

### 🔴 Críticos

#### 1. Código "Fantasma" em Produção
- **Descrição:** VPS Production tem código que não existe no Git
- **Causa:** Deploy anterior via rsync ao invés de GitHub Actions
- **Impacto:** Impossível rastrear versão em produção
- **Status:** 🔴 Não resolvido

#### 2. Ausência de .git em Production
- **Descrição:** `/opt/aponta-production` não tem diretório `.git`
- **Causa:** Deploy via rsync copia apenas arquivos
- **Impacto:** Não é possível fazer `git pull`
- **Status:** 🔴 Não resolvido

### 🟡 Moderados

#### 3. Staging Desatualizado
- **Descrição:** Staging está 2 commits atrás de develop
- **Causa:** Workflow não executou após últimos pushes
- **Impacto:** Ambiente de testes desatualizado
- **Status:** 🟡 Pendente

#### 4. Falta de Workflow de Rollback
- **Descrição:** Não existe processo automatizado de rollback
- **Causa:** Não implementado
- **Impacto:** Recovery manual em caso de problemas
- **Status:** 🟡 Arquivo criado localmente, não commitado

#### 5. Sem Monitoramento
- **Descrição:** Não há alertas de saúde da aplicação
- **Causa:** Não configurado
- **Impacto:** Problemas detectados apenas manualmente
- **Status:** 🟡 Pendente

### 🟢 Menores

#### 6. Health Check Básico
- **Descrição:** Endpoint /health existe mas é simples
- **Causa:** Implementação mínima
- **Impacto:** Diagnóstico limitado
- **Status:** 🟢 Funcional

---

## 💡 Recomendações

### Curto Prazo (Imediato)

1. **Sincronizar Código**
   ```bash
   # Backup VPS
   ssh ubuntu@92.112.178.252 "sudo tar -czvf /opt/backup-$(date +%Y%m%d).tar.gz /opt/aponta-production"
   
   # Commit local
   git add . && git commit -m "feat: sync all local changes"
   git push origin develop
   ```

2. **Recriar Ambiente Production com Git**
   ```bash
   ssh ubuntu@92.112.178.252
   cd /opt
   sudo mv aponta-production aponta-production-backup
   sudo git clone https://github.com/pedroct/aponta-sefaz-backend.git aponta-production
   cd aponta-production && git checkout main
   # Copiar .env do backup
   sudo cp ../aponta-production-backup/.env .
   docker-compose up -d --build
   ```

### Médio Prazo (1-2 semanas)

3. **Implementar Monitoramento**
   - Uptime Robot ou similar para health checks externos
   - Alertas via Slack/Email quando serviço cair

4. **Melhorar Health Check**
   ```python
   @app.get("/health")
   async def health_check():
       return {
           "status": "healthy",
           "version": "1.0.0",
           "git_commit": os.getenv("GIT_COMMIT", "unknown"),
           "environment": os.getenv("ENVIRONMENT"),
           "database": await check_db_connection(),
           "timestamp": datetime.utcnow().isoformat()
       }
   ```

5. **Adicionar Versionamento**
   - Criar tags semânticas (v1.0.0, v1.1.0)
   - Injetar versão no build Docker

### Longo Prazo (1-3 meses)

6. **Separar Ambientes Fisicamente**
   - VPS dedicada para Production
   - VPS dedicada para Staging
   - Reduz risco de impacto cruzado

7. **Implementar Blue-Green Deployment**
   - Dois containers em production
   - Zero-downtime deployments
   - Rollback instantâneo

8. **Container Registry**
   - GitHub Container Registry (ghcr.io)
   - Imagens versionadas e imutáveis
   - Cache de builds

---

## 📈 Plano de Melhorias

### Fase 1: Estabilização (Semana 1)

| Tarefa | Prioridade | Responsável | Status |
|--------|------------|-------------|--------|
| Backup VPS Production | 🔴 Alta | DevOps | ⬜ Pendente |
| Commit código local | 🔴 Alta | Dev | ⬜ Pendente |
| Recriar Production com .git | 🔴 Alta | DevOps | ⬜ Pendente |
| Verificar workflows funcionando | 🔴 Alta | DevOps | ⬜ Pendente |

### Fase 2: Automação (Semana 2-3)

| Tarefa | Prioridade | Responsável | Status |
|--------|------------|-------------|--------|
| Implementar workflow rollback | 🟡 Média | DevOps | ⬜ Pendente |
| Adicionar monitoramento externo | 🟡 Média | DevOps | ⬜ Pendente |
| Melhorar health check | 🟡 Média | Dev | ⬜ Pendente |
| Documentar runbooks | 🟡 Média | DevOps | ⬜ Pendente |

### Fase 3: Otimização (Mês 2-3)

| Tarefa | Prioridade | Responsável | Status |
|--------|------------|-------------|--------|
| Separar VPS staging/prod | 🟢 Baixa | Infra | ⬜ Pendente |
| Implementar blue-green | 🟢 Baixa | DevOps | ⬜ Pendente |
| GitHub Container Registry | 🟢 Baixa | DevOps | ⬜ Pendente |
| CI com testes automatizados | 🟢 Baixa | Dev | ⬜ Pendente |

---

## 📚 Referências

### Documentação Interna

- [DEPLOY.md](../DEPLOY.md) - Guia de deploy
- [DEVELOPMENT_GUIDE.md](../DEVELOPMENT_GUIDE.md) - Guia de desenvolvimento
- [GITHUB_ACTIONS_DEPLOY_STATUS.md](../GITHUB_ACTIONS_DEPLOY_STATUS.md) - Status dos workflows
- [2026-01-27_SINCRONIZACAO_CODIGO_LOCAL_VPS.md](./2026-01-27_SINCRONIZACAO_CODIGO_LOCAL_VPS.md) - Análise de sincronização

### Comandos Úteis

```bash
# Status dos containers
ssh ubuntu@92.112.178.252 "docker ps"

# Logs de produção
ssh ubuntu@92.112.178.252 "docker logs aponta-production --tail 100"

# Health check
curl -s https://aponta.sefaz.ce.gov.br/health | jq
curl -s https://staging.aponta.sefaz.ce.gov.br/health | jq

# Últimos deploys
gh run list --workflow=deploy-staging.yml --limit=5
gh run list --workflow=deploy-production.yml --limit=5
```

---

## 📝 Histórico de Revisões

| Data | Versão | Autor | Descrição |
|------|--------|-------|-----------|
| 2026-01-27 | 1.0 | GitHub Copilot | Documento inicial |

---

*Documento gerado como parte da análise de arquitetura DevOps do Sistema Aponta.*
