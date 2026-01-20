# Guia de Deploy - Aponta SEFAZ

## Servidor
- **IP**: 92.112.178.252
- **Produção**: https://aponta.treit.com.br
- **Staging**: https://staging-aponta.treit.com.br

## Estrutura no Servidor

```
/home/ubuntu/aponta-sefaz/
├── production/
│   ├── backend/          # Clone do repo api-aponta-vps
│   ├── frontend/         # Clone do repo fe-aponta
│   ├── docker-compose.yml
│   └── .env
│
├── staging/
│   ├── backend/          # Clone do repo api-aponta-vps
│   ├── frontend/         # Clone do repo fe-aponta
│   ├── docker-compose.yml
│   └── .env
│
└── shared/
    ├── nginx/
    │   └── nginx.conf
    ├── ssl/
    │   ├── fullchain.pem
    │   └── privkey.pem
    ├── docker-compose.yml
    ├── init-db.sql
    └── .env
```

## Schemas do Banco de Dados
- **Produção**: `aponta_sefaz`
- **Staging**: `aponta_sefaz_staging`

---

## Deploy Inicial

### 1. Preparar arquivos localmente

```powershell
# No Windows - Compactar backend (excluindo desnecessários)
cd C:\Projetos\Azure
# Usar 7-Zip ou criar manualmente

# Ou no WSL:
cd /mnt/c/Projetos/Azure
tar --exclude='node_modules' --exclude='.git' --exclude='dist' --exclude='__pycache__' --exclude='.venv' -czvf backend.tar.gz api-aponta-vps/
tar --exclude='node_modules' --exclude='.git' --exclude='dist' -czvf frontend.tar.gz fe-aponta/
```

### 2. Enviar para o servidor

```bash
# Enviar configs (deploy/)
scp -r deploy/* ubuntu@92.112.178.252:/home/ubuntu/aponta-sefaz/

# Enviar backend compactado
scp backend.tar.gz ubuntu@92.112.178.252:/home/ubuntu/

# Enviar frontend compactado
scp frontend.tar.gz ubuntu@92.112.178.252:/home/ubuntu/
```

### 3. No servidor - Extrair e organizar

```bash
ssh ubuntu@92.112.178.252

cd /home/ubuntu

# Extrair backend para produção e staging
tar -xzvf backend.tar.gz
cp -r api-aponta-vps aponta-sefaz/production/backend
cp -r api-aponta-vps aponta-sefaz/staging/backend
rm -rf api-aponta-vps

# Extrair frontend para produção e staging
tar -xzvf frontend.tar.gz
cp -r fe-aponta aponta-sefaz/production/frontend
cp -r fe-aponta aponta-sefaz/staging/frontend
rm -rf fe-aponta

# Limpar
rm backend.tar.gz frontend.tar.gz
```

### 4. Configurar SSL (Cloudflare Origin Certificate)

```bash
cd /home/ubuntu/aponta-sefaz/shared/ssl

# Criar/colar certificados do Cloudflare
nano fullchain.pem   # Cole o certificado
nano privkey.pem     # Cole a chave privada

chmod 600 privkey.pem
chmod 644 fullchain.pem
```

### 5. Configurar senhas nos .env

```bash
# Shared (banco)
nano /home/ubuntu/aponta-sefaz/shared/.env
# Alterar: POSTGRES_PASSWORD=SUA_SENHA_FORTE

# Produção
nano /home/ubuntu/aponta-sefaz/production/.env
# Alterar: DATABASE_PASSWORD, AZURE_DEVOPS_PAT

# Staging
nano /home/ubuntu/aponta-sefaz/staging/.env
# Alterar: DATABASE_PASSWORD, AZURE_DEVOPS_PAT
```

### 6. Subir os serviços

```bash
cd /home/ubuntu/aponta-sefaz

# 1. Primeiro: Serviços compartilhados (nginx + postgres)
cd shared
docker compose up -d
docker compose logs -f  # Verificar se subiu

# 2. Produção
cd ../production
docker compose up -d --build
docker compose logs -f

# 3. Staging
cd ../staging
docker compose up -d --build
docker compose logs -f
```

### 7. Executar migrações

```bash
# Produção
cd /home/ubuntu/aponta-sefaz/production
docker compose exec api alembic upgrade head

# Staging
cd /home/ubuntu/aponta-sefaz/staging
docker compose exec api alembic upgrade head
```

---

## Comandos Úteis

### Ver logs
```bash
# Nginx
docker logs -f nginx-aponta

# API Produção
docker logs -f api-aponta-prod

# API Staging
docker logs -f api-aponta-staging
```

### Reiniciar serviços
```bash
# Apenas nginx (após alterar config)
docker exec nginx-aponta nginx -s reload

# Rebuild API produção
cd /home/ubuntu/aponta-sefaz/production
docker compose up -d --build api
```

### Verificar status
```bash
docker ps
curl http://localhost/health
```

---

## Atualização de Código

### Backend (Produção)
```bash
cd /home/ubuntu/aponta-sefaz/production/backend
git pull origin main
cd ..
docker compose up -d --build api
docker compose exec api alembic upgrade head
```

### Backend (Staging)
```bash
cd /home/ubuntu/aponta-sefaz/staging/backend
git pull origin develop
cd ..
docker compose up -d --build api
docker compose exec api alembic upgrade head
```

### Frontend
```bash
cd /home/ubuntu/aponta-sefaz/production/frontend
git pull origin main
cd ..
docker compose up -d --build frontend
```
