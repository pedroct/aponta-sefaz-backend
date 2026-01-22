-- Script de inicialização do banco de dados local
-- Cria schemas para staging e produção

-- Schema de Produção
CREATE SCHEMA IF NOT EXISTS aponta_sefaz;
GRANT ALL ON SCHEMA aponta_sefaz TO "api-aponta-user";
GRANT ALL ON ALL TABLES IN SCHEMA aponta_sefaz TO "api-aponta-user";
GRANT ALL ON ALL SEQUENCES IN SCHEMA aponta_sefaz TO "api-aponta-user";

-- Schema de Staging
CREATE SCHEMA IF NOT EXISTS aponta_sefaz_staging;
GRANT ALL ON SCHEMA aponta_sefaz_staging TO "api-aponta-user";
GRANT ALL ON ALL TABLES IN SCHEMA aponta_sefaz_staging TO "api-aponta-user";
GRANT ALL ON ALL SEQUENCES IN SCHEMA aponta_sefaz_staging TO "api-aponta-user";

-- Remover schemas antigos se existirem
DROP SCHEMA IF EXISTS api_aponta CASCADE;
DROP SCHEMA IF EXISTS api_aponta_staging CASCADE;

-- Define o search_path padrão para produção
ALTER DATABASE gestao_projetos SET search_path TO aponta_sefaz;
