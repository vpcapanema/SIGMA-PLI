-- Migration 008: Adicionar colunas relacionais opcionais em cadastro.pessoa (idempotente)
ALTER TABLE
IF EXISTS cadastro.pessoa
ADD COLUMN
IF NOT EXISTS instituicao_id UUID;

ALTER TABLE
IF EXISTS cadastro.pessoa
ADD COLUMN
IF NOT EXISTS departamento_id UUID;
