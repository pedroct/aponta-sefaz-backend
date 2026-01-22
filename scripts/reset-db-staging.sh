#!/bin/bash
# Script para resetar banco de dados e executar migrations corretamente

set -e

echo "📋 Resetando banco de dados para staging..."

# Conectar ao postgres e dropar o schema staging (se existir)
psql -h ${DATABASE_HOST:-postgres-aponta} \
     -U ${DATABASE_USER:-api-aponta-user} \
     -d ${DATABASE_NAME:-gestao_projetos} \
     -c "DROP SCHEMA IF EXISTS ${DATABASE_SCHEMA:-aponta_sefaz_staging} CASCADE;" || echo "⚠️  Schema não existia"

echo "✅ Schema removido (se existia)"

# Executar migrations (isso vai recriar o schema e as tabelas)
echo "🚀 Executando migrations..."
alembic upgrade head

echo "✅ Migrations concluídas com sucesso!"

# Verificar se as tabelas foram criadas
echo "📊 Verificando tabelas criadas..."
psql -h ${DATABASE_HOST:-postgres-aponta} \
     -U ${DATABASE_USER:-api-aponta-user} \
     -d ${DATABASE_NAME:-gestao_projetos} \
     -c "\dt ${DATABASE_SCHEMA:-aponta_sefaz_staging}.*"

echo "✅ Reset concluído!"
