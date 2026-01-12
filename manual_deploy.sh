#!/bin/bash
# Script de deploy manual - Use quando a pipeline do GitHub Actions não estiver funcionando

set -e

echo "🚀 Deploy Manual para VPS"
echo "========================="
echo ""

# Configurações (ajuste se necessário)
VPS_HOST="31.97.16.12"
VPS_USER="root"
VPS_PATH="/opt/api-aponta-vps"

echo "📍 Destino: $VPS_USER@$VPS_HOST:$VPS_PATH"
echo ""

# Verifica se consegue conectar ao servidor
echo "🔍 Testando conexão SSH..."
if ! ssh -o ConnectTimeout=5 $VPS_USER@$VPS_HOST "echo 'Conexão OK'"; then
    echo "❌ Não foi possível conectar ao servidor!"
    echo "Verifique:"
    echo "  - Se o servidor está online"
    echo "  - Se a chave SSH está configurada corretamente"
    echo "  - Se o firewall está permitindo sua conexão"
    exit 1
fi

echo "✅ Conexão SSH OK"
echo ""

# Sincroniza arquivos
echo "📦 Sincronizando arquivos..."
rsync -avz --delete \
    --exclude='.git' \
    --exclude='.github' \
    --exclude='node_modules' \
    --exclude='.vscode' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.env' \
    --exclude='postgres-data' \
    --exclude='.DS_Store' \
    --exclude='nginx/ssl/fullchain.pem' \
    --exclude='nginx/ssl/privkey.pem' \
    --exclude='.coverage*' \
    --exclude='htmlcov' \
    ./ $VPS_USER@$VPS_HOST:$VPS_PATH/

echo "✅ Arquivos sincronizados"
echo ""

# Executa comandos no servidor
echo "🐳 Reconstruindo containers no servidor..."
ssh $VPS_USER@$VPS_HOST << 'ENDSSH'
    set -e
    cd /opt/api-aponta-vps

    echo "🔍 Verificando arquivos necessários..."
    if [ ! -f .env ]; then
        echo "❌ Erro: Arquivo .env não encontrado!"
        exit 1
    fi

    echo "🐳 Parando containers..."
    docker compose down --remove-orphans || true

    echo "📦 Reconstruindo imagens..."
    docker compose build --no-cache

    echo "🚀 Iniciando containers..."
    docker compose up -d

    echo "⏳ Aguardando inicialização (30s)..."
    sleep 30

    echo "🔍 Status dos containers:"
    docker compose ps

    echo ""
    echo "📋 Últimas linhas de log:"
    docker compose logs --tail=20

    echo ""
    echo "🏥 Testando health check..."
    if curl -f http://localhost/health; then
        echo ""
        echo "✅ Health check OK!"
    else
        echo ""
        echo "⚠️  Health check falhou, mas containers estão rodando."
        echo "Verifique os logs: docker compose logs -f api"
    fi
ENDSSH

echo ""
echo "✅ Deploy concluído!"
echo "🌐 API disponível em: https://api-aponta.pedroct.com.br"
echo ""
echo "Para verificar os logs:"
echo "  ssh $VPS_USER@$VPS_HOST 'cd $VPS_PATH && docker compose logs -f api'"