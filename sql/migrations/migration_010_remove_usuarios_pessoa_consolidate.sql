-- Migration 010: Remover tabela usuarios.pessoa e consolidar em cadastro.pessoa
-- Objetivo: eliminar duplicação - usuarios.usuario aponta para cadastro.pessoa

BEGIN;

    -- Remover a tabela usuarios.pessoa (se existir)
    DROP TABLE IF EXISTS usuarios.pessoa
    CASCADE;

-- Criar índices úteis em cadastro.pessoa
CREATE INDEX
IF NOT EXISTS idx_cadastro_pessoa_cpf ON cadastro.pessoa
(cpf);
CREATE INDEX
IF NOT EXISTS idx_cadastro_pessoa_email ON cadastro.pessoa
(email);
CREATE INDEX
IF NOT EXISTS idx_cadastro_pessoa_instituicao_id ON cadastro.pessoa
(instituicao_id);

-- Criar índices úteis em cadastro.instituicao
CREATE INDEX
IF NOT EXISTS idx_cadastro_instituicao_cnpj ON cadastro.instituicao
(cnpj);
CREATE INDEX
IF NOT EXISTS idx_cadastro_instituicao_email ON cadastro.instituicao
(email);

COMMIT;
