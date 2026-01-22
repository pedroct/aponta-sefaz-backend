#!/bin/bash
# Script para migrar dados dos schemas antigos para os novos

set -e

echo "🔄 Iniciando migração de schemas..."

# Variáveis de conexão
HOST=${DATABASE_HOST:-postgres-aponta}
USER=${DATABASE_USER:-api-aponta-user}
DB=${DATABASE_NAME:-gestao_projetos}

# Conectar e executar migração
psql -h "$HOST" -U "$USER" -d "$DB" <<EOF

-- Migrar dados de api_aponta para aponta_sefaz (se existir)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'api_aponta') THEN
        -- Copiar dados
        CREATE SCHEMA IF NOT EXISTS aponta_sefaz;
        
        -- Copiar tabelas (se não existirem no novo schema)
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'aponta_sefaz' AND table_name = 'atividades') THEN
            BEGIN
                INSERT INTO aponta_sefaz.atividades SELECT * FROM api_aponta.atividades;
                INSERT INTO aponta_sefaz.projetos SELECT * FROM api_aponta.projetos;
                -- Copiar outras tabelas conforme necessário
                RAISE NOTICE 'Dados migrados de api_aponta para aponta_sefaz';
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'Aviso: % (pode já existir dados)', SQLERRM;
            END;
        END IF;
        
        -- Remover schema antigo
        DROP SCHEMA IF EXISTS api_aponta CASCADE;
        RAISE NOTICE 'Schema api_aponta removido';
    END IF;
END $$;

-- Migrar dados de api_aponta_staging para aponta_sefaz_staging (se existir)
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM information_schema.schemata WHERE schema_name = 'api_aponta_staging') THEN
        -- Copiar dados
        CREATE SCHEMA IF NOT EXISTS aponta_sefaz_staging;
        
        -- Copiar tabelas (se não existirem no novo schema)
        IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_schema = 'aponta_sefaz_staging' AND table_name = 'atividades') THEN
            BEGIN
                INSERT INTO aponta_sefaz_staging.atividades SELECT * FROM api_aponta_staging.atividades;
                INSERT INTO aponta_sefaz_staging.projetos SELECT * FROM api_aponta_staging.projetos;
                -- Copiar outras tabelas conforme necessário
                RAISE NOTICE 'Dados migrados de api_aponta_staging para aponta_sefaz_staging';
            EXCEPTION WHEN OTHERS THEN
                RAISE NOTICE 'Aviso: % (pode já existir dados)', SQLERRM;
            END;
        END IF;
        
        -- Remover schema antigo
        DROP SCHEMA IF EXISTS api_aponta_staging CASCADE;
        RAISE NOTICE 'Schema api_aponta_staging removido';
    END IF;
END $$;

-- Remover dados do schema public (se houver)
DO $$
DECLARE
    table_record RECORD;
BEGIN
    FOR table_record IN 
        SELECT tablename FROM pg_tables 
        WHERE schemaname = 'public' AND tablename NOT LIKE 'pg_%'
    LOOP
        EXECUTE 'DROP TABLE IF EXISTS public.' || quote_ident(table_record.tablename) || ' CASCADE';
        RAISE NOTICE 'Tabela removida de public: %', table_record.tablename;
    END LOOP;
END $$;

-- Definir search_path padrão
ALTER DATABASE gestao_projetos SET search_path TO aponta_sefaz, aponta_sefaz_staging;

-- Verificar resultado
\dt aponta_sefaz.*
\dt aponta_sefaz_staging.*
\dt public.*

RAISE NOTICE '✅ Migração concluída!';

EOF

echo "✅ Migração de schemas concluída!"
