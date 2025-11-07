-- =============================================================================
-- Migration 005: Adicionar campos profissionais em usuarios.usuario
-- Data: 2025-11-03
-- Descrição: Adiciona campos para telefone institucional e email institucional
--            na tabela usuario (já possui pessoa_id e instituicao_id)
-- =============================================================================

-- Adicionar coluna email_institucional
ALTER TABLE usuarios.usuario
ADD COLUMN
IF NOT EXISTS email_institucional TEXT;

COMMENT ON COLUMN usuarios.usuario.email_institucional IS
'Email institucional do usuário (diferente do email de login)';

-- Adicionar coluna telefone_institucional
ALTER TABLE usuarios.usuario
ADD COLUMN
IF NOT EXISTS telefone_institucional TEXT;

COMMENT ON COLUMN usuarios.usuario.telefone_institucional IS
'Telefone institucional do usuário';

-- Criar índice no email_institucional para facilitar buscas
CREATE INDEX
IF NOT EXISTS idx_usuario_email_institucional
ON usuarios.usuario
(email_institucional);

-- Verificar estrutura atualizada
\echo 'Migration 005 aplicada com sucesso!'
\echo 'Novos campos adicionados à tabela usuarios.usuario:'
\echo '  - email_institucional (TEXT)'
\echo '  - telefone_institucional (TEXT)'
\echo ''
\echo 'Campos já existentes (migration 004):'
\echo '  - pessoa_id (UUID, FK para usuarios.pessoa - pessoa física)'
\echo '  - instituicao_id (UUID, FK para cadastro.instituicao - pessoa jurídica)'
