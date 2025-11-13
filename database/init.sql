-- SIGMA-PLI - Inicialização do Banco de Dados PostgreSQL
-- Script executado automaticamente pelo Docker na primeira inicialização

-- Criar extensões úteis
CREATE EXTENSION
IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION
IF NOT EXISTS "pg_trgm";  -- Para busca de texto similar

-- Mensagem de sucesso
DO $$
BEGIN
    RAISE NOTICE '✅ Banco de dados SIGMA-PLI inicializado com sucesso!';
    RAISE NOTICE '📊 Database: sigma_pli_db';
    RAISE NOTICE '👤 User: sigma_user';
END $$;

-- Criar schema para o sistema (opcional, mas organizado)
CREATE SCHEMA
IF NOT EXISTS sigma;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA sigma TO sigma_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA sigma TO sigma_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA sigma TO sigma_user;

-- Configurar search_path padrão
ALTER DATABASE sigma_pli_db SET search_path
TO sigma, public;
