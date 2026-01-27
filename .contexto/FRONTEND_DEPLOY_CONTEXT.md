# Contexto para Reestruturacao de Deploy - Frontend Aponta

> **Documento de contexto para LLM**
> Use este documento para aplicar as mesmas boas praticas de deploy no repositorio do frontend.

---

## Problema Original (Backend)

A documentacao de deploy estava desatualizada e misturava **5 metodos diferentes**:
- SCP manual + docker cp
- git pull no VPS
- Clone manual
- docker run com variaveis inline
- GitHub Actions (metodo correto atual)

**Consequencias:**
- LLMs seguiam documentacao desatualizada e faziam deploy manual
- Producao ficava a frente de staging
- Secrets hardcoded em arquivos `.env` no repositorio

---

## Solucao Implementada (Backend)

### Arquitetura de Deploy

```
GitHub Repository
    │
    ├─── develop branch ──> Deploy Staging (automatico)
    │
    └─── main branch ──> Deploy Production (automatico via PR)
```

### Principios Aplicados

1. **Deploy 100% via GitHub Actions** - Nenhum deploy manual
2. **Secrets via GitHub Secrets** - Nao versionar `.env` com credenciais
3. **Geracao dinamica de .env** - Workflow gera `.env` no VPS a partir dos secrets
4. **Documentacao unica** - Um unico `docs/DEPLOY.md` como fonte de verdade
5. **Rollback via workflow** - Workflow manual para rollback com image tags

---

## Estrutura do Frontend

### Repositorio
- **GitHub:** https://github.com/pedroct/aponta-sefaz-frontend
- **Local:** C:\Projetos\Azure\fe-aponta
- **Stack:** React + Vite + TypeScript

### VPS (92.112.178.252)
- **Staging:** /home/ubuntu/aponta-sefaz/staging/frontend
- **Producao:** /home/ubuntu/aponta-sefaz/production/frontend

### Containers Docker
- **Staging:** `fe-aponta-staging`
- **Producao:** `fe-aponta-prod`

### URLs
- **Staging:** https://staging-aponta.treit.com.br
- **Producao:** https://aponta.treit.com.br

---

## Arquivos a Criar no Frontend

### 1. `.github/workflows/deploy-staging.yml`

```yaml
# Deploy automatico para Staging quando ha push na branch develop
name: Deploy Staging

on:
  push:
    branches:
      - develop

jobs:
  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build for staging
        run: npm run build
        env:
          VITE_API_URL: /api/v1
          VITE_AZURE_ORG: sefaz-ceara-lab
          VITE_AZURE_PROJECT: DEV
          VITE_ENVIRONMENT: staging

      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  deploy:
    name: Deploy Staging
    needs: build
    runs-on: ubuntu-latest
    environment: staging

    steps:
      - name: Download build artifact
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Configurar SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.VPS_SSH_PRIVATE_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.VPS_HOST }} >> ~/.ssh/known_hosts

      - name: Deploy para Staging
        run: |
          rsync -avz --delete \
            dist/ ${{ secrets.VPS_USER }}@${{ secrets.VPS_HOST }}:/home/ubuntu/aponta-sefaz/staging/frontend/dist/

      - name: Rebuild container
        run: |
          ssh ${{ secrets.VPS_USER }}@${{ secrets.VPS_HOST }} "
            cd /home/ubuntu/aponta-sefaz/staging && \
            docker compose up -d --build --force-recreate frontend
          "

      - name: Verificar deploy
        run: |
          sleep 10
          curl -sf https://staging-aponta.treit.com.br || exit 1
          echo "Deploy staging verificado!"
```

### 2. `.github/workflows/deploy-production.yml`

```yaml
# Deploy para Producao quando ha merge na branch main
name: Deploy Production

on:
  push:
    branches:
      - main

jobs:
  build:
    name: Build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Build for production
        run: npm run build
        env:
          VITE_API_URL: /api/v1
          VITE_AZURE_ORG: sefaz-ceara
          VITE_AZURE_PROJECT: ""
          VITE_ENVIRONMENT: production

      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: dist
          path: dist/

  deploy:
    name: Deploy Production
    needs: build
    runs-on: ubuntu-latest
    environment: production

    steps:
      - name: Download build artifact
        uses: actions/download-artifact@v4
        with:
          name: dist
          path: dist/

      - name: Configurar SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.VPS_SSH_PRIVATE_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H ${{ secrets.VPS_HOST }} >> ~/.ssh/known_hosts

      - name: Deploy para Producao
        run: |
          rsync -avz --delete \
            dist/ ${{ secrets.VPS_USER }}@${{ secrets.VPS_HOST }}:/home/ubuntu/aponta-sefaz/production/frontend/dist/

      - name: Rebuild container
        run: |
          ssh ${{ secrets.VPS_USER }}@${{ secrets.VPS_HOST }} "
            cd /home/ubuntu/aponta-sefaz/production && \
            docker compose up -d --build --force-recreate frontend
          "

      - name: Verificar deploy
        run: |
          sleep 10
          curl -sf https://aponta.treit.com.br || exit 1
          echo "Deploy producao verificado!"
```

### 3. `docs/DEPLOY.md`

```markdown
# Deploy - Frontend Aponta SEFAZ

> **Fonte unica de verdade para deploy**

## Visao Geral

O deploy e 100% automatizado via GitHub Actions. **NAO faca deploy manual.**

## Ambientes

| Ambiente | Branch | URL | Trigger |
|----------|--------|-----|---------|
| Staging | develop | https://staging-aponta.treit.com.br | Push em develop |
| Producao | main | https://aponta.treit.com.br | Push em main (via PR) |

## Fluxo de Trabalho

### Deploy para Staging
1. Desenvolva na sua branch de feature
2. Abra PR para develop
3. Apos merge, o deploy e automatico

### Deploy para Producao
1. Teste em staging
2. Abra PR de develop para main
3. Apos merge, o deploy e automatico

## GitHub Secrets

Configure em **GitHub > Settings > Secrets and variables > Actions**:

### Repository Secrets
| Secret | Valor |
|--------|-------|
| VPS_HOST | 92.112.178.252 |
| VPS_USER | ubuntu |
| VPS_SSH_PRIVATE_KEY | (chave SSH) |

### Environment Secrets (staging e production)
| Secret | Descricao |
|--------|-----------|
| VITE_AZURE_ORG | Organizacao Azure DevOps |

## Monitoramento

### Verificar se esta online
curl https://staging-aponta.treit.com.br
curl https://aponta.treit.com.br

### Logs do container
ssh ubuntu@92.112.178.252 "docker logs fe-aponta-staging --tail 50"
ssh ubuntu@92.112.178.252 "docker logs fe-aponta-prod --tail 50"

## Procedimento de Emergencia

**Apenas se GitHub Actions estiver indisponivel:**

ssh ubuntu@92.112.178.252
cd /home/ubuntu/aponta-sefaz/staging/frontend
git pull origin develop
cd ..
docker compose up -d --build frontend
```

### 4. `.gitignore` (adicionar/verificar)

```gitignore
# Build
dist/
build/

# Dependencies
node_modules/

# Environment
.env
.env.local
.env.production

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db

# Logs
*.log
npm-debug.log*
```

---

## GitHub Secrets a Configurar

No repositorio https://github.com/pedroct/aponta-sefaz-frontend:

### Repository Secrets (Settings > Secrets > Actions)

| Secret | Valor |
|--------|-------|
| `VPS_HOST` | `92.112.178.252` |
| `VPS_USER` | `ubuntu` |
| `VPS_SSH_PRIVATE_KEY` | (mesma chave SSH do backend) |

### Environments

Criar dois environments: `staging` e `production`

**Environment: staging**
- Nenhum secret adicional necessario (variaveis de build sao hardcoded no workflow)

**Environment: production**
- Nenhum secret adicional necessario

---

## Documentacao a Deletar (se existir)

Procure e delete qualquer documentacao que mencione:
- Deploy manual via SCP
- docker cp para container
- git pull no VPS como metodo padrao
- Variaveis de ambiente hardcoded

---

## Checklist de Implementacao

- [ ] Criar `.github/workflows/deploy-staging.yml`
- [ ] Criar `.github/workflows/deploy-production.yml`
- [ ] Criar `docs/DEPLOY.md`
- [ ] Atualizar `.gitignore`
- [ ] Configurar GitHub Secrets (repository level)
- [ ] Criar environments `staging` e `production` no GitHub
- [ ] Deletar documentacao de deploy manual desatualizada
- [ ] Testar deploy em staging (push para develop)
- [ ] Testar deploy em producao (PR develop -> main)

---

## Diferenca Backend vs Frontend

| Aspecto | Backend | Frontend |
|---------|---------|----------|
| Build | Docker build no VPS | npm build no GitHub Actions |
| Artifact | Imagem Docker | Arquivos estaticos (dist/) |
| .env | Gerado no VPS via secrets | Build args no workflow |
| Container | api-aponta-* | fe-aponta-* |
| Compose | build: ./backend | build: ./frontend (ou nginx serve dist) |

---

## Comando para a LLM

> "Aplique a reestruturacao de deploy conforme o documento FRONTEND_DEPLOY_CONTEXT.md.
> Crie os workflows de GitHub Actions, a documentacao de deploy, e delete qualquer
> documentacao desatualizada que mencione deploy manual."
