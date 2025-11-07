-- ============================================================================
-- MIGRATION 004: Consolidar usuarios.conta_usuario → usuarios.usuario
-- Data: 2025-11-03
-- Objetivo: Unificar estrutura de usuários (Pessoa + Instituição + Credenciais)
-- ============================================================================
-- Arquitetura Final:
--   usuarios.usuario = pessoa_id + instituicao_id + credenciais + auditoria
--   cadastro.pessoa = dados pessoais (CPF, nome, email, etc.)
--   cadastro.instituicao = dados organizacionais (CNPJ, razão social, etc.)
-- ============================================================================

BEGIN;

-- ============================================================================
-- PASSO 1: Backup da tabela antiga usuarios.usuario (legacy)
-- ============================================================================

-- 1.1: Renomear tabela antiga para backup
ALTER TABLE usuarios.usuario RENAME TO usuario_legacy;

-- 1.2: Renomear constraints e índices da tabela legacy
ALTER TABLE usuarios.usuario_legacy RENAME CONSTRAINT usuario_pkey TO usuario_legacy_pkey;
ALTER TABLE usuarios.usuario_legacy RENAME CONSTRAINT usuario_email_key TO usuario_legacy_email_key;
ALTER TABLE usuarios.usuario_legacy RENAME CONSTRAINT usuario_username_key TO usuario_legacy_username_key;

ALTER INDEX usuarios.idx_usuario_ativo RENAME TO idx_usuario_legacy_ativo;
ALTER INDEX usuarios.idx_usuario_email RENAME TO idx_usuario_legacy_email;
ALTER INDEX usuarios.idx_usuario_username RENAME TO idx_usuario_legacy_username;

RAISE NOTICE '✅ Tabela usuarios.usuario renomeada para usuario_legacy';

-- ============================================================================
-- PASSO 2: Renomear usuarios.conta_usuario → usuarios.usuario
-- ============================================================================

-- 2.1: Renomear tabela
ALTER TABLE usuarios.conta_usuario RENAME TO usuario;

-- 2.2: Renomear constraints
ALTER TABLE usuarios.usuario RENAME CONSTRAINT conta_usuario_pkey TO usuario_pkey;
ALTER TABLE usuarios.usuario RENAME CONSTRAINT conta_usuario_email_key TO usuario_email_key;
ALTER TABLE usuarios.usuario RENAME CONSTRAINT conta_usuario_username_key TO usuario_username_key;
ALTER TABLE usuarios.usuario RENAME CONSTRAINT conta_usuario_pessoa_id_fkey TO usuario_pessoa_id_fkey;

-- 2.3: Renomear índices
ALTER INDEX usuarios.idx_conta_usuario_ativo RENAME TO idx_usuario_ativo;
ALTER INDEX usuarios.idx_conta_usuario_email RENAME TO idx_usuario_email;
ALTER INDEX usuarios.idx_conta_usuario_pessoa RENAME TO idx_usuario_pessoa;
ALTER INDEX usuarios.idx_conta_usuario_username RENAME TO idx_usuario_username;

-- 2.4: Renomear triggers
ALTER TRIGGER trigger_auditoria_conta_usuario ON usuarios.usuario RENAME TO trigger_auditoria_usuario;
ALTER TRIGGER trigger_update_conta_usuario_updated_at ON usuarios.usuario RENAME TO trigger_update_usuario_updated_at;

RAISE NOTICE '✅ Tabela usuarios.conta_usuario renomeada para usuarios.usuario';

-- ============================================================================
-- PASSO 3: Adicionar campo instituicao_id em usuarios.usuario
-- ============================================================================

-- 3.1: Adicionar coluna instituicao_id
ALTER TABLE usuarios.usuario 
ADD COLUMN instituicao_id UUID;

-- 3.2: Copiar instituicao_id de cadastro.pessoa (se a pessoa já tiver)
UPDATE usuarios.usuario u
SET instituicao_id = p.instituicao_id
FROM cadastro.pessoa p
WHERE u.pessoa_id = p.id AND p.instituicao_id IS NOT NULL;

-- 3.3: Adicionar FK para cadastro.instituicao
ALTER TABLE usuarios.usuario 
ADD CONSTRAINT usuario_instituicao_id_fkey 
FOREIGN KEY (instituicao_id) REFERENCES cadastro.instituicao(id);

-- 3.4: Criar índice
CREATE INDEX idx_usuario_instituicao ON usuarios.usuario(instituicao_id);

-- 3.5: Comentário
COMMENT ON COLUMN usuarios.usuario.instituicao_id IS 'Instituição à qual o usuário está vinculado (define contexto organizacional)';

RAISE NOTICE '✅ Campo instituicao_id adicionado em usuarios.usuario';

-- ============================================================================
-- PASSO 4: Atualizar FKs de sessao (conta_usuario_id → usuario_id)
-- ============================================================================

-- 4.1: Renomear coluna
ALTER TABLE usuarios.sessao RENAME COLUMN conta_usuario_id TO usuario_id;

-- 4.2: Remover constraint antiga
ALTER TABLE usuarios.sessao DROP CONSTRAINT sessao_conta_usuario_id_fkey;

-- 4.3: Adicionar nova constraint
ALTER TABLE usuarios.sessao 
ADD CONSTRAINT sessao_usuario_id_fkey 
FOREIGN KEY (usuario_id) REFERENCES usuarios.usuario(id) ON DELETE CASCADE;

-- 4.4: Renomear trigger
ALTER TRIGGER trigger_auditoria_sessao ON usuarios.sessao RENAME TO trigger_auditoria_sessao_usuario;

RAISE NOTICE '✅ usuarios.sessao atualizada (conta_usuario_id → usuario_id)';

-- ============================================================================
-- PASSO 5: Atualizar FKs de tentativa_login
-- ============================================================================

-- 5.1: Renomear coluna
ALTER TABLE usuarios.tentativa_login RENAME COLUMN conta_usuario_id TO usuario_id;

-- 5.2: Remover constraint antiga
ALTER TABLE usuarios.tentativa_login DROP CONSTRAINT tentativa_login_conta_usuario_id_fkey;

-- 5.3: Adicionar nova constraint
ALTER TABLE usuarios.tentativa_login 
ADD CONSTRAINT tentativa_login_usuario_id_fkey 
FOREIGN KEY (usuario_id) REFERENCES usuarios.usuario(id);

RAISE NOTICE '✅ usuarios.tentativa_login atualizada (conta_usuario_id → usuario_id)';

-- ============================================================================
-- PASSO 6: Atualizar FKs de token_recuperacao
-- ============================================================================

-- 6.1: Renomear coluna
ALTER TABLE usuarios.token_recuperacao RENAME COLUMN conta_usuario_id TO usuario_id;

-- 6.2: Remover constraint antiga
ALTER TABLE usuarios.token_recuperacao DROP CONSTRAINT token_recuperacao_conta_usuario_id_fkey;

-- 6.3: Adicionar nova constraint
ALTER TABLE usuarios.token_recuperacao 
ADD CONSTRAINT token_recuperacao_usuario_id_fkey 
FOREIGN KEY (usuario_id) REFERENCES usuarios.usuario(id) ON DELETE CASCADE;

RAISE NOTICE '✅ usuarios.token_recuperacao atualizada (conta_usuario_id → usuario_id)';

-- ============================================================================
-- PASSO 7: Atualizar FKs das tabelas que apontavam para usuario_legacy
-- ============================================================================

-- 7.1: auditoria_login - Não há dados, só atualizar constraint
ALTER TABLE usuarios.auditoria_login DROP CONSTRAINT auditoria_login_usuario_id_fkey;
ALTER TABLE usuarios.auditoria_login 
ADD CONSTRAINT auditoria_login_usuario_id_fkey 
FOREIGN KEY (usuario_id) REFERENCES usuarios.usuario(id);

-- 7.2: evento - Não há dados, só atualizar constraint
ALTER TABLE usuarios.evento DROP CONSTRAINT evento_usuario_id_fkey;
ALTER TABLE usuarios.evento 
ADD CONSTRAINT evento_usuario_id_fkey 
FOREIGN KEY (usuario_id) REFERENCES usuarios.usuario(id) ON DELETE CASCADE;

-- 7.3: homeoffice - Não há dados, só atualizar constraint
ALTER TABLE usuarios.homeoffice DROP CONSTRAINT homeoffice_usuario_id_fkey;
ALTER TABLE usuarios.homeoffice 
ADD CONSTRAINT homeoffice_usuario_id_fkey 
FOREIGN KEY (usuario_id) REFERENCES usuarios.usuario(id) ON DELETE CASCADE;

-- 7.4: tarefa - Não há dados, só atualizar constraint
ALTER TABLE usuarios.tarefa DROP CONSTRAINT tarefa_usuario_id_fkey;
ALTER TABLE usuarios.tarefa 
ADD CONSTRAINT tarefa_usuario_id_fkey 
FOREIGN KEY (usuario_id) REFERENCES usuarios.usuario(id) ON DELETE CASCADE;

RAISE NOTICE '✅ Constraints de auditoria_login, evento, homeoffice, tarefa atualizadas';

-- ============================================================================
-- PASSO 8: Remover tabelas legacy
-- ============================================================================

-- 8.1: Remover usuario_papel (era relacionada à usuario_legacy)
DROP TABLE IF EXISTS usuarios.usuario_papel CASCADE;

-- 8.2: Remover usuario_legacy
DROP TABLE IF EXISTS usuarios.usuario_legacy CASCADE;

RAISE NOTICE '✅ Tabelas legacy removidas (usuario_papel, usuario_legacy)';

-- ============================================================================
-- PASSO 9: Criar tabela usuario_papel (ligada à nova estrutura)
-- ============================================================================

-- 9.1: Criar nova tabela de relacionamento N:N
CREATE TABLE usuarios.usuario_papel (
    usuario_id UUID NOT NULL REFERENCES usuarios.usuario(id) ON DELETE CASCADE,
    papel_id UUID NOT NULL REFERENCES usuarios.papel(id) ON DELETE CASCADE,
    atribuido_em TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atribuido_por UUID,
    PRIMARY KEY (usuario_id, papel_id)
);

-- 9.2: Criar índices
CREATE INDEX idx_usuario_papel_usuario ON usuarios.usuario_papel(usuario_id);
CREATE INDEX idx_usuario_papel_papel ON usuarios.usuario_papel(papel_id);

-- 9.3: Comentário
COMMENT ON TABLE usuarios.usuario_papel IS 'Relacionamento N:N entre usuários e papéis (roles/permissões)';

RAISE NOTICE '✅ Tabela usuarios.usuario_papel recriada com nova estrutura';

-- ============================================================================
-- VERIFICAÇÃO FINAL
-- ============================================================================

DO $$
DECLARE
    v_count_usuarios INTEGER;
    v_count_sessoes INTEGER;
    v_count_pessoas INTEGER;
    v_count_instituicoes INTEGER;
BEGIN
    -- Contar registros
    SELECT COUNT(*) INTO v_count_usuarios FROM usuarios.usuario;
    SELECT COUNT(*) INTO v_count_sessoes FROM usuarios.sessao;
    SELECT COUNT(*) INTO v_count_pessoas FROM cadastro.pessoa;
    SELECT COUNT(*) INTO v_count_instituicoes FROM cadastro.instituicao;
    
    RAISE NOTICE '==================================================';
    RAISE NOTICE '📊 RESULTADO DA MIGRAÇÃO:';
    RAISE NOTICE '==================================================';
    RAISE NOTICE 'usuarios.usuario: % registros', v_count_usuarios;
    RAISE NOTICE 'usuarios.sessao: % registros', v_count_sessoes;
    RAISE NOTICE 'cadastro.pessoa: % registros', v_count_pessoas;
    RAISE NOTICE 'cadastro.instituicao: % registros', v_count_instituicoes;
    RAISE NOTICE '==================================================';
    
    -- Verificar estrutura final
    RAISE NOTICE '🔍 Verificando estrutura final...';
    
    -- Verificar se todas as colunas existem
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'usuarios' 
        AND table_name = 'usuario' 
        AND column_name = 'instituicao_id'
    ) THEN
        RAISE NOTICE '✅ usuarios.usuario.instituicao_id: OK';
    ELSE
        RAISE EXCEPTION '❌ usuarios.usuario.instituicao_id: FALTANDO';
    END IF;
    
    IF EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_schema = 'usuarios' 
        AND table_name = 'sessao' 
        AND column_name = 'usuario_id'
    ) THEN
        RAISE NOTICE '✅ usuarios.sessao.usuario_id: OK';
    ELSE
        RAISE EXCEPTION '❌ usuarios.sessao.usuario_id: FALTANDO';
    END IF;
    
    RAISE NOTICE '==================================================';
    RAISE NOTICE '✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!';
    RAISE NOTICE '==================================================';
    RAISE NOTICE '';
    RAISE NOTICE '📐 Estrutura Final:';
    RAISE NOTICE '   usuarios.usuario = pessoa_id + instituicao_id + credenciais';
    RAISE NOTICE '   cadastro.pessoa = dados pessoais';
    RAISE NOTICE '   cadastro.instituicao = dados organizacionais';
    RAISE NOTICE '==================================================';
END $$;

COMMIT;

-- ============================================================================
-- PRÓXIMOS PASSOS
-- ============================================================================
-- 1. Verificar aplicação: atualizar código que referenciava usuarios.conta_usuario
-- 2. Testar autenticação com a nova estrutura
-- 3. Popular usuarios.usuario_papel com papéis dos usuários existentes
