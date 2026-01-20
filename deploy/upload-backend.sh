#!/bin/bash
# Script de Deploy para novo servidor
# IP: 92.112.178.252

set -e

SERVER="ubuntu@92.112.178.252"
REMOTE_PATH="/home/ubuntu/aponta-sefaz"

echo "=========================================="
echo "Deploy Aponta SEFAZ - Novo Servidor"
echo "=========================================="

# 1. Enviar configs de deploy
echo ""
echo "[1/4] Enviando configurações..."
scp -r deploy/shared/* ${SERVER}:${REMOTE_PATH}/shared/
scp deploy/production/docker-compose.yml deploy/production/.env ${SERVER}:${REMOTE_PATH}/production/
scp deploy/staging/docker-compose.yml deploy/staging/.env ${SERVER}:${REMOTE_PATH}/staging/

# 2. Compactar backend (excluindo desnecessários)
echo ""
echo "[2/4] Compactando backend..."
tar --exclude='node_modules' \
    --exclude='.git' \
    --exclude='dist' \
    --exclude='__pycache__' \
    --exclude='.venv' \
    --exclude='.pytest_cache' \
    --exclude='htmlcov' \
    --exclude='*.pyc' \
    --exclude='deploy' \
    -czvf /tmp/backend.tar.gz -C . .

# 3. Enviar backend
echo ""
echo "[3/4] Enviando backend..."
scp /tmp/backend.tar.gz ${SERVER}:/tmp/

# 4. No servidor: extrair para prod e staging
echo ""
echo "[4/4] Extraindo no servidor..."
ssh ${SERVER} << 'EOF'
cd /tmp
tar -xzvf backend.tar.gz -C /home/ubuntu/aponta-sefaz/production/backend/
tar -xzvf backend.tar.gz -C /home/ubuntu/aponta-sefaz/staging/backend/
rm backend.tar.gz
echo "Backend extraído com sucesso!"
EOF

# Limpar local
rm /tmp/backend.tar.gz

echo ""
echo "=========================================="
echo "✅ Backend enviado!"
echo ""
echo "Próximos passos:"
echo "1. Enviar frontend (fe-aponta) separadamente"
echo "2. Configurar SSL em ${REMOTE_PATH}/shared/ssl/"
echo "3. Editar senhas nos arquivos .env"
echo "4. docker compose up -d em shared, production, staging"
echo "=========================================="
