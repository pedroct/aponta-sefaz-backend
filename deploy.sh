#!/bin/bash
# =============================================================================
# Script de Deploy - Aponta SEFAZ
# Uso: ./deploy.sh [staging|production|all]
# =============================================================================

set -e

# Configurações
VPS_HOST="92.112.178.252"
VPS_USER="root"
REMOTE_BASE="/home/ubuntu/aponta-sefaz"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções de log
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Banner
show_banner() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║           APONTA SEFAZ - Deploy Script                        ║"
    echo "║           VPS: $VPS_HOST                               ║"
    echo "╚═══════════════════════════════════════════════════════════════╝"
    echo ""
}

# Verificar ambiente
check_env() {
    local env=$1
    if [[ "$env" != "staging" && "$env" != "production" && "$env" != "all" ]]; then
        log_error "Ambiente inválido: $env"
        echo "Uso: ./deploy.sh [staging|production|all]"
        exit 1
    fi
}

# Rodar testes
run_tests() {
    log_info "Executando testes..."
    if pytest tests/ -v --tb=short; then
        log_success "Testes passaram!"
    else
        log_error "Testes falharam!"
        read -p "Continuar mesmo assim? (y/N): " confirm
        if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
            exit 1
        fi
    fi
}

# Criar pacote do backend
create_package() {
    log_info "Criando pacote do backend..."
    tar --exclude='node_modules' \
        --exclude='.git' \
        --exclude='dist' \
        --exclude='__pycache__' \
        --exclude='.venv' \
        --exclude='venv' \
        --exclude='.pytest_cache' \
        --exclude='htmlcov' \
        --exclude='*.pyc' \
        --exclude='deploy' \
        --exclude='.env' \
        -czvf /tmp/backend.tar.gz -C . .
    log_success "Pacote criado: /tmp/backend.tar.gz"
}

# Deploy para um ambiente
deploy_env() {
    local env=$1
    local remote_path="${REMOTE_BASE}/${env}/backend"
    
    log_info "Deployando para ${env}..."
    
    # Enviar pacote
    log_info "Enviando arquivos para ${env}..."
    scp /tmp/backend.tar.gz ${VPS_USER}@${VPS_HOST}:/tmp/backend_${env}.tar.gz
    
    # Extrair e reiniciar
    ssh ${VPS_USER}@${VPS_HOST} << EOF
        set -e
        echo "Extraindo backend para ${env}..."
        cd ${remote_path}
        tar -xzf /tmp/backend_${env}.tar.gz
        rm /tmp/backend_${env}.tar.gz
        
        echo "Reiniciando containers de ${env}..."
        cd ${REMOTE_BASE}/${env}
        docker compose down
        docker compose up -d
        
        echo "Aguardando inicialização (pode levar até 40 segundos)..."
        
        # Health check com retry logic
        max_attempts=5
        attempt=1
        health_ok=false
        
        echo ""
        echo "Testando health check com retry logic:"
        
        while [ $attempt -le $max_attempts ]; do
            echo -n "  [Tentativa $attempt/$max_attempts] "
            
            if [ "${env}" = "production" ]; then
                if curl -sf --connect-timeout 5 --max-time 10 http://localhost/api/v1 > /dev/null 2>&1; then
                    echo "✅ API respondendo"
                    health_ok=true
                    break
                else
                    echo "⏳ Aguardando..."
                fi
            else
                if curl -sf --connect-timeout 5 --max-time 10 -H "Host: staging-aponta.treit.com.br" http://localhost/api/v1 > /dev/null 2>&1; then
                    echo "✅ API respondendo"
                    health_ok=true
                    break
                else
                    echo "⏳ Aguardando..."
                fi
            fi
            
            if [ $attempt -lt $max_attempts ]; then
                sleep 8
            fi
            
            attempt=$((attempt + 1))
        done
        
        if [ "$health_ok" = true ]; then
            echo ""
            echo "${env} - Health check OK!"
        else
            echo ""
            echo "Aviso: Timeout no health check após $max_attempts tentativas."
            echo "A API pode estar ainda inicializando. Verifique os logs:"
            echo "  docker compose logs -f api"
        fi
EOF
    
    log_success "Deploy para ${env} concluído!"
}

# Health check com retry logic
health_check() {
    local env=$1
    log_info "Verificando saúde de ${env}..."
    
    max_attempts=3
    attempt=1
    health_ok=false
    
    while [ $attempt -le $max_attempts ]; do
        if [[ "$env" == "production" ]]; then
            if curl -sf --connect-timeout 5 --max-time 10 http://aponta.treit.com.br/api/v1 > /dev/null 2>&1; then
                log_success "Produção está saudável!"
                health_ok=true
                break
            fi
        else
            if curl -sf --connect-timeout 5 --max-time 10 http://staging-aponta.treit.com.br/api/v1 > /dev/null 2>&1; then
                log_success "Staging está saudável!"
                health_ok=true
                break
            fi
        fi
        
        if [ $attempt -lt $max_attempts ]; then
            sleep 5
        fi
        attempt=$((attempt + 1))
    done
    
    if [ "$health_ok" = false ]; then
        log_warn "${env} pode estar com problemas (tentativas esgotadas)"
    fi
}

# Main
main() {
    local env=${1:-"staging"}
    
    show_banner
    check_env "$env"
    
    echo "Ambiente selecionado: $env"
    echo ""
    
    # Confirmação para produção
    if [[ "$env" == "production" || "$env" == "all" ]]; then
        log_warn "⚠️  ATENÇÃO: Deploy para PRODUÇÃO!"
        read -p "Tem certeza que deseja continuar? (y/N): " confirm
        if [[ "$confirm" != "y" && "$confirm" != "Y" ]]; then
            log_info "Deploy cancelado."
            exit 0
        fi
    fi
    
    # Rodar testes
    run_tests
    
    # Criar pacote
    create_package
    
    # Deploy
    if [[ "$env" == "all" ]]; then
        deploy_env "staging"
        deploy_env "production"
        health_check "staging"
        health_check "production"
    else
        deploy_env "$env"
        health_check "$env"
    fi
    
    # Limpar
    rm -f /tmp/backend.tar.gz
    
    echo ""
    log_success "🎉 Deploy finalizado com sucesso!"
    echo ""
}

# Executar
main "$@"
