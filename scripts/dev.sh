#!/bin/bash
# ===========================================
# Script de Desenvolvimento Local
# Uso: ./scripts/dev.sh [start|stop|restart|status]
# ===========================================

set -e

COMPOSE_FILE="docker-compose.local.yml"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

stop_server() {
    echo -e "${YELLOW}Parando ambiente Docker...${NC}"
    docker compose -f "$COMPOSE_FILE" down
    echo -e "${GREEN}Ambiente Docker parado${NC}"
}

start_server() {
    echo -e "${YELLOW}Iniciando ambiente Docker...${NC}"

    if [ ! -f ".env" ]; then
        echo -e "${RED}Erro: arquivo .env não encontrado${NC}"
        echo "Copie .env.local para .env ou crie um arquivo .env"
        exit 1
    fi

    docker compose -f "$COMPOSE_FILE" up -d --build

    echo -e "${GREEN}Ambiente Docker iniciado com sucesso!${NC}"
    echo "  - Docs: http://localhost:8000/docs"
    echo "  - API:  http://localhost:8000/api/v1"
}

status_server() {
    docker compose -f "$COMPOSE_FILE" ps
}

case "${1:-start}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        stop_server
        start_server
        ;;
    status)
        status_server
        ;;
    *)
        echo "Uso: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
