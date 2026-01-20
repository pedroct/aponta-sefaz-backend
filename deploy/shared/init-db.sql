-- Inicialização do banco de dados
-- Cria os schemas para produção e staging

-- Schema de produção
CREATE SCHEMA IF NOT EXISTS aponta_sefaz;

-- Schema de staging/homologação
CREATE SCHEMA IF NOT EXISTS aponta_sefaz_staging;

-- Garantir permissões
GRANT ALL PRIVILEGES ON SCHEMA aponta_sefaz TO aponta_user;
GRANT ALL PRIVILEGES ON SCHEMA aponta_sefaz_staging TO aponta_user;

-- Comentários
COMMENT ON SCHEMA aponta_sefaz IS 'Schema de produção - aponta.treit.com.br';
COMMENT ON SCHEMA aponta_sefaz_staging IS 'Schema de homologação - staging-aponta.treit.com.br';
