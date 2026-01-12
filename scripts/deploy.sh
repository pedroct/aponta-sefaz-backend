#!/bin/bash
# Script de deploy para VPS Hostinger
# Uso: ./scripts/deploy.sh

set -e

echo "==================================="
echo "   Deploy API Aponta - Hostinger   "
echo "==================================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verifica se .env existe
if [ ! -f .env ]; then
    echo -e "${RED}Erro: Arquivo .env nao encontrado!${NC}"
    echo "Copie .env.example para .env e configure as variaveis."
    exit 1
fi

echo -e "${YELLOW}Parando containers existentes...${NC}"
docker compose down --remove-orphans 2>/dev/null || true

echo -e "${YELLOW}Construindo imagens...${NC}"
docker compose build --no-cache

echo -e "${YELLOW}Iniciando containers...${NC}"
docker compose up -d

echo -e "${YELLOW}Aguardando containers iniciarem...${NC}"
sleep 10

# Verifica status dos containers
echo -e "${YELLOW}Verificando status dos containers...${NC}"
docker compose ps

# Verifica health da API
echo -e "${YELLOW}Verificando health da API...${NC}"
if curl -sf http://localhost/health > /dev/null 2>&1; then
    echo -e "${GREEN}API esta funcionando!${NC}"
else
    echo -e "${YELLOW}API ainda iniciando ou endpoint /health nao disponivel${NC}"
fi

echo ""
echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}   Deploy concluido com sucesso!  ${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""
echo "Comandos uteis:"
echo "  docker compose logs -f    # Ver logs"
echo "  docker compose ps         # Status dos containers"
echo "  docker compose restart    # Reiniciar"
echo "  docker compose down       # Parar tudo"
