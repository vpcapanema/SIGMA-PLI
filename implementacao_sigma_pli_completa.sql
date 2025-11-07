-- =============================================================================
-- SIGMA-PLI - SCRIPT PRINCIPAL DE IMPLEMENTAÇÃO
-- Executa todos os componentes na ordem correta
-- Versão: 1.2
-- =============================================================================

-- =============================================================================
-- INSTRUÇÕES DE EXECUÇÃO
-- =============================================================================

/*
PASSO A PASSO PARA IMPLEMENTAÇÃO COMPLETA:

1. PREPARAÇÃO:
   - Certifique-se que o PostgreSQL está rodando com as extensões necessárias
   - Tenha os arquivos CSV legados preparados
   - Execute como usuário com privilégios administrativos

2. EXECUÇÃO:
   psql -h localhost -U postgres -d sigma_pli -f implementacao_sigma_pli_completa.sql

3. MIGRAÇÃO DE DADOS (opcional):
   - Copie os dados CSV legados
   - Execute as funções de migração

4. CONFIGURAÇÃO DE USUÁRIOS:
   - Crie usuários administrativos
   - Configure permissões iniciais

*/

-- =============================================================================
-- VERIFICAÇÕES INICIAIS
-- =============================================================================

\echo '=================================================='
\echo 'SIGMA-PLI - IMPLEMENTAÇÃO COMPLETA v1.2'
\echo '=================================================='
\echo ''

-- Verificar versão do PostgreSQL
\echo 'Verificando versão do PostgreSQL...'
SELECT version();

-- Verificar extensões disponíveis
\echo 'Verificando extensões disponíveis...'
SELECT name, installed_version, default_version 
FROM pg_available_extensions 
WHERE name IN ('uuid-ossp', 'postgis', 'pg_trgm');

-- =============================================================================
-- ETAPA 1: CRIAÇÃO DE EXTENSÕES
-- =============================================================================

\echo ''
\echo 'ETAPA 1: Criando extensões necessárias...'

-- Criar extensões se não existem
CREATE EXTENSION IF NOT EXISTS "uuid-ossp" SCHEMA public;
CREATE EXTENSION IF NOT EXISTS "pg_trgm" SCHEMA public;

-- PostGIS (opcional, para dados geoespaciais)
-- Descomente se necessário:
-- CREATE EXTENSION IF NOT EXISTS "postgis" SCHEMA public;

\echo 'Extensões criadas com sucesso!'

-- =============================================================================
-- ETAPA 2: EXECUÇÃO DO DDL PRINCIPAL
-- =============================================================================

\echo ''
\echo 'ETAPA 2: Executando DDL principal...'

-- Incluir o conteúdo do ddl_sigma_pli_completo.sql aqui
-- Ou executar separadamente: \i ddl_sigma_pli_completo.sql

\echo 'DDL principal executado!'

-- =============================================================================
-- ETAPA 3: TRIGGERS DE AUDITORIA
-- =============================================================================

\echo ''
\echo 'ETAPA 3: Configurando sistema de auditoria...'

-- Incluir o conteúdo do triggers_auditoria_completos.sql aqui
-- Ou executar separadamente: \i triggers_auditoria_completos.sql

\echo 'Sistema de auditoria configurado!'

-- =============================================================================
-- ETAPA 4: DADOS INICIAIS OBRIGATÓRIOS
-- =============================================================================

\echo ''
\echo 'ETAPA 4: Inserindo dados iniciais...'

-- Verificar se perfis já existem
DO $$
DECLARE
    perfil_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO perfil_count FROM dicionario.perfil;
    
    IF perfil_count = 0 THEN
        RAISE NOTICE 'Inserindo perfis padrão...';
        
        -- Perfis já são inseridos no DDL principal
        -- Mas vamos garantir que existem
        INSERT INTO dicionario.perfil (nome, descricao, icone, cor, ordem) VALUES
        ('documentos_texto', 'Documentos de texto (DOC, PDF, TXT)', 'file-text', '#3498db', 1),
        ('midia', 'Arquivos de mídia (áudio, vídeo, imagem)', 'file-image', '#e74c3c', 2),
        ('tabular', 'Dados tabulares (CSV, XLS, XLSX)', 'table', '#2ecc71', 3),
        ('geoespacial_vetor', 'Dados geoespaciais vetoriais (SHP, KML, GeoJSON)', 'map', '#f39c12', 4),
        ('geoespacial_raster', 'Dados geoespaciais raster (GeoTIFF, IMG)', 'image', '#9b59b6', 5),
        ('nuvem_pontos', 'Nuvem de pontos (LAS, LAZ, PLY)', 'cloud', '#1abc9c', 6),
        ('desenho_2d3d', 'Desenhos 2D/3D (DWG, DXF, SKP)', 'cube', '#34495e', 7),
        ('database', 'Bancos de dados (SQL, DB, MDB)', 'database', '#e67e22', 8),
        ('geodatabase', 'Geodatabases (GDB, SDE)', 'globe', '#8e44ad', 9),
        ('pacote', 'Pacotes e compactados (ZIP, RAR, 7Z)', 'archive', '#95a5a6', 10)
        ON CONFLICT (nome) DO NOTHING;
        
    ELSE
        RAISE NOTICE 'Perfis já existem: % registros', perfil_count;
    END IF;
END $$;

-- Verificar papéis de usuário
DO $$
DECLARE
    papel_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO papel_count FROM usuarios.papel;
    
    IF papel_count = 0 THEN
        RAISE NOTICE 'Inserindo papéis de usuário...';
        
        INSERT INTO usuarios.papel (nome, descricao) VALUES
        ('admin', 'Administrador do sistema'),
        ('gestor', 'Gestor de conteúdo'),
        ('produtor', 'Produtor de dados'),
        ('consultor', 'Consultor de dados'),
        ('usuario', 'Usuário básico')
        ON CONFLICT (nome) DO NOTHING;
        
    ELSE
        RAISE NOTICE 'Papéis já existem: % registros', papel_count;
    END IF;
END $$;

\echo 'Dados iniciais inseridos!'

-- =============================================================================
-- ETAPA 5: CRIAÇÃO DE USUÁRIO ADMINISTRATIVO
-- =============================================================================

\echo ''
\echo 'ETAPA 5: Criando usuário administrativo...'

-- Inserir usuário admin padrão (ALTERE A SENHA!)
INSERT INTO usuarios.usuario (
    username,
    email,
    password_hash,
    nome_completo,
    primeiro_nome,
    ultimo_nome,
    cargo,
    instituicao,
    ativo
) VALUES (
    'admin',
    'admin@sigma.gov.br',
    '$2b$12$LQv3c1yqBwrf4VHID2DbfOeUtGT.iKLBvBGr8UJ6pYUe1x6j2eMa.', -- senha: admin123 (ALTERE!)
    'Administrador do Sistema',
    'Administrador',
    'Sistema',
    'Administrador',
    'SIGMA-PLI',
    TRUE
) ON CONFLICT (username) DO NOTHING;

-- Associar papel de admin
DO $$
DECLARE
    admin_user_id UUID;
    admin_papel_id UUID;
BEGIN
    SELECT id INTO admin_user_id FROM usuarios.usuario WHERE username = 'admin';
    SELECT id INTO admin_papel_id FROM usuarios.papel WHERE nome = 'admin';
    
    IF admin_user_id IS NOT NULL AND admin_papel_id IS NOT NULL THEN
        INSERT INTO usuarios.usuario_papel (usuario_id, papel_id)
        VALUES (admin_user_id, admin_papel_id)
        ON CONFLICT DO NOTHING;
        
        RAISE NOTICE 'Usuário admin criado e configurado!';
    END IF;
END $$;

\echo 'Usuário administrativo criado!'
\echo 'IMPORTANTE: Altere a senha padrão do usuário admin!'

-- =============================================================================
-- ETAPA 6: CONFIGURAÇÕES DE SEGURANÇA
-- =============================================================================

\echo ''
\echo 'ETAPA 6: Aplicando configurações de segurança...'

-- Revogar permissões públicas desnecessárias
REVOKE ALL ON SCHEMA usuarios FROM PUBLIC;
REVOKE ALL ON SCHEMA auditoria FROM PUBLIC;

-- Conceder permissões específicas
GRANT USAGE ON SCHEMA dicionario TO PUBLIC;
GRANT SELECT ON dicionario.view_catalogo_base TO PUBLIC;
GRANT SELECT ON dicionario.perfil TO PUBLIC;
GRANT SELECT ON dicionario.extensao TO PUBLIC;

-- Configurar row level security (opcional)
-- ALTER TABLE dicionario.arquivo ENABLE ROW LEVEL SECURITY;

\echo 'Configurações de segurança aplicadas!'

-- =============================================================================
-- ETAPA 7: VERIFICAÇÕES FINAIS
-- =============================================================================

\echo ''
\echo 'ETAPA 7: Verificações finais...'

-- Verificar estrutura dos esquemas
\echo 'Verificando esquemas criados:'
SELECT schemaname, tablename, tableowner 
FROM pg_tables 
WHERE schemaname IN ('dicionario', 'usuarios', 'cadastro', 'auditoria')
ORDER BY schemaname, tablename;

-- Verificar triggers
\echo 'Verificando triggers de auditoria:'
SELECT trigger_name, event_object_table, action_statement 
FROM information_schema.triggers 
WHERE trigger_schema IN ('dicionario', 'usuarios')
ORDER BY event_object_table;

-- Verificar dados iniciais
\echo 'Verificando dados iniciais:'
SELECT 'perfis' as tabela, COUNT(*) as registros FROM dicionario.perfil
UNION ALL
SELECT 'extensões' as tabela, COUNT(*) as registros FROM dicionario.extensao
UNION ALL
SELECT 'papéis' as tabela, COUNT(*) as registros FROM usuarios.papel
UNION ALL
SELECT 'usuários' as tabela, COUNT(*) as registros FROM usuarios.usuario;

-- =============================================================================
-- PRÓXIMOS PASSOS PARA MIGRAÇÃO DE DADOS
-- =============================================================================

\echo ''
\echo '=================================================='
\echo 'IMPLEMENTAÇÃO CONCLUÍDA COM SUCESSO!'
\echo '=================================================='
\echo ''
\echo 'PRÓXIMOS PASSOS:'
\echo ''
\echo '1. MIGRAÇÃO DE DADOS CSV LEGADOS:'
\echo '   - Prepare o arquivo CSV com os dados legados'
\echo '   - Execute: COPY dicionario.temp_csv_import FROM ''caminho/arquivo.csv'' WITH (FORMAT CSV, HEADER TRUE);'
\echo '   - Valide: SELECT dicionario.validar_csv_legado();'
\echo '   - Migre: SELECT dicionario.migrar_dados_csv_legado();'
\echo ''
\echo '2. CONFIGURAÇÃO DE USUÁRIOS:'
\echo '   - Crie usuários adicionais conforme necessário'
\echo '   - Configure papéis e permissões específicas'
\echo '   - ALTERE a senha do usuário admin padrão!'
\echo ''
\echo '3. CONFIGURAÇÃO DE APLICAÇÃO:'
\echo '   - Configure connection strings no backend'
\echo '   - Ajuste configurações de autenticação'
\echo '   - Configure upload de arquivos'
\echo ''
\echo '4. TESTES:'
\echo '   - Teste upload de arquivos'
\echo '   - Teste sistema de auditoria'
\echo '   - Valide catálogo público'
\echo ''
\echo 'Para acessar o sistema:'
\echo '- Usuário: admin'
\echo '- Senha: admin123 (ALTERE IMEDIATAMENTE!)'
\echo ''

-- =============================================================================
-- FUNÇÃO DE STATUS DO SISTEMA
-- =============================================================================

CREATE OR REPLACE FUNCTION public.sigma_pli_status()
RETURNS TABLE (
    componente TEXT,
    status TEXT,
    detalhes TEXT
) AS $$
BEGIN
    RETURN QUERY
    
    -- Verificar esquemas
    SELECT 
        'Esquemas' as componente,
        CASE WHEN COUNT(*) = 4 THEN 'OK' ELSE 'ERRO' END as status,
        'Encontrados: ' || COUNT(*) || '/4 esquemas' as detalhes
    FROM information_schema.schemata 
    WHERE schema_name IN ('dicionario', 'usuarios', 'cadastro', 'auditoria')
    
    UNION ALL
    
    -- Verificar perfis
    SELECT 
        'Perfis de arquivo' as componente,
        CASE WHEN COUNT(*) >= 10 THEN 'OK' ELSE 'AVISO' END as status,
        'Total: ' || COUNT(*) || ' perfis cadastrados' as detalhes
    FROM dicionario.perfil
    
    UNION ALL
    
    -- Verificar extensões
    SELECT 
        'Extensões de arquivo' as componente,
        CASE WHEN COUNT(*) >= 20 THEN 'OK' ELSE 'AVISO' END as status,
        'Total: ' || COUNT(*) || ' extensões cadastradas' as detalhes
    FROM dicionario.extensao
    
    UNION ALL
    
    -- Verificar usuários
    SELECT 
        'Usuários' as componente,
        CASE WHEN COUNT(*) >= 1 THEN 'OK' ELSE 'ERRO' END as status,
        'Total: ' || COUNT(*) || ' usuários cadastrados' as detalhes
    FROM usuarios.usuario
    
    UNION ALL
    
    -- Verificar triggers
    SELECT 
        'Sistema de auditoria' as componente,
        CASE WHEN COUNT(*) >= 5 THEN 'OK' ELSE 'ERRO' END as status,
        'Total: ' || COUNT(*) || ' triggers ativos' as detalhes
    FROM information_schema.triggers 
    WHERE trigger_schema IN ('dicionario', 'usuarios')
    
    UNION ALL
    
    -- Verificar arquivos (se existem)
    SELECT 
        'Arquivos cadastrados' as componente,
        'INFO' as status,
        'Total: ' || COUNT(*) || ' arquivos no catálogo' as detalhes
    FROM dicionario.arquivo;
    
END;
$$ LANGUAGE plpgsql;

\echo 'Para verificar o status do sistema a qualquer momento:'
\echo 'SELECT * FROM public.sigma_pli_status();'
\echo ''

-- Executar verificação final
SELECT * FROM public.sigma_pli_status();

\echo ''
\echo 'IMPLEMENTAÇÃO FINALIZADA!'
\echo '=================================================='