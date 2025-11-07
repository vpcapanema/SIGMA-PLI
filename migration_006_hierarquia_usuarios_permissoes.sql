-- =====================================================
-- MIGRAÇÃO 006: Hierarquia de Usuários e Permissões
-- Sistema SIGMA-PLI
-- Data: 03/11/2025
-- =====================================================

BEGIN;

    -- =====================================================
    -- 1. ADICIONAR CAMPO tipo_usuario COM CONSTRAINT
    -- =====================================================

    -- Adicionar coluna tipo_usuario se não existir
    DO $$
    BEGIN
        IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'usuarios'
            AND table_name = 'usuario'
            AND column_name = 'tipo_usuario'
    ) THEN
        ALTER TABLE usuarios.usuario 
        ADD COLUMN tipo_usuario VARCHAR
        (50) NOT NULL DEFAULT 'VISUALIZADOR';

    RAISE NOTICE 'Coluna "tipo_usuario" adicionada com sucesso';
ELSE
        RAISE NOTICE 'Coluna "tipo_usuario" já existe';
END
IF;
END $$;

-- Adicionar constraint para valores válidos
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
    FROM pg_constraint
    WHERE conname = 'ck_usuario_tipo_usuario'
    ) THEN
    ALTER TABLE usuarios.usuario 
        ADD CONSTRAINT ck_usuario_tipo_usuario 
        CHECK (tipo_usuario IN ('ADMIN', 'GESTOR', 'ANALISTA', 'OPERADOR', 'VISUALIZADOR'));

    RAISE NOTICE 'Constraint "ck_usuario_tipo_usuario" adicionada com sucesso';
ELSE
        RAISE NOTICE 'Constraint "ck_usuario_tipo_usuario" já existe';
END
IF;
END $$;

-- =====================================================
-- 2. ADICIONAR CAMPO nivel_acesso
-- =====================================================

-- Adicionar coluna nivel_acesso se não existir
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
    FROM information_schema.columns
    WHERE table_schema = 'usuarios'
        AND table_name = 'usuario'
        AND column_name = 'nivel_acesso'
    ) THEN
    ALTER TABLE usuarios.usuario 
        ADD COLUMN nivel_acesso INTEGER DEFAULT 1;

RAISE NOTICE 'Coluna "nivel_acesso" adicionada com sucesso';
    ELSE
        RAISE NOTICE 'Coluna "nivel_acesso" já existe';
END
IF;
END $$;

-- Adicionar constraint para valores válidos (1 a 5)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
    FROM pg_constraint
    WHERE conname = 'ck_usuario_nivel_acesso'
    ) THEN
    ALTER TABLE usuarios.usuario 
        ADD CONSTRAINT ck_usuario_nivel_acesso 
        CHECK (nivel_acesso >= 1 AND nivel_acesso <= 5);

    RAISE NOTICE 'Constraint "ck_usuario_nivel_acesso" adicionada com sucesso';
ELSE
        RAISE NOTICE 'Constraint "ck_usuario_nivel_acesso" já existe';
END
IF;
END $$;

-- =====================================================
-- 3. FUNÇÃO PARA CALCULAR nivel_acesso AUTOMATICAMENTE
-- =====================================================

CREATE OR REPLACE FUNCTION usuarios.calcular_nivel_acesso
()
RETURNS TRIGGER AS $$
BEGIN
    -- Mapear tipo_usuario para nivel_acesso
    NEW.nivel_acesso := CASE NEW.tipo_usuario
        WHEN 'ADMIN' THEN 5
        WHEN 'GESTOR' THEN 4
        WHEN 'ANALISTA' THEN 3
        WHEN 'OPERADOR' THEN 2
        WHEN 'VISUALIZADOR' THEN 1
        ELSE 1
END;

RETURN NEW;
END;
$$ LANGUAGE plpgsql;

COMMENT ON FUNCTION usuarios.calcular_nivel_acesso
() IS 
'Calcula automaticamente o nivel_acesso baseado no tipo_usuario: ADMIN=5, GESTOR=4, ANALISTA=3, OPERADOR=2, VISUALIZADOR=1';

-- =====================================================
-- 4. TRIGGER PARA CALCULAR nivel_acesso AUTOMATICAMENTE
-- =====================================================

-- Remover trigger se já existir
DROP TRIGGER IF EXISTS tr_usuario_calcular_nivel
ON usuarios.usuario;

-- Criar trigger
CREATE TRIGGER tr_usuario_calcular_nivel
    BEFORE
INSERT OR
UPDATE OF tipo_usuario ON usuarios.usuario
    FOR EACH ROW
EXECUTE FUNCTION usuarios
.calcular_nivel_acesso
();

COMMENT ON TRIGGER tr_usuario_calcular_nivel ON usuarios.usuario IS 
'Trigger que calcula automaticamente o nivel_acesso quando tipo_usuario é inserido ou atualizado';

-- =====================================================
-- 5. ATUALIZAR REGISTROS EXISTENTES
-- =====================================================

-- Atualizar nivel_acesso de registros existentes baseado no tipo_usuario
UPDATE usuarios.usuario
SET nivel_acesso = CASE tipo_usuario
    WHEN 'ADMIN' THEN 5
    WHEN 'GESTOR' THEN 4
    WHEN 'ANALISTA' THEN 3
    WHEN 'OPERADOR' THEN 2
    WHEN 'VISUALIZADOR' THEN 1
    ELSE 1
END;

-- =====================================================
-- 6. ÍNDICES PARA PERFORMANCE
-- =====================================================

-- Índice para consultas por tipo_usuario
CREATE INDEX
IF NOT EXISTS idx_usuario_tipo_usuario 
ON usuarios.usuario
(tipo_usuario);

-- Índice para consultas por nivel_acesso
CREATE INDEX
IF NOT EXISTS idx_usuario_nivel_acesso 
ON usuarios.usuario
(nivel_acesso);

-- Índice composto para consultas por tipo_usuario + ativo
CREATE INDEX
IF NOT EXISTS idx_usuario_tipo_ativo 
ON usuarios.usuario
(tipo_usuario, ativo);

-- =====================================================
-- 7. COMENTÁRIOS PARA DOCUMENTAÇÃO
-- =====================================================

COMMENT ON COLUMN usuarios.usuario.tipo_usuario IS 
'Tipo de usuário: ADMIN (5), GESTOR (4), ANALISTA (3), OPERADOR (2), VISUALIZADOR (1)';

COMMENT ON COLUMN usuarios.usuario.nivel_acesso IS 
'Nível de acesso do usuário (1-5), calculado automaticamente pelo tipo_usuario';

-- =====================================================
-- 8. VIEW COM HIERARQUIA (FACILITADOR)
-- =====================================================

CREATE OR REPLACE VIEW usuarios.v_usuarios_hierarquia AS
SELECT
    u.id,
    u.username,
    u.email_institucional,
    u.tipo_usuario,
    u.nivel_acesso,
    u.ativo,
    u.email_verificado,
    u.criado_em,
    u.ultimo_login,
    CASE u.tipo_usuario
        WHEN 'ADMIN' THEN 'Administrador'
        WHEN 'GESTOR' THEN 'Gestor'
        WHEN 'ANALISTA' THEN 'Analista'
        WHEN 'OPERADOR' THEN 'Operador'
        WHEN 'VISUALIZADOR' THEN 'Visualizador'
    END as tipo_usuario_descricao
FROM usuarios.usuario u
ORDER BY u.nivel_acesso DESC, u.criado_em DESC;

COMMENT ON VIEW usuarios.v_usuarios_hierarquia IS 
'View com todos os dados de usuários incluindo hierarquia e descrição do tipo';

-- =====================================================
-- 9. FUNÇÃO PARA VERIFICAR PERMISSÃO
-- =====================================================

CREATE OR REPLACE FUNCTION usuarios.verificar_permissao
(
    p_usuario_id UUID,
    p_nivel_minimo INTEGER
)
RETURNS BOOLEAN AS $$
DECLARE
    v_nivel_usuario INTEGER;
BEGIN
    -- Buscar nivel_acesso do usuário
    SELECT nivel_acesso
    INTO v_nivel_usuario
    FROM usuarios.usuario
    WHERE id = p_usuario_id
        AND ativo = true;

    -- Se usuário não encontrado ou inativo, retorna false
    IF v_nivel_usuario IS NULL THEN
    RETURN FALSE;
END
IF;
    
    -- Retorna true se nivel do usuário é >= nivel mínimo requerido
    RETURN v_nivel_usuario
>= p_nivel_minimo;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

COMMENT ON FUNCTION usuarios.verificar_permissao
(UUID, INTEGER) IS 
'Verifica se um usuário tem permissão baseado no nível mínimo requerido. Retorna true se nivel_acesso >= nivel_minimo';

-- =====================================================
-- 10. ESTATÍSTICAS DE USUÁRIOS POR TIPO
-- =====================================================

CREATE OR REPLACE VIEW usuarios.v_estatisticas_tipo_usuario AS
SELECT
    tipo_usuario,
    nivel_acesso,
    COUNT(*) as total_usuarios,
    COUNT(CASE WHEN ativo = true THEN 1 END) as ativos,
    COUNT(CASE WHEN ativo = false THEN 1 END) as inativos,
    COUNT(CASE WHEN email_verificado = true THEN 1 END) as emails_verificados
FROM usuarios.usuario
GROUP BY tipo_usuario, nivel_acesso
ORDER BY nivel_acesso DESC;

COMMENT ON VIEW usuarios.v_estatisticas_tipo_usuario IS 
'Estatísticas de usuários agrupados por tipo_usuario e nivel_acesso';

COMMIT;

-- =====================================================
-- VERIFICAÇÃO FINAL
-- =====================================================

DO $$
DECLARE
    v_count INTEGER;
BEGIN
    -- Verificar se as colunas foram criadas
    SELECT COUNT(*)
    INTO v_count
    FROM information_schema.columns
    WHERE table_schema = 'usuarios'
        AND table_name = 'usuario'
        AND column_name IN ('tipo_usuario', 'nivel_acesso');

    IF v_count = 2 THEN
        RAISE NOTICE '✅ Migração 006 concluída com sucesso!';
RAISE NOTICE '✅ Colunas tipo_usuario e nivel_acesso criadas';
        RAISE NOTICE '✅ Constraints adicionadas';
        RAISE NOTICE '✅ Trigger de cálculo automático criado';
        RAISE NOTICE '✅ Índices criados';
        RAISE NOTICE '✅ Views de consulta criadas';
    ELSE
        RAISE WARNING '⚠️ Verificar se todas as colunas foram criadas corretamente';
END
IF;
END $$;
