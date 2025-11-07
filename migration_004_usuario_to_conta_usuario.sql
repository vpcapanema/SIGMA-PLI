-- ============================================================================
-- MIGRATION: Migrar relacionamentos de usuarios.usuario para usuarios.conta_usuario
-- Data: 2025-11-03
-- Objetivo: Preparar tabelas para remoção de usuarios.usuario
-- ============================================================================

BEGIN;

-- ============================================================================
-- PASSO 1: AUDITORIA_LOGIN
-- ============================================================================

-- 1.1: Adicionar nova coluna
ALTER TABLE usuarios.auditoria_login 
ADD COLUMN conta_usuario_id UUID;

-- 1.2: Comentário
COMMENT ON COLUMN usuarios.auditoria_login.conta_usuario_id IS 'Referência para usuarios.conta_usuario (nova arquitetura)';

-- 1.3: Migrar dados existentes (se houver)
-- Como a tabela está vazia, este UPDATE não fará nada, mas fica para documentação
UPDATE usuarios.auditoria_login al
SET conta_usuario_id = cu.id
FROM usuarios.usuario u
JOIN usuarios.conta_usuario cu ON u.email = cu.email
WHERE al.usuario_id = u.id;

-- 1.4: Remover constraint antiga
ALTER TABLE usuarios.auditoria_login 
DROP CONSTRAINT IF EXISTS auditoria_login_usuario_id_fkey;

-- 1.5: Adicionar nova constraint
ALTER TABLE usuarios.auditoria_login 
ADD CONSTRAINT auditoria_login_conta_usuario_id_fkey 
FOREIGN KEY (conta_usuario_id) REFERENCES usuarios.conta_usuario(id) ON DELETE CASCADE;

-- 1.6: Criar índice
CREATE INDEX IF NOT EXISTS idx_auditoria_login_conta_usuario 
ON usuarios.auditoria_login(conta_usuario_id);

-- 1.7: Remover coluna antiga
ALTER TABLE usuarios.auditoria_login 
DROP COLUMN usuario_id;

RAISE NOTICE '✅ usuarios.auditoria_login migrada para conta_usuario';

-- ============================================================================
-- PASSO 2: EVENTO
-- ============================================================================

-- 2.1: Adicionar nova coluna
ALTER TABLE usuarios.evento 
ADD COLUMN conta_usuario_id UUID;

-- 2.2: Comentário
COMMENT ON COLUMN usuarios.evento.conta_usuario_id IS 'Referência para usuarios.conta_usuario';

-- 2.3: Migrar dados existentes
UPDATE usuarios.evento e
SET conta_usuario_id = cu.id
FROM usuarios.usuario u
JOIN usuarios.conta_usuario cu ON u.email = cu.email
WHERE e.usuario_id = u.id;

-- 2.4: Remover constraint antiga
ALTER TABLE usuarios.evento 
DROP CONSTRAINT IF EXISTS evento_usuario_id_fkey;

-- 2.5: Adicionar nova constraint
ALTER TABLE usuarios.evento 
ADD CONSTRAINT evento_conta_usuario_id_fkey 
FOREIGN KEY (conta_usuario_id) REFERENCES usuarios.conta_usuario(id) ON DELETE CASCADE;

-- 2.6: Criar índice
CREATE INDEX IF NOT EXISTS idx_evento_conta_usuario 
ON usuarios.evento(conta_usuario_id);

-- 2.7: Remover coluna antiga
ALTER TABLE usuarios.evento 
DROP COLUMN usuario_id;

RAISE NOTICE '✅ usuarios.evento migrada para conta_usuario';

-- ============================================================================
-- PASSO 3: HOMEOFFICE
-- ============================================================================

-- 3.1: Adicionar nova coluna
ALTER TABLE usuarios.homeoffice 
ADD COLUMN conta_usuario_id UUID;

-- 3.2: Comentário
COMMENT ON COLUMN usuarios.homeoffice.conta_usuario_id IS 'Referência para usuarios.conta_usuario';

-- 3.3: Migrar dados existentes
UPDATE usuarios.homeoffice h
SET conta_usuario_id = cu.id
FROM usuarios.usuario u
JOIN usuarios.conta_usuario cu ON u.email = cu.email
WHERE h.usuario_id = u.id;

-- 3.4: Remover constraint de unique antiga (usuario_id + data)
ALTER TABLE usuarios.homeoffice 
DROP CONSTRAINT IF EXISTS homeoffice_usuario_id_data_key;

-- 3.5: Remover constraint FK antiga
ALTER TABLE usuarios.homeoffice 
DROP CONSTRAINT IF EXISTS homeoffice_usuario_id_fkey;

-- 3.6: Adicionar nova constraint FK
ALTER TABLE usuarios.homeoffice 
ADD CONSTRAINT homeoffice_conta_usuario_id_fkey 
FOREIGN KEY (conta_usuario_id) REFERENCES usuarios.conta_usuario(id) ON DELETE CASCADE;

-- 3.7: Adicionar nova constraint UNIQUE (conta_usuario_id + data)
ALTER TABLE usuarios.homeoffice 
ADD CONSTRAINT homeoffice_conta_usuario_id_data_key 
UNIQUE (conta_usuario_id, data);

-- 3.8: Criar índice
CREATE INDEX IF NOT EXISTS idx_homeoffice_conta_usuario 
ON usuarios.homeoffice(conta_usuario_id);

-- 3.9: Remover coluna antiga
ALTER TABLE usuarios.homeoffice 
DROP COLUMN usuario_id;

RAISE NOTICE '✅ usuarios.homeoffice migrada para conta_usuario';

-- ============================================================================
-- PASSO 4: TAREFA
-- ============================================================================

-- 4.1: Adicionar nova coluna
ALTER TABLE usuarios.tarefa 
ADD COLUMN conta_usuario_id UUID;

-- 4.2: Comentário
COMMENT ON COLUMN usuarios.tarefa.conta_usuario_id IS 'Referência para usuarios.conta_usuario';

-- 4.3: Migrar dados existentes
UPDATE usuarios.tarefa t
SET conta_usuario_id = cu.id
FROM usuarios.usuario u
JOIN usuarios.conta_usuario cu ON u.email = cu.email
WHERE t.usuario_id = u.id;

-- 4.4: Remover constraint antiga
ALTER TABLE usuarios.tarefa 
DROP CONSTRAINT IF EXISTS tarefa_usuario_id_fkey;

-- 4.5: Adicionar nova constraint
ALTER TABLE usuarios.tarefa 
ADD CONSTRAINT tarefa_conta_usuario_id_fkey 
FOREIGN KEY (conta_usuario_id) REFERENCES usuarios.conta_usuario(id) ON DELETE CASCADE;

-- 4.6: Criar índice
CREATE INDEX IF NOT EXISTS idx_tarefa_conta_usuario 
ON usuarios.tarefa(conta_usuario_id);

-- 4.7: Remover coluna antiga
ALTER TABLE usuarios.tarefa 
DROP COLUMN usuario_id;

RAISE NOTICE '✅ usuarios.tarefa migrada para conta_usuario';

-- ============================================================================
-- PASSO 5: USUARIO_PAPEL (tratamento especial)
-- ============================================================================

-- Esta tabela faz relação N:N entre usuario e papel
-- Precisamos criar nova tabela conta_usuario_papel

-- 5.1: Criar nova tabela conta_usuario_papel
CREATE TABLE IF NOT EXISTS usuarios.conta_usuario_papel (
    conta_usuario_id UUID NOT NULL REFERENCES usuarios.conta_usuario(id) ON DELETE CASCADE,
    papel_id UUID NOT NULL REFERENCES usuarios.papel(id) ON DELETE CASCADE,
    atribuido_em TIMESTAMP WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    atribuido_por UUID,
    PRIMARY KEY (conta_usuario_id, papel_id)
);

-- 5.2: Comentário
COMMENT ON TABLE usuarios.conta_usuario_papel IS 'Relacionamento N:N entre contas de usuário e papéis (roles)';

-- 5.3: Migrar dados existentes de usuario_papel para conta_usuario_papel
INSERT INTO usuarios.conta_usuario_papel (conta_usuario_id, papel_id)
SELECT DISTINCT cu.id, up.papel_id
FROM usuarios.usuario_papel up
JOIN usuarios.usuario u ON up.usuario_id = u.id
JOIN usuarios.conta_usuario cu ON u.email = cu.email
ON CONFLICT (conta_usuario_id, papel_id) DO NOTHING;

-- 5.4: Criar índices
CREATE INDEX IF NOT EXISTS idx_conta_usuario_papel_conta 
ON usuarios.conta_usuario_papel(conta_usuario_id);

CREATE INDEX IF NOT EXISTS idx_conta_usuario_papel_papel 
ON usuarios.conta_usuario_papel(papel_id);

RAISE NOTICE '✅ usuarios.conta_usuario_papel criada e migrada';

-- ============================================================================
-- VERIFICAÇÃO FINAL
-- ============================================================================

DO $$
DECLARE
    v_count_auditoria INTEGER;
    v_count_evento INTEGER;
    v_count_homeoffice INTEGER;
    v_count_tarefa INTEGER;
    v_count_papel INTEGER;
BEGIN
    -- Contar registros migrados
    SELECT COUNT(*) INTO v_count_auditoria FROM usuarios.auditoria_login WHERE conta_usuario_id IS NOT NULL;
    SELECT COUNT(*) INTO v_count_evento FROM usuarios.evento WHERE conta_usuario_id IS NOT NULL;
    SELECT COUNT(*) INTO v_count_homeoffice FROM usuarios.homeoffice WHERE conta_usuario_id IS NOT NULL;
    SELECT COUNT(*) INTO v_count_tarefa FROM usuarios.tarefa WHERE conta_usuario_id IS NOT NULL;
    SELECT COUNT(*) INTO v_count_papel FROM usuarios.conta_usuario_papel;
    
    RAISE NOTICE '==================================================';
    RAISE NOTICE '📊 RESULTADO DA MIGRAÇÃO:';
    RAISE NOTICE '==================================================';
    RAISE NOTICE 'usuarios.auditoria_login: % registros migrados', v_count_auditoria;
    RAISE NOTICE 'usuarios.evento: % registros migrados', v_count_evento;
    RAISE NOTICE 'usuarios.homeoffice: % registros migrados', v_count_homeoffice;
    RAISE NOTICE 'usuarios.tarefa: % registros migrados', v_count_tarefa;
    RAISE NOTICE 'usuarios.conta_usuario_papel: % registros migrados', v_count_papel;
    RAISE NOTICE '==================================================';
    RAISE NOTICE '✅ MIGRAÇÃO CONCLUÍDA COM SUCESSO!';
    RAISE NOTICE '==================================================';
END $$;

COMMIT;

-- ============================================================================
-- PRÓXIMO PASSO: Executar script de remoção
-- ============================================================================
-- Após confirmar que a migração foi bem-sucedida, execute:
-- DROP TABLE usuarios.usuario_papel CASCADE;
-- DROP TABLE usuarios.usuario CASCADE;
