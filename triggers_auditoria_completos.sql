-- =============================================================================
-- SIGMA-PLI - TRIGGERS DE AUDITORIA COMPLETOS
-- Sistema avançado de rastreamento de operações
-- =============================================================================

-- =============================================================================
-- SCHEMA E TABELAS DE AUDITORIA EXPANDIDAS
-- =============================================================================

-- Tabela de sessões de usuário
CREATE TABLE IF NOT EXISTS auditoria.sessao_usuario (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID,
    ip_address INET,
    user_agent TEXT,
    inicio_sessao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fim_sessao TIMESTAMP,
    ativa BOOLEAN DEFAULT TRUE,
    origem TEXT -- web, api, sistema
);

-- Tabela de operações sensíveis
CREATE TABLE IF NOT EXISTS auditoria.operacao_sensivel (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID,
    operacao TEXT NOT NULL,
    recurso TEXT NOT NULL,
    detalhes JSONB,
    ip_address INET,
    sucesso BOOLEAN,
    timestamp_operacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de alterações de permissões
CREATE TABLE IF NOT EXISTS auditoria.alteracao_permissao (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_afetado_id UUID,
    usuario_executor_id UUID,
    papel_anterior TEXT[],
    papel_novo TEXT[],
    motivo TEXT,
    timestamp_alteracao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de downloads de arquivos
CREATE TABLE IF NOT EXISTS auditoria.download_arquivo (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    arquivo_id UUID,
    usuario_id UUID,
    ip_address INET,
    user_agent TEXT,
    metodo_download TEXT, -- direct, api, bulk
    sucesso BOOLEAN,
    timestamp_download TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- FUNÇÕES DE CONFIGURAÇÃO DE CONTEXTO
-- =============================================================================

-- Função para configurar contexto do usuário atual
CREATE OR REPLACE FUNCTION auditoria.set_user_context(
    p_usuario_id UUID,
    p_ip_address TEXT DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    -- Configurar variáveis de sessão
    PERFORM set_config('app.current_user_id', p_usuario_id::TEXT, false);
    
    IF p_ip_address IS NOT NULL THEN
        PERFORM set_config('app.current_ip', p_ip_address, false);
    END IF;
    
    IF p_user_agent IS NOT NULL THEN
        PERFORM set_config('app.current_user_agent', p_user_agent, false);
    END IF;
    
    -- Registrar início de sessão se necessário
    INSERT INTO auditoria.sessao_usuario (usuario_id, ip_address, user_agent)
    VALUES (p_usuario_id, p_ip_address::INET, p_user_agent)
    ON CONFLICT DO NOTHING;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Função para limpar contexto
CREATE OR REPLACE FUNCTION auditoria.clear_user_context()
RETURNS VOID AS $$
BEGIN
    PERFORM set_config('app.current_user_id', '', false);
    PERFORM set_config('app.current_ip', '', false);
    PERFORM set_config('app.current_user_agent', '', false);
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- FUNÇÕES DE AUDITORIA ESPECIALIZADAS
-- =============================================================================

-- Função de auditoria básica (melhorada)
CREATE OR REPLACE FUNCTION auditoria.trigger_auditoria_basica()
RETURNS TRIGGER AS $$
DECLARE
    usuario_id_atual UUID;
    ip_address_atual INET;
    user_agent_atual TEXT;
    dados_sensíveis BOOLEAN := FALSE;
BEGIN
    -- Obter contexto da sessão
    BEGIN
        usuario_id_atual := current_setting('app.current_user_id', true)::UUID;
    EXCEPTION
        WHEN OTHERS THEN
            usuario_id_atual := NULL;
    END;
    
    BEGIN
        ip_address_atual := current_setting('app.current_ip', true)::INET;
    EXCEPTION
        WHEN OTHERS THEN
            ip_address_atual := NULL;
    END;
    
    BEGIN
        user_agent_atual := current_setting('app.current_user_agent', true);
    EXCEPTION
        WHEN OTHERS THEN
            user_agent_atual := NULL;
    END;
    
    -- Verificar se tabela contém dados sensíveis
    IF TG_TABLE_NAME IN ('usuario', 'papel', 'permissao', 'arquivo') THEN
        dados_sensíveis := TRUE;
    END IF;
    
    -- Registrar operação básica
    INSERT INTO auditoria.log_operacao (
        tabela,
        operacao,
        registro_id,
        dados_antigos,
        dados_novos,
        usuario_id,
        ip_address,
        user_agent,
        timestamp_operacao
    ) VALUES (
        TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME,
        TG_OP,
        CASE 
            WHEN TG_OP = 'DELETE' THEN OLD.id
            ELSE NEW.id
        END,
        CASE WHEN TG_OP IN ('UPDATE', 'DELETE') THEN to_jsonb(OLD) ELSE NULL END,
        CASE WHEN TG_OP IN ('INSERT', 'UPDATE') THEN to_jsonb(NEW) ELSE NULL END,
        usuario_id_atual,
        ip_address_atual,
        user_agent_atual,
        CURRENT_TIMESTAMP
    );
    
    -- Registrar operação sensível se aplicável
    IF dados_sensíveis THEN
        INSERT INTO auditoria.operacao_sensivel (
            usuario_id,
            operacao,
            recurso,
            detalhes,
            ip_address,
            sucesso,
            timestamp_operacao
        ) VALUES (
            usuario_id_atual,
            TG_OP,
            TG_TABLE_SCHEMA || '.' || TG_TABLE_NAME,
            jsonb_build_object(
                'registro_id', CASE WHEN TG_OP = 'DELETE' THEN OLD.id ELSE NEW.id END,
                'campos_alterados', CASE 
                    WHEN TG_OP = 'UPDATE' THEN auditoria.get_changed_fields(to_jsonb(OLD), to_jsonb(NEW))
                    ELSE NULL
                END
            ),
            ip_address_atual,
            TRUE,
            CURRENT_TIMESTAMP
        );
    END IF;
    
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Função para detectar campos alterados
CREATE OR REPLACE FUNCTION auditoria.get_changed_fields(old_data JSONB, new_data JSONB)
RETURNS JSONB AS $$
DECLARE
    changed_fields JSONB := '{}';
    key TEXT;
BEGIN
    FOR key IN SELECT jsonb_object_keys(new_data) LOOP
        IF old_data->key IS DISTINCT FROM new_data->key THEN
            changed_fields := changed_fields || jsonb_build_object(
                key, jsonb_build_object(
                    'anterior', old_data->key,
                    'novo', new_data->key
                )
            );
        END IF;
    END LOOP;
    
    RETURN changed_fields;
END;
$$ LANGUAGE plpgsql;

-- Função específica para auditoria de arquivos
CREATE OR REPLACE FUNCTION auditoria.trigger_auditoria_arquivo()
RETURNS TRIGGER AS $$
DECLARE
    usuario_id_atual UUID;
    ip_address_atual INET;
    operacao_critica BOOLEAN := FALSE;
BEGIN
    -- Obter contexto
    BEGIN
        usuario_id_atual := current_setting('app.current_user_id', true)::UUID;
        ip_address_atual := current_setting('app.current_ip', true)::INET;
    EXCEPTION
        WHEN OTHERS THEN
            usuario_id_atual := NULL;
            ip_address_atual := NULL;
    END;
    
    -- Verificar se é operação crítica
    IF TG_OP = 'DELETE' OR 
       (TG_OP = 'UPDATE' AND OLD.status != NEW.status) OR
       (TG_OP = 'UPDATE' AND OLD.publico != NEW.publico) THEN
        operacao_critica := TRUE;
    END IF;
    
    -- Auditoria básica
    PERFORM auditoria.trigger_auditoria_basica();
    
    -- Log específico para operações críticas em arquivos
    IF operacao_critica THEN
        INSERT INTO auditoria.operacao_sensivel (
            usuario_id,
            operacao,
            recurso,
            detalhes,
            ip_address,
            sucesso,
            timestamp_operacao
        ) VALUES (
            usuario_id_atual,
            TG_OP || '_CRITICO',
            'arquivo_' || CASE 
                WHEN TG_OP = 'DELETE' THEN OLD.id::TEXT
                ELSE NEW.id::TEXT
            END,
            jsonb_build_object(
                'nome_arquivo', CASE WHEN TG_OP = 'DELETE' THEN OLD.nome_original ELSE NEW.nome_original END,
                'motivo', CASE 
                    WHEN TG_OP = 'DELETE' THEN 'exclusao_arquivo'
                    WHEN OLD.status != NEW.status THEN 'alteracao_status'
                    WHEN OLD.publico != NEW.publico THEN 'alteracao_visibilidade'
                    ELSE 'alteracao_critica'
                END,
                'valor_anterior', CASE
                    WHEN TG_OP = 'UPDATE' AND OLD.status != NEW.status THEN OLD.status
                    WHEN TG_OP = 'UPDATE' AND OLD.publico != NEW.publico THEN OLD.publico::TEXT
                    ELSE NULL
                END,
                'valor_novo', CASE
                    WHEN TG_OP = 'UPDATE' AND OLD.status != NEW.status THEN NEW.status
                    WHEN TG_OP = 'UPDATE' AND OLD.publico != NEW.publico THEN NEW.publico::TEXT
                    ELSE NULL
                END
            ),
            ip_address_atual,
            TRUE,
            CURRENT_TIMESTAMP
        );
    END IF;
    
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Função para auditoria de alterações de usuário
CREATE OR REPLACE FUNCTION auditoria.trigger_auditoria_usuario()
RETURNS TRIGGER AS $$
DECLARE
    usuario_id_atual UUID;
    papeis_antigos TEXT[];
    papeis_novos TEXT[];
BEGIN
    -- Obter contexto
    BEGIN
        usuario_id_atual := current_setting('app.current_user_id', true)::UUID;
    EXCEPTION
        WHEN OTHERS THEN
            usuario_id_atual := NULL;
    END;
    
    -- Auditoria básica
    PERFORM auditoria.trigger_auditoria_basica();
    
    -- Para UPDATE de usuários, verificar alterações de papéis
    IF TG_OP = 'UPDATE' THEN
        -- Obter papéis atuais do usuário (antes da alteração)
        SELECT array_agg(p.nome) INTO papeis_antigos
        FROM usuarios.papel p
        JOIN usuarios.usuario_papel up ON p.id = up.papel_id
        WHERE up.usuario_id = OLD.id;
        
        -- Aguardar alguns milissegundos para obter papéis após alteração
        -- (Nota: Em um cenário real, isso seria tratado por triggers separados)
        
        -- Registrar alteração crítica se status mudou
        IF OLD.ativo != NEW.ativo THEN
            INSERT INTO auditoria.operacao_sensivel (
                usuario_id,
                operacao,
                recurso,
                detalhes,
                sucesso,
                timestamp_operacao
            ) VALUES (
                usuario_id_atual,
                'ALTERACAO_STATUS_USUARIO',
                'usuario_' || NEW.id::TEXT,
                jsonb_build_object(
                    'usuario_afetado', NEW.username,
                    'status_anterior', OLD.ativo,
                    'status_novo', NEW.ativo,
                    'executado_por', usuario_id_atual
                ),
                TRUE,
                CURRENT_TIMESTAMP
            );
        END IF;
    END IF;
    
    -- Para DELETE, registrar exclusão crítica
    IF TG_OP = 'DELETE' THEN
        INSERT INTO auditoria.operacao_sensivel (
            usuario_id,
            operacao,
            recurso,
            detalhes,
            sucesso,
            timestamp_operacao
        ) VALUES (
            usuario_id_atual,
            'EXCLUSAO_USUARIO',
            'usuario_' || OLD.id::TEXT,
            jsonb_build_object(
                'usuario_excluido', OLD.username,
                'email', OLD.email,
                'nome_completo', OLD.nome_completo,
                'ativo_antes_exclusao', OLD.ativo
            ),
            TRUE,
            CURRENT_TIMESTAMP
        );
    END IF;
    
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Função para auditoria de downloads
CREATE OR REPLACE FUNCTION auditoria.registrar_download(
    p_arquivo_id UUID,
    p_metodo_download TEXT DEFAULT 'direct',
    p_sucesso BOOLEAN DEFAULT TRUE
)
RETURNS VOID AS $$
DECLARE
    usuario_id_atual UUID;
    ip_address_atual INET;
    user_agent_atual TEXT;
BEGIN
    -- Obter contexto
    BEGIN
        usuario_id_atual := current_setting('app.current_user_id', true)::UUID;
        ip_address_atual := current_setting('app.current_ip', true)::INET;
        user_agent_atual := current_setting('app.current_user_agent', true);
    EXCEPTION
        WHEN OTHERS THEN
            usuario_id_atual := NULL;
            ip_address_atual := NULL;
            user_agent_atual := NULL;
    END;
    
    -- Registrar download
    INSERT INTO auditoria.download_arquivo (
        arquivo_id,
        usuario_id,
        ip_address,
        user_agent,
        metodo_download,
        sucesso,
        timestamp_download
    ) VALUES (
        p_arquivo_id,
        usuario_id_atual,
        ip_address_atual,
        user_agent_atual,
        p_metodo_download,
        p_sucesso,
        CURRENT_TIMESTAMP
    );
    
    -- Registrar como operação sensível se arquivo não é público
    INSERT INTO auditoria.operacao_sensivel (
        usuario_id,
        operacao,
        recurso,
        detalhes,
        sucesso,
        timestamp_operacao
    )
    SELECT 
        usuario_id_atual,
        'DOWNLOAD_ARQUIVO',
        'arquivo_' || a.id::TEXT,
        jsonb_build_object(
            'nome_arquivo', a.nome_original,
            'publico', a.publico,
            'metodo', p_metodo_download,
            'tamanho_bytes', a.tamanho_bytes
        ),
        p_sucesso,
        CURRENT_TIMESTAMP
    FROM dicionario.arquivo a
    WHERE a.id = p_arquivo_id AND NOT a.publico;
    
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =============================================================================
-- CRIAÇÃO DOS TRIGGERS
-- =============================================================================

-- Remover triggers existentes se houver
DROP TRIGGER IF EXISTS trigger_auditoria_arquivo ON dicionario.arquivo;
DROP TRIGGER IF EXISTS trigger_auditoria_usuario ON usuarios.usuario;
DROP TRIGGER IF EXISTS trigger_auditoria_perfil ON dicionario.perfil;
DROP TRIGGER IF EXISTS trigger_auditoria_produtor ON dicionario.produtor;
DROP TRIGGER IF EXISTS trigger_auditoria_papel ON usuarios.papel;
DROP TRIGGER IF EXISTS trigger_auditoria_permissao ON usuarios.permissao;

-- Criar triggers específicos
CREATE TRIGGER trigger_auditoria_arquivo
    AFTER INSERT OR UPDATE OR DELETE ON dicionario.arquivo
    FOR EACH ROW EXECUTE FUNCTION auditoria.trigger_auditoria_arquivo();

CREATE TRIGGER trigger_auditoria_usuario
    AFTER INSERT OR UPDATE OR DELETE ON usuarios.usuario
    FOR EACH ROW EXECUTE FUNCTION auditoria.trigger_auditoria_usuario();

-- Triggers básicos para outras tabelas importantes
CREATE TRIGGER trigger_auditoria_perfil
    AFTER INSERT OR UPDATE OR DELETE ON dicionario.perfil
    FOR EACH ROW EXECUTE FUNCTION auditoria.trigger_auditoria_basica();

CREATE TRIGGER trigger_auditoria_produtor
    AFTER INSERT OR UPDATE OR DELETE ON dicionario.produtor
    FOR EACH ROW EXECUTE FUNCTION auditoria.trigger_auditoria_basica();

CREATE TRIGGER trigger_auditoria_papel
    AFTER INSERT OR UPDATE OR DELETE ON usuarios.papel
    FOR EACH ROW EXECUTE FUNCTION auditoria.trigger_auditoria_basica();

CREATE TRIGGER trigger_auditoria_permissao
    AFTER INSERT OR UPDATE OR DELETE ON usuarios.permissao
    FOR EACH ROW EXECUTE FUNCTION auditoria.trigger_auditoria_basica();

CREATE TRIGGER trigger_auditoria_usuario_papel
    AFTER INSERT OR UPDATE OR DELETE ON usuarios.usuario_papel
    FOR EACH ROW EXECUTE FUNCTION auditoria.trigger_auditoria_basica();

-- =============================================================================
-- VIEWS PARA RELATÓRIOS DE AUDITORIA
-- =============================================================================

-- View resumo de operações por usuário
CREATE VIEW auditoria.view_operacoes_usuario AS
SELECT 
    u.username,
    u.nome_completo,
    lo.operacao,
    lo.tabela,
    COUNT(*) as total_operacoes,
    MIN(lo.timestamp_operacao) as primeira_operacao,
    MAX(lo.timestamp_operacao) as ultima_operacao
FROM auditoria.log_operacao lo
JOIN usuarios.usuario u ON lo.usuario_id = u.id
WHERE lo.timestamp_operacao >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY u.id, u.username, u.nome_completo, lo.operacao, lo.tabela
ORDER BY total_operacoes DESC;

-- View operações sensíveis recentes
CREATE VIEW auditoria.view_operacoes_sensíveis_recentes AS
SELECT 
    os.timestamp_operacao,
    u.username,
    u.nome_completo,
    os.operacao,
    os.recurso,
    os.detalhes,
    os.ip_address
FROM auditoria.operacao_sensivel os
LEFT JOIN usuarios.usuario u ON os.usuario_id = u.id
WHERE os.timestamp_operacao >= CURRENT_DATE - INTERVAL '7 days'
ORDER BY os.timestamp_operacao DESC;

-- View downloads por arquivo
CREATE VIEW auditoria.view_downloads_arquivo AS
SELECT 
    a.nome_original,
    a.titulo,
    COUNT(da.id) as total_downloads,
    COUNT(DISTINCT da.usuario_id) as usuarios_unicos,
    MAX(da.timestamp_download) as ultimo_download,
    SUM(CASE WHEN da.sucesso THEN 1 ELSE 0 END) as downloads_sucesso,
    SUM(CASE WHEN NOT da.sucesso THEN 1 ELSE 0 END) as downloads_falha
FROM dicionario.arquivo a
LEFT JOIN auditoria.download_arquivo da ON a.id = da.arquivo_id
WHERE da.timestamp_download >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY a.id, a.nome_original, a.titulo
ORDER BY total_downloads DESC;

-- View atividade por IP
CREATE VIEW auditoria.view_atividade_ip AS
SELECT 
    lo.ip_address,
    COUNT(DISTINCT lo.usuario_id) as usuarios_unicos,
    COUNT(*) as total_operacoes,
    MIN(lo.timestamp_operacao) as primeira_atividade,
    MAX(lo.timestamp_operacao) as ultima_atividade,
    array_agg(DISTINCT lo.operacao) as operacoes_realizadas
FROM auditoria.log_operacao lo
WHERE lo.ip_address IS NOT NULL 
AND lo.timestamp_operacao >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY lo.ip_address
ORDER BY total_operacoes DESC;

-- =============================================================================
-- FUNÇÕES DE RELATÓRIOS
-- =============================================================================

-- Função para relatório de atividade de usuário
CREATE OR REPLACE FUNCTION auditoria.relatorio_atividade_usuario(
    p_usuario_id UUID,
    p_dias INTEGER DEFAULT 30
)
RETURNS TABLE (
    data DATE,
    operacao TEXT,
    tabela TEXT,
    total_operacoes BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        lo.timestamp_operacao::DATE as data,
        lo.operacao,
        lo.tabela,
        COUNT(*) as total_operacoes
    FROM auditoria.log_operacao lo
    WHERE lo.usuario_id = p_usuario_id
    AND lo.timestamp_operacao >= CURRENT_DATE - INTERVAL '%s days' % p_dias
    GROUP BY lo.timestamp_operacao::DATE, lo.operacao, lo.tabela
    ORDER BY data DESC, total_operacoes DESC;
END;
$$ LANGUAGE plpgsql;

-- Função para detectar atividade suspeita
CREATE OR REPLACE FUNCTION auditoria.detectar_atividade_suspeita()
RETURNS TABLE (
    usuario_id UUID,
    username TEXT,
    motivo TEXT,
    detalhes JSONB,
    timestamp_deteccao TIMESTAMP
) AS $$
BEGIN
    RETURN QUERY
    -- Muitos downloads em pouco tempo
    SELECT 
        da.usuario_id,
        u.username,
        'downloads_excessivos' as motivo,
        jsonb_build_object(
            'total_downloads', COUNT(*),
            'periodo_horas', 1,
            'ultimo_download', MAX(da.timestamp_download)
        ) as detalhes,
        CURRENT_TIMESTAMP as timestamp_deteccao
    FROM auditoria.download_arquivo da
    JOIN usuarios.usuario u ON da.usuario_id = u.id
    WHERE da.timestamp_download >= CURRENT_TIMESTAMP - INTERVAL '1 hour'
    GROUP BY da.usuario_id, u.username
    HAVING COUNT(*) > 50
    
    UNION ALL
    
    -- Login de IPs muito diferentes
    SELECT 
        lo.usuario_id,
        u.username,
        'ips_multiplos' as motivo,
        jsonb_build_object(
            'ips_diferentes', COUNT(DISTINCT lo.ip_address),
            'periodo_horas', 24
        ) as detalhes,
        CURRENT_TIMESTAMP as timestamp_deteccao
    FROM auditoria.log_operacao lo
    JOIN usuarios.usuario u ON lo.usuario_id = u.id
    WHERE lo.timestamp_operacao >= CURRENT_TIMESTAMP - INTERVAL '24 hours'
    AND lo.ip_address IS NOT NULL
    GROUP BY lo.usuario_id, u.username
    HAVING COUNT(DISTINCT lo.ip_address) > 5;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- CONFIGURAÇÕES DE LIMPEZA AUTOMÁTICA
-- =============================================================================

-- Função para limpeza de logs antigos
CREATE OR REPLACE FUNCTION auditoria.limpar_logs_antigos(p_dias INTEGER DEFAULT 365)
RETURNS TEXT AS $$
DECLARE
    registros_removidos INTEGER;
    resultado TEXT;
BEGIN
    -- Limpar logs de operação antigos
    DELETE FROM auditoria.log_operacao 
    WHERE timestamp_operacao < CURRENT_DATE - INTERVAL '%s days' % p_dias;
    GET DIAGNOSTICS registros_removidos = ROW_COUNT;
    resultado := 'Logs de operação removidos: ' || registros_removidos || E'\n';
    
    -- Limpar downloads antigos
    DELETE FROM auditoria.download_arquivo 
    WHERE timestamp_download < CURRENT_DATE - INTERVAL '%s days' % p_dias;
    GET DIAGNOSTICS registros_removidos = ROW_COUNT;
    resultado := resultado || 'Logs de download removidos: ' || registros_removidos || E'\n';
    
    -- Limpar sessões antigas
    DELETE FROM auditoria.sessao_usuario 
    WHERE inicio_sessao < CURRENT_DATE - INTERVAL '%s days' % p_dias;
    GET DIAGNOSTICS registros_removidos = ROW_COUNT;
    resultado := resultado || 'Sessões antigas removidas: ' || registros_removidos || E'\n';
    
    RETURN resultado;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- EXEMPLO DE USO
-- =============================================================================

/*
-- 1. Configurar contexto do usuário (fazer no início da sessão)
SELECT auditoria.set_user_context(
    'USER_UUID_HERE'::UUID,
    '192.168.1.100',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
);

-- 2. Executar operações normais (triggers são automáticos)
INSERT INTO dicionario.arquivo (nome_original, titulo) VALUES ('teste.pdf', 'Arquivo de teste');

-- 3. Registrar download de arquivo
SELECT auditoria.registrar_download('ARQUIVO_UUID_HERE'::UUID, 'api', TRUE);

-- 4. Consultar relatórios
SELECT * FROM auditoria.view_operacoes_sensíveis_recentes;
SELECT * FROM auditoria.detectar_atividade_suspeita();

-- 5. Limpar logs antigos (executar periodicamente)
SELECT auditoria.limpar_logs_antigos(365);
*/

-- =============================================================================
-- ÍNDICES PARA PERFORMANCE
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_log_operacao_usuario_timestamp 
ON auditoria.log_operacao(usuario_id, timestamp_operacao);

CREATE INDEX IF NOT EXISTS idx_download_arquivo_timestamp 
ON auditoria.download_arquivo(timestamp_download);

CREATE INDEX IF NOT EXISTS idx_operacao_sensivel_timestamp 
ON auditoria.operacao_sensivel(timestamp_operacao);

CREATE INDEX IF NOT EXISTS idx_sessao_usuario_ativa 
ON auditoria.sessao_usuario(ativa, inicio_sessao);

-- =============================================================================
-- COMENTÁRIOS E DOCUMENTAÇÃO
-- =============================================================================

COMMENT ON SCHEMA auditoria IS 'Sistema completo de auditoria e rastreamento do SIGMA-PLI';

COMMENT ON FUNCTION auditoria.set_user_context(UUID, TEXT, TEXT) IS 'Configura contexto do usuário para auditoria';
COMMENT ON FUNCTION auditoria.registrar_download(UUID, TEXT, BOOLEAN) IS 'Registra download de arquivo com auditoria';
COMMENT ON FUNCTION auditoria.detectar_atividade_suspeita() IS 'Detecta padrões suspeitos de atividade';
COMMENT ON FUNCTION auditoria.limpar_logs_antigos(INTEGER) IS 'Remove logs antigos para manutenção do banco';

COMMENT ON VIEW auditoria.view_operacoes_usuario IS 'Resumo de operações por usuário (últimos 30 dias)';
COMMENT ON VIEW auditoria.view_operacoes_sensíveis_recentes IS 'Operações sensíveis dos últimos 7 dias';
COMMENT ON VIEW auditoria.view_downloads_arquivo IS 'Estatísticas de download por arquivo';
COMMENT ON VIEW auditoria.view_atividade_ip IS 'Atividade agrupada por endereço IP';