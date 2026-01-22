# ⚠️ GitHub Actions Deploy Pipeline - Status Report

## Problema Identificado

O workflow `Deploy Staging` está falhando na etapa de SSH com erro:
```
⚠️  ssh-keyscan falhou, tentando alternativa...
##[error]Process completed with exit code 1.
```

## Diagnóstico

### ✅ O que está funcionando:
- Repositório: `pedroct/aponta-sefaz-backend` ✅
- Branch trigger: `develop` ✅  
- Checkout: Commit `d5ba0ef` ✅
- Testes: Não foi executado (falhou antes)

### ❌ O que está falhando:
- Conexão SSH ao VPS de staging
- `ssh-keyscan` timeout de 15 segundos
- Tentativa alternativa com rsa,ecdsa também falhou

## Causas Possíveis

1. **Servidor VPS offline** - O servidor de staging (31.97.16.12 ou outro) não está respondendo
2. **Firewall bloqueando** - GitHub Actions IP não consegue acessar a porta SSH
3. **Secrets não configurados** - `VPS_HOST`, `VPS_USER`, `VPS_SSH_PRIVATE_KEY` ausentes/incorretos
4. **Network connectivity** - Problema de conectividade geral

## Próximas Ações Necessárias

### 1. Verificar Status do Servidor
```bash
# Verificar se servidor está online
ping <VPS_HOST>

# Verificar SSH
ssh -v ubuntu@<VPS_HOST> "echo OK"
```

### 2. Verificar GitHub Secrets
Ir para: **Settings → Secrets and variables → Actions**

Verificar se existem:
- ✅ `VPS_HOST` 
- ✅ `VPS_USER` 
- ✅ `VPS_SSH_PRIVATE_KEY`
- ✅ `DEPLOY_PATH_STG`

### 3. Configurar Secrets (Se necessário)

```bash
# Gerar chave SSH (se ainda não tiver)
ssh-keygen -t rsa -b 4096 -f ~/.ssh/staging_deploy -N ""

# Conteúdo da chave privada para GitHub Secret
cat ~/.ssh/staging_deploy | base64
```

Adicionar no GitHub:
- `VPS_HOST`: `31.97.16.12` (ou servidor correto)
- `VPS_USER`: `root` ou `ubuntu`
- `VPS_SSH_PRIVATE_KEY`: Conteúdo da chave privada
- `DEPLOY_PATH_STG`: `/home/ubuntu/aponta-sefaz/staging/backend` ou caminho correto

### 4. Permitir Chave SSH no VPS

No servidor, adicionar chave pública ao `~/.ssh/authorized_keys`:
```bash
# No VPS
echo "<VPS_SSH_PUBLIC_KEY>" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
```

## Workflow Atual

```
┌─ Push to develop
│
├─ Job: Testes
│  ├─ Setup Python 3.12
│  ├─ Install dependencies
│  └─ Run tests (pytest)
│
├─ Job: Deploy Staging (needs: test)
│  ├─ ❌ Configurar SSH ← FALHANDO AQUI
│  ├─ Deploy para Staging
│  ├─ rsync código
│  ├─ Docker restart
│  └─ Verificar health check
```

## Configuração do Workflow

**Arquivo**: `.github/workflows/deploy-staging.yml`

**Trigger**: Push em `develop`

**Etapas**:
1. Testes (pytest)
2. SSH setup
3. rsync código para VPS
4. `docker compose up -d --build`
5. Health check em `http://localhost:8000/api/v1`

## Variáveis de Ambiente

| Variável | Valor | Tipo |
|----------|-------|------|
| `DEPLOY_PATH` | `/home/ubuntu/aponta-sefaz/staging/backend` | Env |
| `DATABASE_SCHEMA` | `api_aponta_test` | Test env |
| `VPS_HOST` | ??? | Secret |
| `VPS_USER` | ??? | Secret |
| `VPS_SSH_PRIVATE_KEY` | ??? | Secret |
| `DEPLOY_PATH_STG` | ??? | Secret |

## ⚠️ Ações Imediatas

1. [ ] Verificar se servidor VPS está online
2. [ ] Confirmar IP/hostname do servidor staging
3. [ ] Configurar secrets no GitHub com dados corretos
4. [ ] Testar SSH manualmente
5. [ ] Retry do workflow

## Teste Manual

```bash
# Local
ssh -i ~/.ssh/staging_deploy root@31.97.16.12 "echo SSH OK"

# Se funcionar, adicionar a chave pública ao servidor:
ssh-copy-id -i ~/.ssh/staging_deploy root@31.97.16.12
```

## Referência

- Workflow file: `.github/workflows/deploy-staging.yml`
- Repository: `github.com/pedroct/aponta-sefaz-backend`
- Branch: `develop`
- Commit: `d5ba0ef`
