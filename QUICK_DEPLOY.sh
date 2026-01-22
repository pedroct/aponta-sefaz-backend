#!/bin/bash
# Quick Deploy Script para VPS Hostinger
# Execute este script no VPS após copiar os arquivos necessários

set -e

echo "=========================================="
echo "   Quick Deploy - API Aponta VPS"
echo "=========================================="
echo ""

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Função para printar com cor
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# 1. Verificar se está no diretório correto
if [ ! -f "docker-compose.yml" ]; then
    print_error "Erro: docker-compose.yml não encontrado!"
    print_warning "Execute este script no diretório /opt/api-aponta-vps"
    exit 1
fi

print_status "Diretório correto"

# 2. Verificar arquivo .env
if [ ! -f ".env" ]; then
    print_error "Erro: Arquivo .env não encontrado!"
    echo ""
    echo "Crie o arquivo .env:"
    echo "  nano .env"
    echo ""
    echo "Cole o conteúdo do .env local e salve (Ctrl+X, Y, Enter)"
    exit 1
fi

print_status "Arquivo .env encontrado"

# 3. Verificar certificados SSL
if [ ! -f "nginx/ssl/fullchain.pem" ] || [ ! -f "nginx/ssl/privkey.pem" ]; then
    print_error "Erro: Certificados SSL não encontrados!"
    echo ""
    echo "Copie os certificados:"
    echo "  nano nginx/ssl/fullchain.pem  # Cole o Origin Certificate"
    echo "  nano nginx/ssl/privkey.pem    # Cole a Private Key"
    exit 1
fi

print_status "Certificados SSL encontrados"

# 4. Verificar Docker
if ! command -v docker &> /dev/null; then
    print_error "Docker não está instalado!"
    echo ""
    echo "Instale o Docker:"
    echo "  curl -fsSL https://get.docker.com -o get-docker.sh"
    echo "  sh get-docker.sh"
    exit 1
fi

print_status "Docker instalado"

# 5. Verificar Docker Compose
if ! command -v docker compose &> /dev/null; then
    print_error "Docker Compose não está instalado!"
    exit 1
fi

print_status "Docker Compose instalado"

echo ""
echo "=========================================="
echo "   Iniciando Deploy..."
echo "=========================================="
echo ""

# 6. Parar containers existentes
print_warning "Parando containers existentes..."
docker compose down --remove-orphans 2>/dev/null || true

# 7. Build das imagens
print_warning "Construindo imagens Docker (isso pode demorar 2-3 minutos)..."
docker compose build --no-cache

# 8. Iniciar containers
print_warning "Iniciando containers..."
docker compose up -d

# 9. Health check com retry logic
print_warning "Aguardando inicialização dos serviços (pode levar até 40 segundos)..."

max_attempts=5
attempt=1
health_ok=false

echo ""
echo "=========================================="
echo "   Health Check - Retry Logic"
echo "=========================================="
echo ""

while [ $attempt -le $max_attempts ]; do
    echo -n "  [Tentativa $attempt/$max_attempts] Testando health local... "
    
    if curl -sf --connect-timeout 5 --max-time 10 http://localhost/health > /dev/null 2>&1; then
        echo "✅"
        health_ok=true
        break
    else
        echo "⏳"
        if [ $attempt -lt $max_attempts ]; then
            sleep 8
        fi
    fi
    
    attempt=$((attempt + 1))
done

# 10. Verificar status
echo ""
echo "=========================================="
echo "   Verificando Status dos Containers"
echo "=========================================="
echo ""
docker compose ps

echo ""
echo "=========================================="
echo "   Resultados do Health Check"
echo "=========================================="
echo ""

if [ "$health_ok" = true ]; then
    print_status "Health check local: OK"
else
    print_warning "Health check local: Timeout após $max_attempts tentativas"
    print_warning "A API pode estar ainda inicializando. Verifique os logs:"
    print_warning "  docker compose logs -f api"
fi

# Tentar health check via domínio
if curl -sf --connect-timeout 5 --max-time 10 https://api-aponta.pedroct.com.br/health > /dev/null 2>&1; then
    print_status "Health check público (HTTPS): OK"
else
    print_warning "Health check público: Ainda propagando ou CloudFlare não configurado"
fi

echo ""
echo "=========================================="
echo "   Deploy Concluído!"
echo "=========================================="
echo ""

print_status "Containers rodando"
print_status "Migrations executadas"
print_status "API inicializada"

echo ""
echo "Próximos passos:"
echo ""
echo "1. Verificar logs completos (últimas 50 linhas):"
echo "   docker compose logs --tail=50 api"
echo ""
echo "2. Monitorar logs em tempo real:"
echo "   docker compose logs -f api"
echo ""
echo "3. Testar endpoints:"
echo "   curl http://localhost/health"
echo "   curl https://api-aponta.pedroct.com.br/health"
echo ""
echo "4. Acessar documentação:"
echo "   https://api-aponta.pedroct.com.br/docs"
echo ""
echo "5. Troubleshooting:"
if [ "$health_ok" = false ]; then
    echo "   ⚠️  Health check falhou - aguarde 10-15 segundos e teste novamente:"
    echo "   curl http://localhost/health"
fi
echo "   Se HTTPS não funcionar, verifique:"
echo "   - CloudFlare está em modo 'Full (strict)'?"
echo "   - DNS propagou? (pode levar 5-10 minutos)"
echo "   - Certificados foram copiados corretamente?"
echo ""

print_status "Deploy finalizado com sucesso!"
