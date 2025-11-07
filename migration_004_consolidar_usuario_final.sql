-- =================================================================
-- Migration 004: Consolidar usuarios.conta_usuario em usuarios.usuario
-- =================================================================
-- Objetivo: Unificar autenticacao em uma tabela usuarios.usuario com FK para pessoa e instituicao
-- Data: 2025-01-XX
-- Autor: Sistema SIGMA-PLI
-- =================================================================

BEGIN;

-- =================================================================
-- PASSO 1: Renomear usuarios.usuario -> usuario_legacy (backup)
-- =================================================================
ALTER TABLE usuarios.usuario RENAME TO usuario_legacy;
ALTER TABLE usuarios.usuario_papel RENAME TO usuario_papel_legacy;

-- Renomear indexes da tabela usuario
ALTER INDEX usuarios.usuario_pkey RENAME TO usuario_legacy_pkey;
ALTER INDEX usuarios.usuario_username_key RENAME TO usuario_legacy_username_key;
ALTER INDEX usuarios.usuario_email_key RENAME TO usuario_legacy_email_key;
ALTER INDEX usuarios.idx_usuario_ativo RENAME TO idx_usuario_legacy_ativo;
ALTER INDEX usuarios.idx_usuario_email RENAME TO idx_usuario_legacy_email;
ALTER INDEX usuarios.idx_usuario_username RENAME TO idx_usuario_legacy_username;

-- =================================================================
-- PASSO 2: Renomear usuarios.conta_usuario -> usuarios.usuario
-- =================================================================
ALTER TABLE usuarios.conta_usuario RENAME TO usuario;

-- Renomear indexes
ALTER INDEX usuarios.conta_usuario_pkey RENAME TO usuario_pkey;
ALTER INDEX usuarios.conta_usuario_username_key RENAME TO usuario_username_key;
ALTER INDEX usuarios.conta_usuario_email_key RENAME TO usuario_email_key;
ALTER INDEX usuarios.idx_conta_usuario_pessoa RENAME TO idx_usuario_pessoa;
ALTER INDEX usuarios.idx_conta_usuario_ativo RENAME TO idx_usuario_ativo;
ALTER INDEX usuarios.idx_conta_usuario_email RENAME TO idx_usuario_email;
ALTER INDEX usuarios.idx_conta_usuario_username RENAME TO idx_usuario_username;

-- Renomear triggers
ALTER TRIGGER trigger_auditoria_conta_usuario ON usuarios.usuario RENAME TO trigger_auditoria_usuario;
ALTER TRIGGER trigger_update_conta_usuario_updated_at ON usuarios.usuario RENAME TO trigger_update_usuario_updated_at;

-- =================================================================
-- PASSO 3: Adicionar instituicao_id em usuarios.usuario
-- =================================================================
ALTER TABLE usuarios.usuario 
ADD COLUMN instituicao_id UUID REFERENCES cadastro.instituicao(id) ON DELETE SET NULL;

CREATE INDEX idx_usuario_instituicao ON usuarios.usuario(instituicao_id);

COMMENT ON COLUMN usuarios.usuario.instituicao_id IS 'FK para instituicao associada ao usuario';

-- =================================================================
-- PASSO 4: Atualizar usuarios.sessao (conta_usuario_id -> usuario_id)
-- =================================================================
ALTER TABLE usuarios.sessao 
DROP CONSTRAINT sessao_conta_usuario_id_fkey;

ALTER TABLE usuarios.sessao 
RENAME COLUMN conta_usuario_id TO usuario_id;

ALTER TABLE usuarios.sessao 
ADD CONSTRAINT sessao_usuario_id_fkey 
FOREIGN KEY (usuario_id) REFERENCES usuarios.usuario(id) ON DELETE CASCADE;

CREATE INDEX idx_sessao_usuario ON usuarios.sessao(usuario_id);

-- =================================================================
-- PASSO 5: Atualizar usuarios.tentativa_login
-- =================================================================
ALTER TABLE usuarios.tentativa_login 
DROP CONSTRAINT tentativa_login_conta_usuario_id_fkey;

ALTER TABLE usuarios.tentativa_login 
RENAME COLUMN conta_usuario_id TO usuario_id;

ALTER TABLE usuarios.tentativa_login 
ADD CONSTRAINT tentativa_login_usuario_id_fkey 
FOREIGN KEY (usuario_id) REFERENCES usuarios.usuario(id) ON DELETE CASCADE;

CREATE INDEX idx_tentativa_login_usuario ON usuarios.tentativa_login(usuario_id);

-- =================================================================
-- PASSO 6: Atualizar usuarios.token_recuperacao
-- =================================================================
ALTER TABLE usuarios.token_recuperacao 
DROP CONSTRAINT token_recuperacao_conta_usuario_id_fkey;

ALTER TABLE usuarios.token_recuperacao 
RENAME COLUMN conta_usuario_id TO usuario_id;

ALTER TABLE usuarios.token_recuperacao 
ADD CONSTRAINT token_recuperacao_usuario_id_fkey 
FOREIGN KEY (usuario_id) REFERENCES usuarios.usuario(id) ON DELETE CASCADE;

CREATE INDEX idx_token_recuperacao_usuario ON usuarios.token_recuperacao(usuario_id);

-- =================================================================
-- PASSO 7: Atualizar tabelas que referenciam usuario_legacy
-- =================================================================
-- auditoria_login
ALTER TABLE usuarios.auditoria_login 
DROP CONSTRAINT auditoria_login_usuario_id_fkey;

ALTER TABLE usuarios.auditoria_login 
ADD CONSTRAINT auditoria_login_usuario_id_fkey 
FOREIGN KEY (usuario_id) REFERENCES usuarios.usuario(id) ON DELETE SET NULL;

-- evento
ALTER TABLE usuarios.evento 
DROP CONSTRAINT evento_usuario_id_fkey;

ALTER TABLE usuarios.evento 
ADD CONSTRAINT evento_usuario_id_fkey 
FOREIGN KEY (usuario_id) REFERENCES usuarios.usuario(id) ON DELETE CASCADE;

-- homeoffice
ALTER TABLE usuarios.homeoffice 
DROP CONSTRAINT homeoffice_usuario_id_fkey;

ALTER TABLE usuarios.homeoffice 
ADD CONSTRAINT homeoffice_usuario_id_fkey 
FOREIGN KEY (usuario_id) REFERENCES usuarios.usuario(id) ON DELETE CASCADE;

-- tarefa
ALTER TABLE usuarios.tarefa 
DROP CONSTRAINT tarefa_usuario_id_fkey;

ALTER TABLE usuarios.tarefa 
ADD CONSTRAINT tarefa_usuario_id_fkey 
FOREIGN KEY (usuario_id) REFERENCES usuarios.usuario(id) ON DELETE CASCADE;

-- =================================================================
-- PASSO 8: Remover tabelas legacy
-- =================================================================
DROP TABLE IF EXISTS usuarios.usuario_papel_legacy CASCADE;
DROP TABLE IF EXISTS usuarios.usuario_legacy CASCADE;

-- =================================================================
-- PASSO 9: Criar nova usuarios.usuario_papel
-- =================================================================
CREATE TABLE usuarios.usuario_papel (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID NOT NULL REFERENCES usuarios.usuario(id) ON DELETE CASCADE,
    papel_id UUID NOT NULL REFERENCES usuarios.papel(id) ON DELETE CASCADE,
    atribuido_por UUID REFERENCES usuarios.usuario(id) ON DELETE SET NULL,
    atribuido_em TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(usuario_id, papel_id)
);

CREATE INDEX idx_usuario_papel_usuario ON usuarios.usuario_papel(usuario_id);
CREATE INDEX idx_usuario_papel_papel ON usuarios.usuario_papel(papel_id);

COMMENT ON TABLE usuarios.usuario_papel IS 'Associacao entre usuarios e papeis (nova estrutura)';
COMMENT ON COLUMN usuarios.usuario_papel.usuario_id IS 'FK para usuarios.usuario (consolidada)';
COMMENT ON COLUMN usuarios.usuario_papel.papel_id IS 'FK para papel';
COMMENT ON COLUMN usuarios.usuario_papel.atribuido_por IS 'Usuario que atribuiu o papel';

-- =================================================================
-- VERIFICACAO FINAL
-- =================================================================
DO $$
DECLARE
    v_usuario_count INTEGER;
    v_sessao_count INTEGER;
    v_usuario_papel_count INTEGER;
BEGIN
    -- Contar usuarios
    SELECT COUNT(*) INTO v_usuario_count FROM usuarios.usuario;
    RAISE NOTICE 'Total de usuarios apos migracao: %', v_usuario_count;
    
    -- Contar sessoes
    SELECT COUNT(*) INTO v_sessao_count FROM usuarios.sessao;
    RAISE NOTICE 'Total de sessoes apos migracao: %', v_sessao_count;
    
    -- Contar usuario_papel
    SELECT COUNT(*) INTO v_usuario_papel_count FROM usuarios.usuario_papel;
    RAISE NOTICE 'Total de usuario_papel apos migracao: %', v_usuario_papel_count;
    
    -- Verificar se instituicao_id existe
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'usuarios' 
        AND table_name = 'usuario' 
        AND column_name = 'instituicao_id'
    ) THEN
        RAISE NOTICE 'Campo instituicao_id criado com sucesso';
    ELSE
        RAISE EXCEPTION 'ERRO: Campo instituicao_id nao foi criado';
    END IF;
    
    RAISE NOTICE '=== MIGRACAO CONCLUIDA COM SUCESSO ===';
END $$;

COMMIT;
