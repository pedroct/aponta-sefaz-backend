---
type: agent
name: devops-specialist
description: Expert in Docker, CI/CD, and VPS deployment for Sistema Aponta
category: infrastructure
generated: 2026-01-22
status: filled
scaffoldVersion: "2.0.0"
---
# DevOps Specialist - Sistema Aponta

## Role

Especialista em infraestrutura, containerização e CI/CD para o Sistema Aponta.

## Key Responsibilities

- Gerenciar containers Docker no VPS
- Manter pipelines de CI/CD (GitHub Actions)
- Configurar e manter Nginx reverse proxy
- Gerenciar certificados SSL
- Monitorar health dos serviços

## Infrastructure Overview

### VPS Details

| Item | Value |
|------|-------|
| **IP** | 92.112.178.252 |
| **Provider** | Hostinger |
| **OS** | Ubuntu |
| **Access** | `ssh root@92.112.178.252` |

### Containers

| Container | Image | Port | Purpose |
|-----------|-------|------|---------|
| `api-aponta-staging` | `staging-api:latest` | 8001 | Backend Staging |
| `api-aponta-prod` | `production-api:latest` | 8000 | Backend Produção |
| `fe-aponta-staging` | `staging-frontend` | 80 | Frontend Staging |
| `fe-aponta-prod` | `production-frontend` | 80 | Frontend Produção |
| `postgres-aponta` | `postgres:15-alpine` | 5432 | Database |
| `nginx-aponta` | `nginx:alpine` | 80/443 | Proxy Reverso |

### Network

Todos os containers estão na rede `aponta-shared-network`.

## Key Files

| File | Purpose |
|------|---------|
| `Dockerfile` | Build da imagem da API |
| `docker-compose.yml` | Produção compose |
| `docker-compose.staging.yml` | Staging compose |
| `.github/workflows/deploy-staging.yml` | CI/CD Staging |
| `.github/workflows/deploy-production.yml` | CI/CD Produção |
| `nginx/nginx.conf` | Nginx configuration |

## Environment Files

Arquivos de ambiente no VPS:
- `/root/staging.env` — Variáveis para staging
- `/root/prod.env` — Variáveis para produção

### Required Variables

```env
# Database
DATABASE_URL=postgresql://aponta_user:xxx@postgres-aponta:5432/gestao_projetos
DATABASE_SCHEMA=aponta_sefaz_staging  # ou aponta_sefaz

# Authentication
AUTH_ENABLED=true
AZURE_EXTENSION_SECRET=xxx
AZURE_EXTENSION_APP_ID=560de67c-a2e8-408a-86ae-be7ea6bd0b7a
AZURE_DEVOPS_PAT=xxx
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/sefaz-ceara-lab

# CORS
CORS_ORIGINS=https://staging-aponta.treit.com.br,https://dev.azure.com
```

## Common Commands

### Container Management

```bash
# Listar containers
ssh root@92.112.178.252 "docker ps --format 'table {{.Names}}\t{{.Status}}'"

# Ver logs
ssh root@92.112.178.252 "docker logs api-aponta-staging --tail 50"

# Reiniciar container
ssh root@92.112.178.252 "docker restart api-aponta-staging"

# Verificar variáveis
ssh root@92.112.178.252 "docker exec api-aponta-staging printenv | grep AZURE"
```

### Deploy Manual (Hotfix)

```bash
# 1. Copiar arquivo para VPS
scp app/services/azure.py root@92.112.178.252:/tmp/

# 2. Copiar para container
ssh root@92.112.178.252 "docker cp /tmp/azure.py api-aponta-staging:/app/app/services/azure.py"

# 3. Reiniciar
ssh root@92.112.178.252 "docker restart api-aponta-staging"
```

### Rebuild Container

```bash
# Staging
ssh root@92.112.178.252 'docker stop api-aponta-staging && docker rm api-aponta-staging'
ssh root@92.112.178.252 'docker run -d \
  --name api-aponta-staging \
  --network aponta-shared-network \
  --env-file /root/staging.env \
  -p 8001:8000 \
  --health-cmd="curl -f http://localhost:8000/health || exit 1" \
  --health-interval=30s \
  --restart=unless-stopped \
  staging-api:latest'
```

### Build Images

```bash
# Build no VPS
ssh root@92.112.178.252 'cd /root/api-aponta-deploy && docker build -t staging-api:latest .'
```

## CI/CD Pipeline

### Staging (deploy-staging.yml)

Trigger: Push to `develop`

Steps:
1. Checkout code
2. Setup Python 3.12
3. Install dependencies
4. Run pytest
5. rsync to VPS
6. docker compose up --build
7. Health check

### Production (deploy-production.yml)

Trigger: Push to `main`

Same steps, different environment.

## Troubleshooting

### Container não inicia

```bash
ssh root@92.112.178.252 "docker logs api-aponta-staging 2>&1 | head -50"
```

### 502 Bad Gateway

- Verificar se container está rodando
- Verificar logs por erros Python
- Verificar se porta está exposta corretamente

### Health check falha

```bash
curl https://staging-aponta.treit.com.br/health
```

## Related Docs

- [architecture.md](../docs/architecture.md)
- [development-workflow.md](../docs/development-workflow.md)
