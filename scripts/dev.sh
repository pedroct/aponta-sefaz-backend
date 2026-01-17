#!/bin/bash
# ===========================================
# Script de Desenvolvimento Local
# Uso: ./scripts/dev.sh [start|stop|restart|status]
# ===========================================

set -e

PORT=8000
PID_FILE=".dev.pid"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

stop_server() {
    echo -e "${YELLOW}Parando servidor...${NC}"

    # Kill by PID file
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID" 2>/dev/null || true
            echo "Processo $PID finalizado"
        fi
        rm -f "$PID_FILE"
    fi

    # Kill any remaining processes on port
    if command -v lsof &> /dev/null; then
        lsof -ti:$PORT | xargs kill -9 2>/dev/null || true
    elif command -v netstat &> /dev/null; then
        # Windows/WSL fallback
        netstat -ano 2>/dev/null | grep ":$PORT" | grep LISTENING | awk '{print $5}' | while read pid; do
            taskkill //F //PID "$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null || true
        done
    fi

    # Kill Python processes running uvicorn
    pkill -f "uvicorn app.main:app" 2>/dev/null || true

    echo -e "${GREEN}Servidor parado${NC}"
}

clear_cache() {
    echo -e "${YELLOW}Limpando cache Python...${NC}"
    find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    echo -e "${GREEN}Cache limpo${NC}"
}

start_server() {
    echo -e "${YELLOW}Iniciando servidor de desenvolvimento...${NC}"

    # Check if .env exists
    if [ ! -f ".env" ]; then
        echo -e "${RED}Erro: arquivo .env não encontrado${NC}"
        echo "Copie .env.local para .env ou crie um arquivo .env"
        exit 1
    fi

    # Clear cache first
    clear_cache

    # Start uvicorn with reload
    python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT --reload &
    PID=$!
    echo $PID > "$PID_FILE"

    # Wait for startup
    echo -n "Aguardando servidor iniciar"
    for i in {1..30}; do
        if curl -s "http://localhost:$PORT/" > /dev/null 2>&1; then
            echo ""
            echo -e "${GREEN}Servidor iniciado com sucesso!${NC}"
            echo "  - Docs: http://localhost:$PORT/docs"
            echo "  - API:  http://localhost:$PORT/api/v1"
            echo "  - PID:  $PID"
            return 0
        fi
        echo -n "."
        sleep 1
    done

    echo ""
    echo -e "${RED}Erro: servidor não iniciou em 30 segundos${NC}"
    return 1
}

status_server() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            echo -e "${GREEN}Servidor rodando (PID: $PID)${NC}"
            echo "  - URL: http://localhost:$PORT"

            # Check if responding
            if curl -s "http://localhost:$PORT/" > /dev/null 2>&1; then
                echo -e "  - Status: ${GREEN}Respondendo${NC}"
            else
                echo -e "  - Status: ${YELLOW}Não respondendo${NC}"
            fi
            return 0
        fi
    fi

    echo -e "${YELLOW}Servidor não está rodando${NC}"
    return 1
}

case "${1:-start}" in
    start)
        stop_server
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
