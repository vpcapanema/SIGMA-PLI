-- =====================================================
-- SCRIPT DE EXPLORAÇÃO DO BANCO SIGMA-PLI
-- =====================================================

-- 1. LISTAR TODOS OS SCHEMAS
SELECT schema_name 
FROM information_schema.schemata 
WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
ORDER BY schema_name;

-- 2. LISTAR TABELAS DO SCHEMA DICIONARIO
SELECT table_name, table_type
FROM information_schema.tables 
WHERE table_schema = 'dicionario'
ORDER BY table_name;

-- 3. ESTRUTURA DA TABELA ARQUIVO (PRINCIPAL)
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default,
    ordinal_position
FROM information_schema.columns 
WHERE table_schema = 'dicionario' 
AND table_name = 'arquivo'
ORDER BY ordinal_position;

-- 4. ESTRUTURA DA TABELA PRODUTOR
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default,
    ordinal_position
FROM information_schema.columns 
WHERE table_schema = 'dicionario' 
AND table_name = 'produtor'
ORDER BY ordinal_position;

-- 5. ESTRUTURA DA TABELA PERFIL
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default,
    ordinal_position
FROM information_schema.columns 
WHERE table_schema = 'dicionario' 
AND table_name = 'perfil'
ORDER BY ordinal_position;

-- 6. ESTRUTURA DA TABELA EXTENSAO
SELECT 
    column_name,
    data_type,
    character_maximum_length,
    is_nullable,
    column_default,
    ordinal_position
FROM information_schema.columns 
WHERE table_schema = 'dicionario' 
AND table_name = 'extensao'
ORDER BY ordinal_position;

-- 7. LISTAR TODAS AS CONSTRAINTS (CHAVES PRIMÁRIAS, ESTRANGEIRAS, ETC)
SELECT 
    tc.constraint_name,
    tc.table_name,
    tc.constraint_type,
    kcu.column_name,
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu 
    ON tc.constraint_name = kcu.constraint_name
LEFT JOIN information_schema.constraint_column_usage AS ccu 
    ON ccu.constraint_name = tc.constraint_name
WHERE tc.table_schema = 'dicionario'
ORDER BY tc.table_name, tc.constraint_type;

-- 8. LISTAR TODAS AS TABELAS COM PREFIXO ESTRUTURA_
SELECT table_name
FROM information_schema.tables 
WHERE table_schema = 'dicionario'
AND table_name LIKE 'estrutura_%'
ORDER BY table_name;

-- 9. LISTAR TODAS AS TABELAS COM PREFIXO CONTEUDO_
SELECT table_name
FROM information_schema.tables 
WHERE table_schema = 'dicionario'
AND table_name LIKE 'conteudo_%'
ORDER BY table_name;

-- 10. VERIFICAR SE EXISTEM DADOS NAS TABELAS PRINCIPAIS
SELECT 
    'arquivo' as tabela, 
    COUNT(*) as total_registros 
FROM dicionario.arquivo
UNION ALL
SELECT 
    'produtor' as tabela, 
    COUNT(*) as total_registros 
FROM dicionario.produtor
UNION ALL
SELECT 
    'perfil' as tabela, 
    COUNT(*) as total_registros 
FROM dicionario.perfil
UNION ALL
SELECT 
    'extensao' as tabela, 
    COUNT(*) as total_registros 
FROM dicionario.extensao;
