-- =============================================================================
-- SIGMA-PLI - SCRIPT DE MIGRAÇÃO DE DADOS CSV LEGADOS
-- Ajusta estrutura para dados existentes e carrega via PostgreSQL COPY
-- =============================================================================

-- =============================================================================
-- TABELAS TEMPORÁRIAS PARA IMPORTAÇÃO DOS CSVs
-- =============================================================================

-- Tabela temporária para importar CSVs com estrutura flexível
CREATE TABLE IF NOT EXISTS dicionario.temp_csv_import (
    nome_arquivo TEXT,
    caminho_completo TEXT,
    tamanho_bytes BIGINT,
    data_modificacao TEXT,
    extensao TEXT,
    tipo_conteudo TEXT,
    produtor TEXT,
    departamento TEXT,
    instituicao TEXT,
    descricao TEXT,
    palavras_chave TEXT,
    publico TEXT,
    observacoes TEXT,
    created_date TEXT,
    -- Campos específicos conforme CSV legado
    campo1 TEXT,
    campo2 TEXT,
    campo3 TEXT,
    campo4 TEXT,
    campo5 TEXT,
    campo6 TEXT,
    campo7 TEXT,
    campo8 TEXT,
    campo9 TEXT,
    campo10 TEXT
);

-- =============================================================================
-- PROCEDIMENTO DE MIGRAÇÃO DOS DADOS LEGADOS
-- =============================================================================

CREATE OR REPLACE FUNCTION dicionario.migrar_dados_csv_legado()
RETURNS TEXT AS $$
DECLARE
    resultado TEXT := '';
    contador INTEGER := 0;
    total_registros INTEGER;
    rec RECORD;
    perfil_id UUID;
    extensao_id UUID;
    produtor_id UUID;
    novo_arquivo_id UUID;
BEGIN
    -- Limpar tabela temporária
    DELETE FROM dicionario.temp_csv_import;
    
    resultado := 'INÍCIO DA MIGRAÇÃO DOS DADOS CSV LEGADOS' || E'\n';
    resultado := resultado || '================================================' || E'\n';
    
    -- PASSO 1: Carregar dados do CSV legado
    resultado := resultado || 'PASSO 1: Carregando dados do CSV...' || E'\n';
    
    -- IMPORTANTE: O comando COPY deve ser executado separadamente
    -- COPY dicionario.temp_csv_import FROM 'caminho/para/arquivo_legado.csv' WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',', ENCODING 'UTF8');
    
    -- Verificar se dados foram carregados
    SELECT COUNT(*) INTO total_registros FROM dicionario.temp_csv_import;
    resultado := resultado || 'Total de registros carregados: ' || total_registros || E'\n' || E'\n';
    
    IF total_registros = 0 THEN
        resultado := resultado || 'AVISO: Nenhum dado encontrado na tabela temporária.' || E'\n';
        resultado := resultado || 'Execute primeiro: COPY dicionario.temp_csv_import FROM ''caminho/para/csv'' WITH (FORMAT CSV, HEADER TRUE);' || E'\n';
        RETURN resultado;
    END IF;
    
    -- PASSO 2: Migrar produtores únicos
    resultado := resultado || 'PASSO 2: Migrando produtores...' || E'\n';
    
    INSERT INTO dicionario.produtor (nome, instituicao, departamento)
    SELECT DISTINCT 
        COALESCE(NULLIF(trim(produtor), ''), 'Não informado'),
        COALESCE(NULLIF(trim(instituicao), ''), 'Não informado'),
        COALESCE(NULLIF(trim(departamento), ''), 'Não informado')
    FROM dicionario.temp_csv_import
    WHERE trim(produtor) IS NOT NULL
    ON CONFLICT DO NOTHING;
    
    GET DIAGNOSTICS contador = ROW_COUNT;
    resultado := resultado || 'Produtores inseridos: ' || contador || E'\n';
    
    -- PASSO 3: Migrar extensões não cadastradas
    resultado := resultado || 'PASSO 3: Verificando extensões...' || E'\n';
    
    INSERT INTO dicionario.extensao (nome, descricao, categoria)
    SELECT DISTINCT 
        CASE 
            WHEN lower(trim(extensao)) NOT LIKE '.%' THEN '.' || lower(trim(extensao))
            ELSE lower(trim(extensao))
        END,
        'Extensão importada do sistema legado',
        'outros'
    FROM dicionario.temp_csv_import
    WHERE trim(extensao) IS NOT NULL 
    AND NOT EXISTS (
        SELECT 1 FROM dicionario.extensao e 
        WHERE e.nome = CASE 
            WHEN lower(trim(temp_csv_import.extensao)) NOT LIKE '.%' THEN '.' || lower(trim(temp_csv_import.extensao))
            ELSE lower(trim(temp_csv_import.extensao))
        END
    );
    
    GET DIAGNOSTICS contador = ROW_COUNT;
    resultado := resultado || 'Novas extensões inseridas: ' || contador || E'\n' || E'\n';
    
    -- PASSO 4: Migrar arquivos
    resultado := resultado || 'PASSO 4: Migrando arquivos...' || E'\n';
    
    FOR rec IN 
        SELECT * FROM dicionario.temp_csv_import 
        WHERE trim(nome_arquivo) IS NOT NULL
    LOOP
        -- Buscar perfil baseado na extensão
        SELECT p.id INTO perfil_id
        FROM dicionario.perfil p
        JOIN dicionario.perfil_extensao pe ON p.id = pe.perfil_id
        JOIN dicionario.extensao e ON pe.extensao_id = e.id
        WHERE e.nome = CASE 
            WHEN lower(trim(rec.extensao)) NOT LIKE '.%' THEN '.' || lower(trim(rec.extensao))
            ELSE lower(trim(rec.extensao))
        END
        LIMIT 1;
        
        -- Se não encontrou perfil, usar 'outros'
        IF perfil_id IS NULL THEN
            SELECT id INTO perfil_id 
            FROM dicionario.perfil 
            WHERE nome = 'documentos_texto'
            LIMIT 1;
        END IF;
        
        -- Buscar extensão
        SELECT id INTO extensao_id
        FROM dicionario.extensao
        WHERE nome = CASE 
            WHEN lower(trim(rec.extensao)) NOT LIKE '.%' THEN '.' || lower(trim(rec.extensao))
            ELSE lower(trim(rec.extensao))
        END
        LIMIT 1;
        
        -- Buscar produtor
        SELECT id INTO produtor_id
        FROM dicionario.produtor
        WHERE nome = COALESCE(NULLIF(trim(rec.produtor), ''), 'Não informado')
        AND instituicao = COALESCE(NULLIF(trim(rec.instituicao), ''), 'Não informado')
        LIMIT 1;
        
        -- Inserir arquivo
        INSERT INTO dicionario.arquivo (
            nome_original,
            nome_fisico,
            caminho,
            tamanho_bytes,
            perfil_id,
            extensao_id,
            produtor_id,
            titulo,
            descricao,
            palavras_chave,
            status,
            publico,
            data_criacao,
            created_at
        ) VALUES (
            trim(rec.nome_arquivo),
            trim(rec.nome_arquivo), -- nome físico igual ao original por padrão
            COALESCE(NULLIF(trim(rec.caminho_completo), ''), '/legado/' || trim(rec.nome_arquivo)),
            CASE 
                WHEN rec.tamanho_bytes ~ '^[0-9]+$' THEN rec.tamanho_bytes::BIGINT
                ELSE NULL
            END,
            perfil_id,
            extensao_id,
            produtor_id,
            COALESCE(NULLIF(trim(rec.nome_arquivo), ''), 'Documento legado'),
            COALESCE(NULLIF(trim(rec.descricao), ''), 'Arquivo migrado do sistema legado'),
            CASE 
                WHEN trim(rec.palavras_chave) IS NOT NULL AND trim(rec.palavras_chave) != '' 
                THEN string_to_array(trim(rec.palavras_chave), ',')
                ELSE ARRAY['legado', 'migração']
            END,
            'aprovado', -- Status padrão para dados legados
            CASE 
                WHEN lower(trim(rec.publico)) IN ('true', 'sim', 's', '1', 'público') THEN TRUE
                WHEN lower(trim(rec.publico)) IN ('false', 'não', 'n', '0', 'privado') THEN FALSE
                ELSE TRUE -- Padrão público para dados legados
            END,
            CASE 
                WHEN rec.created_date ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}' THEN rec.created_date::DATE
                WHEN rec.data_modificacao ~ '^[0-9]{4}-[0-9]{2}-[0-9]{2}' THEN rec.data_modificacao::DATE
                ELSE CURRENT_DATE
            END,
            CURRENT_TIMESTAMP
        ) RETURNING id INTO novo_arquivo_id;
        
        contador := contador + 1;
        
        -- Log do progresso a cada 100 registros
        IF contador % 100 = 0 THEN
            resultado := resultado || 'Processados: ' || contador || ' registros...' || E'\n';
        END IF;
        
    END LOOP;
    
    resultado := resultado || 'Total de arquivos migrados: ' || contador || E'\n' || E'\n';
    
    -- PASSO 5: Estatísticas finais
    resultado := resultado || 'PASSO 5: Estatísticas da migração' || E'\n';
    resultado := resultado || '===============================' || E'\n';
    
    SELECT COUNT(*) INTO contador FROM dicionario.arquivo WHERE created_at >= CURRENT_DATE;
    resultado := resultado || 'Arquivos migrados hoje: ' || contador || E'\n';
    
    SELECT COUNT(*) INTO contador FROM dicionario.produtor;
    resultado := resultado || 'Total de produtores: ' || contador || E'\n';
    
    SELECT COUNT(*) INTO contador FROM dicionario.extensao;
    resultado := resultado || 'Total de extensões: ' || contador || E'\n';
    
    -- Estatística por perfil
    resultado := resultado || E'\nDistribuição por perfil:' || E'\n';
    FOR rec IN 
        SELECT p.nome, COUNT(a.id) as total
        FROM dicionario.perfil p
        LEFT JOIN dicionario.arquivo a ON p.id = a.perfil_id
        GROUP BY p.nome
        ORDER BY total DESC
    LOOP
        resultado := resultado || '- ' || rec.nome || ': ' || rec.total || E'\n';
    END LOOP;
    
    resultado := resultado || E'\n' || 'MIGRAÇÃO CONCLUÍDA COM SUCESSO!' || E'\n';
    resultado := resultado || '================================' || E'\n';
    
    RETURN resultado;
    
EXCEPTION
    WHEN OTHERS THEN
        resultado := resultado || E'\nERRO DURANTE A MIGRAÇÃO: ' || SQLERRM || E'\n';
        RAISE NOTICE '%', resultado;
        RETURN resultado;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- FUNÇÃO PARA VALIDAR DADOS ANTES DA MIGRAÇÃO
-- =============================================================================

CREATE OR REPLACE FUNCTION dicionario.validar_csv_legado()
RETURNS TEXT AS $$
DECLARE
    resultado TEXT := '';
    contador INTEGER;
    rec RECORD;
BEGIN
    resultado := 'VALIDAÇÃO DOS DADOS CSV LEGADOS' || E'\n';
    resultado := resultado || '================================' || E'\n';
    
    -- Verificar se existe dados na tabela temporária
    SELECT COUNT(*) INTO contador FROM dicionario.temp_csv_import;
    resultado := resultado || 'Total de registros: ' || contador || E'\n' || E'\n';
    
    IF contador = 0 THEN
        resultado := resultado || 'AVISO: Nenhum dado encontrado!' || E'\n';
        RETURN resultado;
    END IF;
    
    -- Verificar campos obrigatórios
    SELECT COUNT(*) INTO contador 
    FROM dicionario.temp_csv_import 
    WHERE trim(nome_arquivo) IS NULL OR trim(nome_arquivo) = '';
    resultado := resultado || 'Registros sem nome de arquivo: ' || contador || E'\n';
    
    SELECT COUNT(*) INTO contador 
    FROM dicionario.temp_csv_import 
    WHERE trim(extensao) IS NULL OR trim(extensao) = '';
    resultado := resultado || 'Registros sem extensão: ' || contador || E'\n';
    
    SELECT COUNT(*) INTO contador 
    FROM dicionario.temp_csv_import 
    WHERE trim(produtor) IS NULL OR trim(produtor) = '';
    resultado := resultado || 'Registros sem produtor: ' || contador || E'\n' || E'\n';
    
    -- Estatísticas por extensão
    resultado := resultado || 'DISTRIBUIÇÃO POR EXTENSÃO:' || E'\n';
    FOR rec IN 
        SELECT 
            COALESCE(NULLIF(trim(extensao), ''), 'sem_extensao') as ext,
            COUNT(*) as total
        FROM dicionario.temp_csv_import
        GROUP BY extensao
        ORDER BY total DESC
        LIMIT 10
    LOOP
        resultado := resultado || '- ' || rec.ext || ': ' || rec.total || E'\n';
    END LOOP;
    
    resultado := resultado || E'\n' || 'DISTRIBUIÇÃO POR PRODUTOR:' || E'\n';
    FOR rec IN 
        SELECT 
            COALESCE(NULLIF(trim(produtor), ''), 'sem_produtor') as prod,
            COUNT(*) as total
        FROM dicionario.temp_csv_import
        GROUP BY produtor
        ORDER BY total DESC
        LIMIT 10
    LOOP
        resultado := resultado || '- ' || rec.prod || ': ' || rec.total || E'\n';
    END LOOP;
    
    -- Verificar duplicatas
    SELECT COUNT(*) INTO contador
    FROM (
        SELECT nome_arquivo, COUNT(*)
        FROM dicionario.temp_csv_import
        GROUP BY nome_arquivo
        HAVING COUNT(*) > 1
    ) duplicatas;
    resultado := resultado || E'\n' || 'Arquivos duplicados: ' || contador || E'\n';
    
    resultado := resultado || E'\n' || 'VALIDAÇÃO CONCLUÍDA' || E'\n';
    
    RETURN resultado;
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- FUNÇÃO PARA LIMPEZA DE DADOS TEMPORÁRIOS
-- =============================================================================

CREATE OR REPLACE FUNCTION dicionario.limpar_dados_temporarios()
RETURNS TEXT AS $$
BEGIN
    DELETE FROM dicionario.temp_csv_import;
    RETURN 'Dados temporários removidos com sucesso.';
END;
$$ LANGUAGE plpgsql;

-- =============================================================================
-- COMANDOS PARA EXECUÇÃO DA MIGRAÇÃO
-- =============================================================================

/*
PASSOS PARA EXECUTAR A MIGRAÇÃO:

1. Preparar o arquivo CSV legado com as colunas:
   nome_arquivo, caminho_completo, tamanho_bytes, data_modificacao, extensao, 
   tipo_conteudo, produtor, departamento, instituicao, descricao, 
   palavras_chave, publico, observacoes, created_date

2. Carregar dados do CSV:
   COPY dicionario.temp_csv_import(nome_arquivo, caminho_completo, tamanho_bytes, 
   data_modificacao, extensao, tipo_conteudo, produtor, departamento, instituicao, 
   descricao, palavras_chave, publico, observacoes, created_date) 
   FROM 'C:\caminho\para\dados_legados.csv' 
   WITH (FORMAT CSV, HEADER TRUE, DELIMITER ',', ENCODING 'UTF8');

3. Validar dados antes da migração:
   SELECT dicionario.validar_csv_legado();

4. Executar a migração:
   SELECT dicionario.migrar_dados_csv_legado();

5. Limpar dados temporários:
   SELECT dicionario.limpar_dados_temporarios();

6. Verificar resultado:
   SELECT COUNT(*) FROM dicionario.arquivo;
   SELECT * FROM dicionario.view_catalogo_base LIMIT 10;
*/

-- =============================================================================
-- VIEWS PARA MONITORAMENTO DA MIGRAÇÃO
-- =============================================================================

CREATE VIEW dicionario.view_migração_status AS
SELECT 
    'Arquivos totais' as item,
    COUNT(*)::TEXT as valor
FROM dicionario.arquivo
UNION ALL
SELECT 
    'Arquivos migrados hoje' as item,
    COUNT(*)::TEXT as valor
FROM dicionario.arquivo 
WHERE created_at::DATE = CURRENT_DATE
UNION ALL
SELECT 
    'Produtores únicos' as item,
    COUNT(*)::TEXT as valor
FROM dicionario.produtor
UNION ALL
SELECT 
    'Extensões suportadas' as item,
    COUNT(*)::TEXT as valor
FROM dicionario.extensao
UNION ALL
SELECT 
    'Registros temporários' as item,
    COUNT(*)::TEXT as valor
FROM dicionario.temp_csv_import;

COMMENT ON VIEW dicionario.view_migração_status IS 'Visão geral do status da migração';

-- View para arquivos problemáticos
CREATE VIEW dicionario.view_arquivos_problemas AS
SELECT 
    a.id,
    a.nome_original,
    a.caminho,
    CASE 
        WHEN a.tamanho_bytes IS NULL THEN 'Tamanho não informado'
        WHEN a.perfil_id IS NULL THEN 'Perfil não identificado'
        WHEN a.extensao_id IS NULL THEN 'Extensão não cadastrada'
        WHEN a.produtor_id IS NULL THEN 'Produtor não informado'
        ELSE 'OK'
    END as problema,
    a.created_at
FROM dicionario.arquivo a
WHERE a.tamanho_bytes IS NULL 
   OR a.perfil_id IS NULL 
   OR a.extensao_id IS NULL 
   OR a.produtor_id IS NULL;

COMMENT ON VIEW dicionario.view_arquivos_problemas IS 'Arquivos com dados incompletos ou problemáticos';

-- =============================================================================
-- DADOS DE EXEMPLO PARA TESTE DA MIGRAÇÃO
-- =============================================================================

-- Inserir dados de exemplo na tabela temporária para teste
INSERT INTO dicionario.temp_csv_import (
    nome_arquivo, caminho_completo, tamanho_bytes, extensao, 
    produtor, instituicao, departamento, descricao, palavras_chave, publico
) VALUES 
('relatorio_anual_2023.pdf', '/documentos/relatorios/relatorio_anual_2023.pdf', '2048576', '.pdf', 
 'João Silva', 'Secretaria de Planejamento', 'Departamento de Estatística', 
 'Relatório anual das atividades 2023', 'relatório,anual,2023,atividades', 'true'),
 
('dados_populacional.xlsx', '/planilhas/dados_populacional.xlsx', '1024000', '.xlsx',
 'Maria Santos', 'Instituto de Pesquisas', 'Divisão de Demografia',
 'Dados populacionais por município', 'população,demografia,município', 'true'),
 
('mapa_uso_solo.shp', '/gis/mapas/mapa_uso_solo.shp', '5120000', '.shp',
 'Carlos Oliveira', 'Secretaria de Meio Ambiente', 'Departamento de Geoprocessamento',
 'Mapa de uso e ocupação do solo', 'mapa,uso do solo,gis,shapefile', 'false');

-- Comentários finais
COMMENT ON FUNCTION dicionario.migrar_dados_csv_legado() IS 'Função principal para migração de dados CSV legados';
COMMENT ON FUNCTION dicionario.validar_csv_legado() IS 'Validação prévia dos dados antes da migração';
COMMENT ON TABLE dicionario.temp_csv_import IS 'Tabela temporária para importação de dados CSV legados';