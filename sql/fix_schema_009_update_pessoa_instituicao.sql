-- Migration 009: Corrigir schema de cadastro.pessoa e cadastro.instituicao
-- Data: 04/11/2025
-- Objetivo: Adicionar colunas faltantes e sincronizar com novo schema

-- 1. Verificar se as colunas já existem antes de adicionar
-- Para cadastro.pessoa:
ALTER TABLE cadastro.pessoa
    ADD COLUMN
IF NOT EXISTS nome_completo TEXT,
ADD COLUMN
IF NOT EXISTS cpf TEXT UNIQUE,
ADD COLUMN
IF NOT EXISTS instituicao_id UUID REFERENCES cadastro.instituicao
(id) ON
DELETE
SET NULL
,
ADD COLUMN
IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Fazer migration de dados: se 'nome' existe e 'nome_completo' não, copiar
DO $$
BEGIN
    IF EXISTS (SELECT 1
    FROM information_schema.columns
    WHERE table_name='pessoa' AND column_name='nome' AND table_schema='cadastro') THEN
    IF NOT EXISTS (SELECT 1
    FROM information_schema.columns
    WHERE table_name='pessoa' AND column_name='nome_completo' AND table_schema='cadastro') THEN
    UPDATE cadastro.pessoa SET nome_completo = nome WHERE nome_completo IS NULL;
END
IF;
    END
IF;
END $$;

-- 2. Para cadastro.instituicao, adicionar colunas faltantes:
ALTER TABLE cadastro.instituicao
    ADD COLUMN
IF NOT EXISTS nome_fantasia TEXT,
ADD COLUMN
IF NOT EXISTS email TEXT UNIQUE,
ADD COLUMN
IF NOT EXISTS telefone TEXT,
ADD COLUMN
IF NOT EXISTS telefone_secundario TEXT,
ADD COLUMN
IF NOT EXISTS site TEXT,
ADD COLUMN
IF NOT EXISTS created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- 3. Adicionar índices se não existirem
CREATE INDEX
IF NOT EXISTS idx_pessoa_cpf ON cadastro.pessoa
(cpf);
CREATE INDEX
IF NOT EXISTS idx_pessoa_email ON cadastro.pessoa
(email);
CREATE INDEX
IF NOT EXISTS idx_instituicao_cnpj ON cadastro.instituicao
(cnpj);
CREATE INDEX
IF NOT EXISTS idx_instituicao_email ON cadastro.instituicao
(email);
