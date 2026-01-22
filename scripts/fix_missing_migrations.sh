#!/bin/bash
# Script para corrigir o problema de migrações faltando em staging
# Este script marca as migrações faltando como já executadas

set -e

echo "🔧 Corrigindo migrações faltando em staging..."
echo ""

# Conectar ao banco de dados e inserir as migrações no histórico
docker compose exec -T db psql -U postgres -d api_aponta_staging << 'EOF'

-- Ver histórico atual
SELECT * FROM alembic_version;

-- Inserir migração c3d4e5f6g7h8 (create_apontamentos_table)
INSERT INTO alembic_version (version_num) VALUES ('c3d4e5f6g7h8');

-- Inserir migração d4e5f6g7h8i9 (alter_apontamentos_duracao)
INSERT INTO alembic_version (version_num) VALUES ('d4e5f6g7h8i9');

-- Ver histórico após inserção
SELECT * FROM alembic_version;

EOF

echo ""
echo "✅ Migrações registradas no histórico"
echo ""
echo "🚀 Executando migrações..."
docker compose exec -T api alembic upgrade head

echo ""
echo "✅ Migrações aplicadas com sucesso!"
echo ""
echo "🔍 Verificando histórico final..."
docker compose exec -T api alembic history --verbose

echo ""
echo "✅ Problema resolvido!"
