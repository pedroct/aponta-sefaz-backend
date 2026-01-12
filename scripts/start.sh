#!/bin/sh
set -e

# Executa migrações do banco de dados
echo "🚀 Iniciando migrações do banco de dados..."
alembic upgrade head

# Inicia a aplicação
echo "🟢 Iniciando a API Aponta..."
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
