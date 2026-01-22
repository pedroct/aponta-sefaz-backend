#!/bin/bash
# Script de Fix - Resolve o problema de tabelas faltando em staging
# Este script cria as tabelas diretamente no banco de dados

set -e

echo "🔧 Iniciando Fix para tabelas faltando em api_aponta_staging..."
echo ""

# Conectar ao container do banco e criar as tabelas manualmente
docker compose exec -T db psql -U postgres -d api_aponta_staging << 'SQLEOF'

-- 1. Criar tabela apontamentos
CREATE TABLE IF NOT EXISTS api_aponta_staging.apontamentos (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    work_item_id INTEGER NOT NULL,
    project_id VARCHAR(255) NOT NULL,
    organization_name VARCHAR(255) NOT NULL,
    data_apontamento DATE NOT NULL,
    duracao VARCHAR(5),
    horas INTEGER,
    minutos INTEGER,
    id_atividade UUID NOT NULL REFERENCES api_aponta_staging.atividades(id) ON DELETE RESTRICT,
    comentario VARCHAR(100),
    usuario_id VARCHAR(255) NOT NULL,
    usuario_nome VARCHAR(255) NOT NULL,
    usuario_email VARCHAR(255),
    criado_em TIMESTAMP DEFAULT NOW() NOT NULL,
    atualizado_em TIMESTAMP DEFAULT NOW() NOT NULL
);

-- 2. Criar índices para apontamentos
CREATE INDEX IF NOT EXISTS ix_api_aponta_apontamentos_id ON api_aponta_staging.apontamentos(id);
CREATE INDEX IF NOT EXISTS ix_api_aponta_apontamentos_work_item_id ON api_aponta_staging.apontamentos(work_item_id);
CREATE INDEX IF NOT EXISTS ix_api_aponta_apontamentos_project_id ON api_aponta_staging.apontamentos(project_id);
CREATE INDEX IF NOT EXISTS ix_api_aponta_apontamentos_organization_name ON api_aponta_staging.apontamentos(organization_name);
CREATE INDEX IF NOT EXISTS ix_api_aponta_apontamentos_data_apontamento ON api_aponta_staging.apontamentos(data_apontamento);
CREATE INDEX IF NOT EXISTS ix_api_aponta_apontamentos_id_atividade ON api_aponta_staging.apontamentos(id_atividade);
CREATE INDEX IF NOT EXISTS ix_api_aponta_apontamentos_usuario_id ON api_aponta_staging.apontamentos(usuario_id);
CREATE INDEX IF NOT EXISTS ix_api_aponta_apontamentos_work_item_org_project ON api_aponta_staging.apontamentos(work_item_id, organization_name, project_id);

-- 3. Registrar as migrações no histórico do Alembic (para que não tente criar novamente)
INSERT INTO alembic_version (version_num) VALUES ('c3d4e5f6g7h8') ON CONFLICT DO NOTHING;
INSERT INTO alembic_version (version_num) VALUES ('d4e5f6g7h8i9') ON CONFLICT DO NOTHING;

-- 4. Listar tabelas criadas
SELECT table_name FROM information_schema.tables WHERE table_schema = 'api_aponta_staging' ORDER BY table_name;

SQLEOF

echo ""
echo "✅ Tabelas criadas com sucesso!"
echo ""
echo "🔍 Verificando estrutura..."

docker compose exec -T api psql -U postgres -d api_aponta_staging -c "\dt+ api_aponta_staging.apontamentos"

echo ""
echo "🧪 Testando conexão com a API..."
sleep 2
curl -f http://localhost/health && echo "" || echo "⚠️  Health check falhou"

echo ""
echo "✅ Fix concluído! A tabela apontamentos agora existe."
