-- Script de inicialização do banco de dados local
-- Cria o schema api_aponta se não existir

CREATE SCHEMA IF NOT EXISTS api_aponta;

-- Concede permissões ao usuário
GRANT ALL ON SCHEMA api_aponta TO "api-aponta-user";
GRANT ALL ON ALL TABLES IN SCHEMA api_aponta TO "api-aponta-user";
GRANT ALL ON ALL SEQUENCES IN SCHEMA api_aponta TO "api-aponta-user";

-- Define o search_path padrão
ALTER DATABASE gestao_projetos SET search_path TO api_aponta, public;
