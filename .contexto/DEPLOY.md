# Deploy e Operações

**Última atualização:** 21/01/2026

---

## Ambientes

| Ambiente | VPS | Schema DB | Organização Azure |
|----------|-----|-----------|-------------------|
| Staging | 92.112.178.252 | aponta_sefaz_staging | sefaz-ceara-lab |
| Produção | 92.112.178.252 | aponta_sefaz | sefaz-ceara |

---

## Containers

### Listar containers
```bash
ssh root@92.112.178.252 "docker ps --format 'table {{.Names}}\t{{.Status}}'"
```

### Logs
```bash
# Últimas 50 linhas
ssh root@92.112.178.252 "docker logs api-aponta-staging --tail 50"

# Filtrar por autenticação
ssh root@92.112.178.252 "docker logs api-aponta-staging --tail 100 2>&1 | grep -E '(Token|auth|JWT|401)'"
```

### Reiniciar
```bash
ssh root@92.112.178.252 "docker restart api-aponta-staging"
```

---

## Deploy Manual (Staging)

### 1. Copiar arquivos para VPS
```bash
# Do WSL/Linux
scp app/auth.py app/config.py root@92.112.178.252:/tmp/
scp app/services/*.py root@92.112.178.252:/tmp/
```

### 2. Copiar para dentro do container
```bash
ssh root@92.112.178.252 "docker cp /tmp/auth.py api-aponta-staging:/app/app/auth.py"
ssh root@92.112.178.252 "docker cp /tmp/config.py api-aponta-staging:/app/app/config.py"
```

### 3. Instalar dependências (se necessário)
```bash
ssh root@92.112.178.252 "docker exec -u 0 api-aponta-staging pip install PyJWT==2.8.0"
```

### 4. Reiniciar container
```bash
ssh root@92.112.178.252 "docker restart api-aponta-staging"
```

---

## Recriar Container (Método Recomendado)

### Usando arquivo de ambiente

Os arquivos de ambiente estão em `/root/` no VPS:
- `/root/staging.env` - Variáveis para staging
- `/root/prod.env` - Variáveis para produção

### Staging
```bash
# Parar e remover
ssh root@92.112.178.252 "docker stop api-aponta-staging && docker rm api-aponta-staging"

# Recriar usando env-file
ssh root@92.112.178.252 'docker run -d \
  --name api-aponta-staging \
  --network aponta-shared-network \
  --env-file /root/staging.env \
  -p 8001:8000 \
  --health-cmd="curl -f http://localhost:8000/health || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  --restart=unless-stopped \
  staging-api:latest'
```

### Produção
```bash
# Parar e remover
ssh root@92.112.178.252 "docker stop api-aponta-prod && docker rm api-aponta-prod"

# Recriar usando env-file
ssh root@92.112.178.252 'docker run -d \
  --name api-aponta-prod \
  --network aponta-shared-network \
  --env-file /root/prod.env \
  -p 8000:8000 \
  --health-cmd="curl -f http://localhost:8000/health || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  --restart=unless-stopped \
  production-api:latest'
```

---

## Recriar Container (Método Alternativo - variáveis inline)
```bash
ssh root@92.112.178.252 'docker run -d \
  --name api-aponta-staging \
  --network aponta-shared-network \
  --restart unless-stopped \
  -e DATABASE_SCHEMA=aponta_sefaz_staging \
  -e AUTH_ENABLED=true \
  -e ENVIRONMENT=staging \
  -e DATABASE_HOST=postgres-aponta \
  -e "DATABASE_URL=postgresql://aponta_user:SENHA@postgres-aponta:5432/gestao_projetos" \
  -e AZURE_DEVOPS_ORG_URL=https://dev.azure.com/sefaz-ceara-lab \
  -e AZURE_DEVOPS_PAT=xxx \
  -e AZURE_EXTENSION_SECRET=xxx \
  -e "CORS_ORIGINS=https://staging-aponta.treit.com.br,https://dev.azure.com" \
  staging-api:latest'
```

---

## Variáveis de Ambiente Importantes

```env
# Autenticação
AUTH_ENABLED=true
AZURE_EXTENSION_SECRET=9TbeZUXAQW5BJANtPVl5ipNYknRutZLBQpIqenb8zv6IqNgajTixJQQJ99CAACAAAAAAAAAAAAAEAZDOCIUB
AZURE_EXTENSION_APP_ID=560de67c-a2e8-408a-86ae-be7ea6bd0b7a
AZURE_DEVOPS_PAT=xxx
AZURE_DEVOPS_ORG_URL=https://dev.azure.com/sefaz-ceara-lab

# Banco de Dados
DATABASE_SCHEMA=aponta_sefaz_staging  # staging usa aponta_sefaz_staging, prod usa aponta_sefaz
DATABASE_URL=postgresql://aponta_user:xxx@postgres-aponta:5432/gestao_projetos

# CORS
CORS_ORIGINS=https://staging-aponta.treit.com.br,https://dev.azure.com,https://*.visualstudio.com
```

---

## Verificações Úteis

### Testar PAT diretamente
```bash
ssh root@92.112.178.252 'curl -s -u ":SEU_PAT" "https://dev.azure.com/sefaz-ceara-lab/_apis/projects?api-version=7.1"'
```

### Verificar variáveis no container
```bash
ssh root@92.112.178.252 "docker exec api-aponta-staging printenv | grep AZURE"
```

### Verificar health
```bash
curl https://staging-aponta.treit.com.br/health
```

---

## Build de Imagens

### Estrutura no VPS
Os arquivos de deploy ficam em `/root/api-aponta-deploy/`:
```
/root/api-aponta-deploy/
├── Dockerfile
├── alembic.ini
├── alembic/
│   └── versions/
├── app/
├── requirements.txt
├── scripts/
└── tests/
```

### Copiar arquivos atualizados
```bash
# Do local para o VPS
scp app/services/timesheet_service.py root@92.112.178.252:/root/api-aponta-deploy/app/services/
scp app/auth.py root@92.112.178.252:/root/api-aponta-deploy/app/
```

### Build Staging
```bash
ssh root@92.112.178.252 'cd /root/api-aponta-deploy && docker build -t staging-api:latest .'
```

### Build Produção
```bash
ssh root@92.112.178.252 'cd /root/api-aponta-deploy && docker build -t production-api:latest .'
```

### Via Git
```bash
git pull origin develop
docker build -t staging-api .
docker restart api-aponta-staging
```

---

## Troubleshooting

### Container não inicia
```bash
# Ver logs de inicialização
ssh root@92.112.178.252 "docker logs api-aponta-staging 2>&1 | head -50"
```

### Erro de conexão com banco
```bash
# Testar conexão
ssh root@92.112.178.252 "docker exec api-aponta-staging python -c 'from app.database import engine; print(engine.url)'"
```

### 401 nas chamadas Azure DevOps (WIQL, Work Items)
**Causa mais comum:** O serviço está usando o App Token JWT em vez do PAT.

**Solução:** Garantir que `TimesheetService` e `AzureService` usam `settings.azure_devops_pat`:
```python
# CORRETO
self.token = settings.azure_devops_pat or token

# ERRADO (causa 401)
self.token = token  # App Token JWT não pode chamar APIs
```

### App Token JWT inválido
1. Verificar `AZURE_EXTENSION_SECRET` está correto
2. Obter em: https://aka.ms/vsmarketplace-manage > Botão direito > Certificate

### Work Items não aparecem no Timesheet
1. Verificar logs: `docker logs api-aponta-staging --tail 50 2>&1 | grep -i "wiql\|401"`
2. Se aparecer "401 Unauthorized", o PAT não está sendo usado
3. Verificar se `AZURE_DEVOPS_PAT` está configurado corretamente

### App Token JWT inválido
1. Verificar AZURE_EXTENSION_SECRET
2. Verificar se não expirou (~70 min)
---

## APIs Azure DevOps Utilizadas

### Autenticação e Perfil
| Endpoint | Uso |
|----------|-----|
| `vsaex.dev.azure.com/{org}/_apis/userentitlements/{userId}` | Buscar nome real do usuário |
| `vssps.dev.azure.com/{org}/_apis/identities` | Fallback para identidades |

### Work Items
| Endpoint | Uso |
|----------|-----|
| `dev.azure.com/{org}/{project}/_apis/wit/wiql` | Query WIQL |
| `dev.azure.com/{org}/{project}/_apis/wit/workitems` | Detalhes dos Work Items |
| `dev.azure.com/{org}/_apis/wit/workitemicons` | Ícones dos tipos |

### Projetos
| Endpoint | Uso |
|----------|-----|
| `dev.azure.com/{org}/_apis/projects` | Listar projetos |