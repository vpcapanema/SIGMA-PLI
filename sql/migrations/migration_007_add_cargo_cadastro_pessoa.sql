-- Migration 007: Adicionar coluna 'cargo' na tabela cadastro.pessoa (idempotente)
-- Versão simples e compatível: usa IF NOT EXISTS diretamente
ALTER TABLE
IF EXISTS cadastro.pessoa
ADD COLUMN
IF NOT EXISTS cargo VARCHAR
(200);
