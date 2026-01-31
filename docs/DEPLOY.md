# Deploy - API Aponta SEFAZ

> **Fonte unica de verdade para deploy**
> Ultima atualizacao: Janeiro 2026

## Visao Geral

O deploy e 100% automatizado via GitHub Actions. **NAO faca deploy manual.**

```
┌─────────────────────────────────────────────────────────────┐
│                    GitHub Repository                         │
│  ┌─────────┐ PR  ┌─────────┐    ┌──────────────────────────┐│
│  │ develop │────>│  main   │    │ GitHub Secrets           ││
│  └────┬────┘     └────┬────┘    │ ├─ staging environment   ││
│       │               │         │ └─ production environment││
└───────┼───────────────┼─────────┴──────────────────────────┘│
        │               │                                      │
   Auto Deploy     Auto Deploy                                 │
        │               │                                      │
        v               v                                      │
┌─────────────────────────────────────────────────────────────┐
│                   VPS 92.112.178.252                         │
│  /home/ubuntu/aponta-sefaz/                                  │
│  ├── shared/     (nginx + postgres)                         │
│  ├── staging/    (.env gerado via GitHub Secrets)           │
│  └── production/ (.env gerado via GitHub Secrets)           │
└─────────────────────────────────────────────────────────────┘
```

## Ambientes

| Ambiente | Branch | URL | Trigger |
|----------|--------|-----|---------|
| Staging | `develop` | https://staging-aponta.treit.com.br | Push em develop |
| Producao | `main` | https://aponta.treit.com.br | Push em main (via PR) |

## Fluxo de Trabalho

### Deploy para Staging (Homologacao)

1. Desenvolva na sua branch de feature
2. Abra PR para `develop`
3. Apos merge, o deploy e automatico
4. Teste em https://staging-aponta.treit.com.br

### Deploy para Producao

1. Teste em staging
2. Abra PR de `develop` para `main`
3. Apos merge, o deploy e automatico
4. Verifique em https://aponta.treit.com.br

## GitHub Secrets

Os secrets sao gerenciados em: **GitHub > Settings > Secrets and variables > Actions**

### Repository Secrets (compartilhados)

| Secret | Descricao |
|--------|-----------|
| `VPS_HOST` | IP do servidor (92.112.178.252) |
| `VPS_USER` | Usuario SSH (ubuntu) |
| `VPS_SSH_PRIVATE_KEY` | Chave SSH privada |
| `DEPLOY_PATH_STG` | Path staging (/home/ubuntu/aponta-sefaz/staging/backend) |
| `DEPLOY_PATH_PRD` | Path producao (/home/ubuntu/aponta-sefaz/production/backend) |

### Environment Secrets

Configure em **Environments > staging** ou **Environments > production**:

| Secret | Descricao |
|--------|-----------|
| `DATABASE_PASSWORD` | Senha do PostgreSQL |
| `AZURE_DEVOPS_PAT` | Personal Access Token Azure DevOps |
| `AZURE_EXTENSION_SECRET` | Secret da extensao Azure |

## Monitoramento

### Health Checks

```bash
# Staging
curl https://staging-aponta.treit.com.br/health

# Producao
curl https://aponta.treit.com.br/health
```

### Logs dos Containers

```bash
# Staging
ssh ubuntu@92.112.178.252 "docker logs api-aponta-staging --tail 50"

# Producao
ssh ubuntu@92.112.178.252 "docker logs api-aponta-prod --tail 50"

# Filtrar erros
ssh ubuntu@92.112.178.252 "docker logs api-aponta-staging 2>&1 | grep -i error"
```

### Status dos Containers

```bash
ssh ubuntu@92.112.178.252 "docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'"
```

## Rollback

### Via GitHub Actions (Recomendado)

1. Acesse: **Actions > Rollback > Run workflow**
2. Selecione o ambiente (staging/production)
3. Informe a tag da imagem (commit SHA)
4. Execute

### Listar Tags Disponiveis

```bash
# Staging
ssh ubuntu@92.112.178.252 "docker images staging-api --format '{{.Tag}}\t{{.CreatedAt}}' | head -10"

# Producao
ssh ubuntu@92.112.178.252 "docker images production-api --format '{{.Tag}}\t{{.CreatedAt}}' | head -10"
```

## Troubleshooting

### Deploy falhou no GitHub Actions

1. Verifique os logs do workflow em **Actions**
2. Erros comuns:
   - SSH timeout: Verificar VPS esta online
   - Health check falhou: Ver logs do container
   - Secret nao encontrado: Verificar configuracao no GitHub

### Container nao inicia

```bash
# Ver logs de inicializacao
ssh ubuntu@92.112.178.252 "docker logs api-aponta-staging 2>&1 | head -50"

# Verificar .env foi gerado
ssh ubuntu@92.112.178.252 "head -10 /home/ubuntu/aponta-sefaz/staging/.env"
```

### Erro 401 nas chamadas Azure DevOps

1. Verificar `AZURE_DEVOPS_PAT` no GitHub Secrets
2. Verificar se PAT nao expirou
3. Ver logs: `grep -i "401\|unauthorized" `

### Atualizar um Secret

1. GitHub > Settings > Secrets and variables > Actions
2. Selecione o environment
3. Atualize o valor do secret
4. **Re-execute o deploy** para aplicar (push em develop/main ou re-run do workflow)

## Procedimento de Emergencia

**Apenas use se GitHub Actions estiver completamente indisponivel:**

```bash
# SSH para VPS
ssh ubuntu@92.112.178.252

# Staging
cd /home/ubuntu/aponta-sefaz/staging/backend
git pull origin develop
cd ..
docker compose up -d --build api

# Producao
cd /home/ubuntu/aponta-sefaz/production/backend
git pull origin main
cd ..
docker compose up -d --build api
```

> **IMPORTANTE:** Apos usar procedimento de emergencia, registre o incidente.

## Estrutura no VPS

```
/home/ubuntu/aponta-sefaz/
├── shared/
│   ├── docker-compose.yml    # nginx + postgres
│   ├── nginx/nginx.conf
│   ├── ssl/
│   └── init-db.sql
├── staging/
│   ├── docker-compose.yml
│   ├── backend/              # Codigo (synced via rsync)
│   └── .env                  # Gerado pelo GitHub Actions
└── production/
    ├── docker-compose.yml
    ├── backend/              # Codigo (synced via rsync)
    └── .env                  # Gerado pelo GitHub Actions
```

## Referencias

- Workflows: [.github/workflows/](.github/workflows/)
- Templates de ambiente: [deploy/*/env.template](deploy/)
- Arquitetura: [.contexto/ARQUITETURA.md](.contexto/ARQUITETURA.md)
