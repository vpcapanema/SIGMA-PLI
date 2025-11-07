-- =============================================================================
-- SIGMA-PLI - DDL COMPLETO (v1.2)
-- Baseado no documento teórico-conceitual
-- =============================================================================

-- Extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "postgis";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- =============================================================================
-- ESQUEMAS
-- =============================================================================

CREATE SCHEMA IF NOT EXISTS dicionario;
CREATE SCHEMA IF NOT EXISTS usuarios;
CREATE SCHEMA IF NOT EXISTS cadastro;
CREATE SCHEMA IF NOT EXISTS auditoria;

COMMENT ON SCHEMA dicionario IS 'Núcleo de metadados de arquivos do SIGMA-PLI';
COMMENT ON SCHEMA usuarios IS 'Sistema de usuários, papéis e permissões (provisório)';
COMMENT ON SCHEMA cadastro IS 'Instituições, pessoas, produtos e entregas (provisório)';
COMMENT ON SCHEMA auditoria IS 'Logs e rastreamento de operações';

-- =============================================================================
-- ESQUEMA DICIONARIO - TABELAS FIXAS
-- =============================================================================

-- Tabela: perfil
CREATE TABLE dicionario.perfil (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT,
    icone TEXT,
    cor TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    ordem INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE dicionario.perfil IS 'Categorias semânticas de arquivos (tabular, geoespacial_vetor, etc.)';

-- Inserir perfis padrão
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
('pacote', 'Pacotes e compactados (ZIP, RAR, 7Z)', 'archive', '#95a5a6', 10);

-- Tabela: extensao
CREATE TABLE dicionario.extensao (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT,
    mime_type TEXT,
    categoria TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE dicionario.extensao IS 'Extensões de arquivo aceitas pelo sistema';

-- Inserir extensões por perfil
INSERT INTO dicionario.extensao (nome, descricao, mime_type, categoria) VALUES
-- Documentos texto
('.pdf', 'Portable Document Format', 'application/pdf', 'documentos_texto'),
('.doc', 'Microsoft Word 97-2003', 'application/msword', 'documentos_texto'),
('.docx', 'Microsoft Word', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'documentos_texto'),
('.txt', 'Plain Text', 'text/plain', 'documentos_texto'),
('.rtf', 'Rich Text Format', 'application/rtf', 'documentos_texto'),

-- Mídia
('.jpg', 'JPEG Image', 'image/jpeg', 'midia'),
('.jpeg', 'JPEG Image', 'image/jpeg', 'midia'),
('.png', 'PNG Image', 'image/png', 'midia'),
('.gif', 'GIF Image', 'image/gif', 'midia'),
('.mp4', 'MP4 Video', 'video/mp4', 'midia'),
('.mp3', 'MP3 Audio', 'audio/mpeg', 'midia'),

-- Tabular
('.csv', 'Comma Separated Values', 'text/csv', 'tabular'),
('.xls', 'Microsoft Excel 97-2003', 'application/vnd.ms-excel', 'tabular'),
('.xlsx', 'Microsoft Excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'tabular'),
('.ods', 'OpenDocument Spreadsheet', 'application/vnd.oasis.opendocument.spreadsheet', 'tabular'),

-- Geoespacial vetor
('.shp', 'Shapefile', 'application/x-esri-shapefile', 'geoespacial_vetor'),
('.kml', 'Keyhole Markup Language', 'application/vnd.google-earth.kml+xml', 'geoespacial_vetor'),
('.kmz', 'Keyhole Markup Language (Zipped)', 'application/vnd.google-earth.kmz', 'geoespacial_vetor'),
('.geojson', 'GeoJSON', 'application/geo+json', 'geoespacial_vetor'),
('.gpx', 'GPS Exchange Format', 'application/gpx+xml', 'geoespacial_vetor'),

-- Geoespacial raster
('.tif', 'Tagged Image File Format', 'image/tiff', 'geoespacial_raster'),
('.tiff', 'Tagged Image File Format', 'image/tiff', 'geoespacial_raster'),
('.geotiff', 'GeoTIFF', 'image/tiff', 'geoespacial_raster'),
('.img', 'ERDAS Imagine', 'application/octet-stream', 'geoespacial_raster'),

-- Pacotes
('.zip', 'ZIP Archive', 'application/zip', 'pacote'),
('.rar', 'RAR Archive', 'application/x-rar-compressed', 'pacote'),
('.7z', '7-Zip Archive', 'application/x-7z-compressed', 'pacote');

-- Tabela: perfil_extensao (relacionamento N:N)
CREATE TABLE dicionario.perfil_extensao (
    perfil_id UUID REFERENCES dicionario.perfil(id) ON DELETE CASCADE,
    extensao_id UUID REFERENCES dicionario.extensao(id) ON DELETE CASCADE,
    PRIMARY KEY (perfil_id, extensao_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE dicionario.perfil_extensao IS 'Relacionamento entre perfis e extensões aceitas';

-- Popular relacionamentos perfil-extensão
WITH perfil_ext AS (
    SELECT p.id as perfil_id, e.id as extensao_id
    FROM dicionario.perfil p
    JOIN dicionario.extensao e ON e.categoria = p.nome
)
INSERT INTO dicionario.perfil_extensao (perfil_id, extensao_id)
SELECT perfil_id, extensao_id FROM perfil_ext;

-- Tabela: produtor
CREATE TABLE dicionario.produtor (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    email TEXT,
    telefone TEXT,
    instituicao TEXT,
    departamento TEXT,
    cargo TEXT,
    observacoes TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE dicionario.produtor IS 'Produtores/responsáveis pelos arquivos';

-- Tabela: arquivo (principal)
CREATE TABLE dicionario.arquivo (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome_original TEXT NOT NULL,
    nome_fisico TEXT NOT NULL UNIQUE,
    caminho TEXT NOT NULL,
    tamanho_bytes BIGINT,
    hash_md5 TEXT,
    hash_sha256 TEXT,
    mime_type TEXT,
    encoding TEXT,
    perfil_id UUID REFERENCES dicionario.perfil(id),
    extensao_id UUID REFERENCES dicionario.extensao(id),
    produtor_id UUID REFERENCES dicionario.produtor(id),
    
    -- Metadados básicos
    titulo TEXT,
    descricao TEXT,
    palavras_chave TEXT[],
    idioma TEXT DEFAULT 'pt-BR',
    data_criacao DATE,
    data_modificacao DATE,
    
    -- Status e controle
    status TEXT DEFAULT 'pendente' CHECK (status IN ('pendente', 'aprovado', 'rejeitado', 'arquivado')),
    publico BOOLEAN DEFAULT FALSE,
    versao INTEGER DEFAULT 1,
    arquivo_pai_id UUID REFERENCES dicionario.arquivo(id),
    
    -- Auditoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by UUID,
    updated_by UUID
);

COMMENT ON TABLE dicionario.arquivo IS 'Tabela principal de arquivos do sistema';

-- =============================================================================
-- TABELAS ESTRUTURA E CONTEUDO POR PERFIL
-- =============================================================================

-- DOCUMENTOS_TEXTO
CREATE TABLE dicionario.estrutura__documentos_texto (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    arquivo_id UUID REFERENCES dicionario.arquivo(id) ON DELETE CASCADE,
    numero_paginas INTEGER,
    tem_ocr BOOLEAN DEFAULT FALSE,
    protegido_senha BOOLEAN DEFAULT FALSE,
    versao_aplicacao TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dicionario.conteudo__documentos_texto (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    estrutura_id UUID REFERENCES dicionario.estrutura__documentos_texto(id) ON DELETE CASCADE,
    assunto TEXT,
    autor TEXT,
    categoria_documento TEXT,
    nivel_confidencialidade TEXT,
    palavras_chave_especificas TEXT[],
    resumo TEXT,
    data_documento DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- MIDIA
CREATE TABLE dicionario.estrutura__midia (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    arquivo_id UUID REFERENCES dicionario.arquivo(id) ON DELETE CASCADE,
    largura INTEGER,
    altura INTEGER,
    duracao_segundos INTEGER,
    taxa_bits INTEGER,
    codec TEXT,
    fps FLOAT,
    canais_audio INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dicionario.conteudo__midia (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    estrutura_id UUID REFERENCES dicionario.estrutura__midia(id) ON DELETE CASCADE,
    tema TEXT,
    localizacao TEXT,
    data_captura TIMESTAMP,
    equipamento TEXT,
    coordenadas GEOMETRY(POINT, 4326),
    altitude FLOAT,
    direitos_autorais TEXT,
    licenca TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- TABULAR
CREATE TABLE dicionario.estrutura__tabular (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    arquivo_id UUID REFERENCES dicionario.arquivo(id) ON DELETE CASCADE,
    numero_linhas INTEGER,
    numero_colunas INTEGER,
    cabecalho JSONB, -- Array com nomes das colunas
    delimitador TEXT DEFAULT ',',
    encoding_detectado TEXT,
    primeira_linha_cabecalho BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dicionario.conteudo__tabular (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    estrutura_id UUID REFERENCES dicionario.estrutura__tabular(id) ON DELETE CASCADE,
    fonte_dados TEXT,
    metodologia_coleta TEXT,
    periodicidade TEXT,
    cobertura_temporal_inicio DATE,
    cobertura_temporal_fim DATE,
    cobertura_geografica TEXT,
    unidade_observacao TEXT,
    variaveis JSONB, -- Descrição das variáveis/colunas
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GEOESPACIAL_VETOR
CREATE TABLE dicionario.estrutura__geoespacial_vetor (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    arquivo_id UUID REFERENCES dicionario.arquivo(id) ON DELETE CASCADE,
    srid INTEGER DEFAULT 4326,
    tipo_geometria TEXT, -- POINT, LINESTRING, POLYGON, etc.
    numero_features INTEGER,
    bbox GEOMETRY(POLYGON, 4326),
    projecao TEXT,
    sistema_coordenadas TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dicionario.conteudo__geoespacial_vetor (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    estrutura_id UUID REFERENCES dicionario.estrutura__geoespacial_vetor(id) ON DELETE CASCADE,
    tema_geografico TEXT,
    escala TEXT,
    data_levantamento DATE,
    precisao_horizontal FLOAT,
    precisao_vertical FLOAT,
    datum TEXT,
    responsavel_levantamento TEXT,
    metodo_aquisicao TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GEOESPACIAL_RASTER
CREATE TABLE dicionario.estrutura__geoespacial_raster (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    arquivo_id UUID REFERENCES dicionario.arquivo(id) ON DELETE CASCADE,
    largura_pixels INTEGER,
    altura_pixels INTEGER,
    numero_bandas INTEGER,
    resolucao_x FLOAT,
    resolucao_y FLOAT,
    srid INTEGER DEFAULT 4326,
    bbox GEOMETRY(POLYGON, 4326),
    tipo_pixel TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dicionario.conteudo__geoespacial_raster (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    estrutura_id UUID REFERENCES dicionario.estrutura__geoespacial_raster(id) ON DELETE CASCADE,
    sensor TEXT,
    satelite TEXT,
    data_imageamento TIMESTAMP,
    cobertura_nuvens_percent FLOAT,
    processamento_aplicado TEXT,
    bandas_espectrais JSONB,
    resolucao_radiometrica INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- NUVEM_PONTOS
CREATE TABLE dicionario.estrutura__nuvem_pontos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    arquivo_id UUID REFERENCES dicionario.arquivo(id) ON DELETE CASCADE,
    numero_pontos BIGINT,
    tem_cor BOOLEAN DEFAULT FALSE,
    tem_intensidade BOOLEAN DEFAULT FALSE,
    tem_classificacao BOOLEAN DEFAULT FALSE,
    bbox GEOMETRY(POLYGON, 4326),
    densidade_pontos_m2 FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dicionario.conteudo__nuvem_pontos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    estrutura_id UUID REFERENCES dicionario.estrutura__nuvem_pontos(id) ON DELETE CASCADE,
    metodo_aquisicao TEXT, -- LiDAR, fotogrametria, etc.
    equipamento TEXT,
    data_levantamento DATE,
    precisao_vertical FLOAT,
    precisao_horizontal FLOAT,
    area_levantamento FLOAT,
    finalidade TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DESENHO_2D3D
CREATE TABLE dicionario.estrutura__desenho_2d3d (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    arquivo_id UUID REFERENCES dicionario.arquivo(id) ON DELETE CASCADE,
    versao_cad TEXT,
    unidade_medida TEXT,
    tem_3d BOOLEAN DEFAULT FALSE,
    numero_layers INTEGER,
    numero_blocos INTEGER,
    bbox GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dicionario.conteudo__desenho_2d3d (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    estrutura_id UUID REFERENCES dicionario.estrutura__desenho_2d3d(id) ON DELETE CASCADE,
    tipo_projeto TEXT,
    disciplina TEXT,
    fase_projeto TEXT,
    escala_principal TEXT,
    data_projeto DATE,
    revisao TEXT,
    responsavel_tecnico TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DATABASE
CREATE TABLE dicionario.estrutura__database (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    arquivo_id UUID REFERENCES dicionario.arquivo(id) ON DELETE CASCADE,
    sgbd TEXT,
    versao_sgbd TEXT,
    tamanho_mb FLOAT,
    numero_tabelas INTEGER,
    numero_registros_total BIGINT,
    tem_indices BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dicionario.conteudo__database (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    estrutura_id UUID REFERENCES dicionario.estrutura__database(id) ON DELETE CASCADE,
    dominio_aplicacao TEXT,
    finalidade TEXT,
    periodo_dados_inicio DATE,
    periodo_dados_fim DATE,
    frequencia_atualizacao TEXT,
    principais_entidades TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GEODATABASE
CREATE TABLE dicionario.estrutura__geodatabase (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    arquivo_id UUID REFERENCES dicionario.arquivo(id) ON DELETE CASCADE,
    tipo_geodatabase TEXT, -- File GDB, Personal GDB, Enterprise GDB
    versao TEXT,
    numero_feature_classes INTEGER,
    numero_rasters INTEGER,
    numero_tables INTEGER,
    tamanho_mb FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dicionario.conteudo__geodatabase (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    estrutura_id UUID REFERENCES dicionario.estrutura__geodatabase(id) ON DELETE CASCADE,
    projeto_origem TEXT,
    area_estudo TEXT,
    escala_trabalho TEXT,
    data_criacao_gdb DATE,
    principais_datasets TEXT[],
    sistema_referencia TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- PACOTE
CREATE TABLE dicionario.estrutura__pacote (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    arquivo_id UUID REFERENCES dicionario.arquivo(id) ON DELETE CASCADE,
    tipo_compressao TEXT,
    numero_arquivos INTEGER,
    tamanho_descomprimido BIGINT,
    taxa_compressao FLOAT,
    tem_senha BOOLEAN DEFAULT FALSE,
    estrutura_diretorios JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dicionario.conteudo__pacote (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    estrutura_id UUID REFERENCES dicionario.estrutura__pacote(id) ON DELETE CASCADE,
    conteudo_descricao TEXT,
    finalidade_empacotamento TEXT,
    tipos_arquivo_inclusos TEXT[],
    manifesto JSONB, -- Lista detalhada dos arquivos
    instrucoes_uso TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- ESQUEMA USUARIOS (PROVISÓRIO)
-- =============================================================================

CREATE TABLE usuarios.usuario (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    nome_completo TEXT NOT NULL,
    primeiro_nome TEXT,
    ultimo_nome TEXT,
    telefone TEXT,
    cargo TEXT,
    departamento TEXT,
    instituicao TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    ultimo_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE usuarios.papel (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT UNIQUE NOT NULL,
    descricao TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir papéis padrão
INSERT INTO usuarios.papel (nome, descricao) VALUES
('admin', 'Administrador do sistema'),
('gestor', 'Gestor de conteúdo'),
('produtor', 'Produtor de dados'),
('consultor', 'Consultor de dados'),
('usuario', 'Usuário básico');

CREATE TABLE usuarios.usuario_papel (
    usuario_id UUID REFERENCES usuarios.usuario(id) ON DELETE CASCADE,
    papel_id UUID REFERENCES usuarios.papel(id) ON DELETE CASCADE,
    PRIMARY KEY (usuario_id, papel_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE usuarios.permissao (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    recurso TEXT NOT NULL, -- ex: 'arquivo', 'usuario', 'sistema'
    acao TEXT NOT NULL,    -- ex: 'create', 'read', 'update', 'delete'
    descricao TEXT,
    UNIQUE (recurso, acao)
);

-- Inserir permissões básicas
INSERT INTO usuarios.permissao (recurso, acao, descricao) VALUES
('arquivo', 'create', 'Criar arquivos'),
('arquivo', 'read', 'Visualizar arquivos'),
('arquivo', 'update', 'Editar arquivos'),
('arquivo', 'delete', 'Excluir arquivos'),
('arquivo', 'approve', 'Aprovar arquivos'),
('usuario', 'create', 'Criar usuários'),
('usuario', 'read', 'Visualizar usuários'),
('usuario', 'update', 'Editar usuários'),
('usuario', 'delete', 'Excluir usuários'),
('sistema', 'admin', 'Administrar sistema');

CREATE TABLE usuarios.papel_permissao (
    papel_id UUID REFERENCES usuarios.papel(id) ON DELETE CASCADE,
    permissao_id UUID REFERENCES usuarios.permissao(id) ON DELETE CASCADE,
    PRIMARY KEY (papel_id, permissao_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Popular permissões por papel
WITH papel_perm AS (
    SELECT 
        p.id as papel_id,
        perm.id as permissao_id
    FROM usuarios.papel p
    CROSS JOIN usuarios.permissao perm
    WHERE 
        (p.nome = 'admin') OR
        (p.nome = 'gestor' AND perm.recurso IN ('arquivo', 'usuario') AND perm.acao != 'delete') OR
        (p.nome = 'produtor' AND perm.recurso = 'arquivo' AND perm.acao IN ('create', 'read', 'update')) OR
        (p.nome = 'consultor' AND perm.recurso = 'arquivo' AND perm.acao = 'read') OR
        (p.nome = 'usuario' AND perm.recurso = 'arquivo' AND perm.acao = 'read')
)
INSERT INTO usuarios.papel_permissao (papel_id, permissao_id)
SELECT papel_id, permissao_id FROM papel_perm;

CREATE TABLE usuarios.auditoria_login (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES usuarios.usuario(id),
    ip_address INET,
    user_agent TEXT,
    sucesso BOOLEAN,
    tentativa_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabelas para Minha Área
CREATE TABLE usuarios.tarefa (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES usuarios.usuario(id) ON DELETE CASCADE,
    titulo TEXT NOT NULL,
    descricao TEXT,
    prioridade TEXT DEFAULT 'media' CHECK (prioridade IN ('baixa', 'media', 'alta')),
    status TEXT DEFAULT 'pendente' CHECK (status IN ('pendente', 'em_andamento', 'concluida', 'cancelada')),
    data_vencimento DATE,
    concluida_em TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE usuarios.evento (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES usuarios.usuario(id) ON DELETE CASCADE,
    titulo TEXT NOT NULL,
    descricao TEXT,
    data_inicio TIMESTAMP NOT NULL,
    data_fim TIMESTAMP,
    local TEXT,
    tipo TEXT DEFAULT 'reuniao' CHECK (tipo IN ('reuniao', 'evento', 'lembrete', 'feriado')),
    cor TEXT DEFAULT '#3498db',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE usuarios.homeoffice (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    usuario_id UUID REFERENCES usuarios.usuario(id) ON DELETE CASCADE,
    data DATE NOT NULL,
    confirmado BOOLEAN DEFAULT FALSE,
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (usuario_id, data)
);

-- =============================================================================
-- ESQUEMA CADASTRO (PROVISÓRIO)
-- =============================================================================

CREATE TABLE cadastro.instituicao (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    sigla TEXT,
    cnpj TEXT UNIQUE,
    tipo TEXT, -- federal, estadual, municipal, privada
    endereco TEXT,
    telefone TEXT,
    email TEXT,
    site TEXT,
    ativa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cadastro.departamento (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    instituicao_id UUID REFERENCES cadastro.instituicao(id),
    nome TEXT NOT NULL,
    sigla TEXT,
    descricao TEXT,
    responsavel TEXT,
    telefone TEXT,
    email TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cadastro.pessoa (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome_completo TEXT NOT NULL,
    cpf TEXT UNIQUE,
    email TEXT,
    telefone TEXT,
    cargo TEXT,
    instituicao_id UUID REFERENCES cadastro.instituicao(id),
    departamento_id UUID REFERENCES cadastro.departamento(id),
    ativa BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cadastro.produto (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    descricao TEXT,
    tipo TEXT,
    instituicao_responsavel_id UUID REFERENCES cadastro.instituicao(id),
    data_inicio DATE,
    data_fim DATE,
    status TEXT DEFAULT 'ativo' CHECK (status IN ('planejamento', 'ativo', 'concluido', 'cancelado')),
    orcamento DECIMAL(15,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cadastro.entrega (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    produto_id UUID REFERENCES cadastro.produto(id),
    nome TEXT NOT NULL,
    descricao TEXT,
    data_prevista DATE,
    data_entregue DATE,
    status TEXT DEFAULT 'pendente' CHECK (status IN ('pendente', 'em_andamento', 'entregue', 'aprovada', 'rejeitada')),
    observacoes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE cadastro.documento_normativo (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    titulo TEXT NOT NULL,
    tipo TEXT, -- lei, decreto, portaria, instrucao_normativa
    numero TEXT,
    ano INTEGER,
    data_publicacao DATE,
    orgao_emissor TEXT,
    ementa TEXT,
    link_oficial TEXT,
    arquivo_id UUID REFERENCES dicionario.arquivo(id),
    ativo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- ESQUEMA AUDITORIA
-- =============================================================================

CREATE TABLE auditoria.log_operacao (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tabela TEXT NOT NULL,
    operacao TEXT NOT NULL CHECK (operacao IN ('INSERT', 'UPDATE', 'DELETE')),
    registro_id UUID,
    dados_antigos JSONB,
    dados_novos JSONB,
    usuario_id UUID,
    ip_address INET,
    user_agent TEXT,
    timestamp_operacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE auditoria.log_operacao IS 'Log de todas as operações críticas do sistema';

-- =============================================================================
-- ÍNDICES
-- =============================================================================

-- Índices para tabela arquivo (principal)
CREATE INDEX idx_arquivo_perfil_id ON dicionario.arquivo(perfil_id);
CREATE INDEX idx_arquivo_extensao_id ON dicionario.arquivo(extensao_id);
CREATE INDEX idx_arquivo_produtor_id ON dicionario.arquivo(produtor_id);
CREATE INDEX idx_arquivo_status ON dicionario.arquivo(status);
CREATE INDEX idx_arquivo_publico ON dicionario.arquivo(publico);
CREATE INDEX idx_arquivo_created_at ON dicionario.arquivo(created_at);
CREATE INDEX idx_arquivo_nome_original ON dicionario.arquivo USING gin(nome_original gin_trgm_ops);
CREATE INDEX idx_arquivo_palavras_chave ON dicionario.arquivo USING gin(palavras_chave);

-- Índices para busca de texto
CREATE INDEX idx_arquivo_titulo ON dicionario.arquivo USING gin(titulo gin_trgm_ops);
CREATE INDEX idx_arquivo_descricao ON dicionario.arquivo USING gin(descricao gin_trgm_ops);

-- Índices para produtor
CREATE INDEX idx_produtor_nome ON dicionario.produtor USING gin(nome gin_trgm_ops);
CREATE INDEX idx_produtor_email ON dicionario.produtor(email);
CREATE INDEX idx_produtor_instituicao ON dicionario.produtor USING gin(instituicao gin_trgm_ops);

-- Índices para usuários
CREATE INDEX idx_usuario_email ON usuarios.usuario(email);
CREATE INDEX idx_usuario_username ON usuarios.usuario(username);
CREATE INDEX idx_usuario_ativo ON usuarios.usuario(ativo);

-- Índices para auditoria
CREATE INDEX idx_log_operacao_tabela ON auditoria.log_operacao(tabela);
CREATE INDEX idx_log_operacao_timestamp ON auditoria.log_operacao(timestamp_operacao);
CREATE INDEX idx_log_operacao_usuario_id ON auditoria.log_operacao(usuario_id);

-- Índices geoespaciais
CREATE INDEX idx_conteudo_midia_coordenadas ON dicionario.conteudo__midia USING gist(coordenadas);
CREATE INDEX idx_estrutura_geovetor_bbox ON dicionario.estrutura__geoespacial_vetor USING gist(bbox);
CREATE INDEX idx_estrutura_georaster_bbox ON dicionario.estrutura__geoespacial_raster USING gist(bbox);
CREATE INDEX idx_estrutura_nuvempontos_bbox ON dicionario.estrutura__nuvem_pontos USING gist(bbox);

-- =============================================================================
-- FUNÇÕES E TRIGGERS DE AUDITORIA
-- =============================================================================

-- Função genérica de auditoria
CREATE OR REPLACE FUNCTION auditoria.trigger_auditoria()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO auditoria.log_operacao (
        tabela,
        operacao,
        registro_id,
        dados_antigos,
        dados_novos,
        usuario_id,
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
        current_setting('app.current_user_id', true)::UUID,
        CURRENT_TIMESTAMP
    );
    
    IF TG_OP = 'DELETE' THEN
        RETURN OLD;
    ELSE
        RETURN NEW;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- Trigger para tabela arquivo
CREATE TRIGGER trigger_auditoria_arquivo
    AFTER INSERT OR UPDATE OR DELETE ON dicionario.arquivo
    FOR EACH ROW EXECUTE FUNCTION auditoria.trigger_auditoria();

-- Trigger para tabela usuario
CREATE TRIGGER trigger_auditoria_usuario
    AFTER INSERT OR UPDATE OR DELETE ON usuarios.usuario
    FOR EACH ROW EXECUTE FUNCTION auditoria.trigger_auditoria();

-- Função para atualizar updated_at
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers para updated_at
CREATE TRIGGER trigger_update_arquivo_updated_at
    BEFORE UPDATE ON dicionario.arquivo
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER trigger_update_produtor_updated_at
    BEFORE UPDATE ON dicionario.produtor
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER trigger_update_usuario_updated_at
    BEFORE UPDATE ON usuarios.usuario
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- =============================================================================
-- VIEWS PARA CATÁLOGO
-- =============================================================================

-- View base para catálogo (arquivo + produtor)
CREATE VIEW dicionario.view_catalogo_base AS
SELECT 
    a.id,
    a.nome_original,
    a.titulo,
    a.descricao,
    a.palavras_chave,
    a.idioma,
    a.data_criacao,
    a.tamanho_bytes,
    a.status,
    a.publico,
    a.created_at,
    
    -- Perfil
    p.nome as perfil,
    p.descricao as perfil_descricao,
    p.icone as perfil_icone,
    p.cor as perfil_cor,
    
    -- Extensão
    e.nome as extensao,
    e.mime_type,
    
    -- Produtor
    pr.nome as produtor_nome,
    pr.email as produtor_email,
    pr.instituicao as produtor_instituicao,
    pr.departamento as produtor_departamento
    
FROM dicionario.arquivo a
LEFT JOIN dicionario.perfil p ON a.perfil_id = p.id
LEFT JOIN dicionario.extensao e ON a.extensao_id = e.id
LEFT JOIN dicionario.produtor pr ON a.produtor_id = pr.id
WHERE a.status = 'aprovado' AND a.publico = TRUE;

COMMENT ON VIEW dicionario.view_catalogo_base IS 'View base para catálogo público de arquivos';

-- View específica para dados tabulares
CREATE VIEW dicionario.view_catalogo_tabular AS
SELECT 
    cb.*,
    et.numero_linhas,
    et.numero_colunas,
    et.cabecalho,
    ct.fonte_dados,
    ct.metodologia_coleta,
    ct.periodicidade,
    ct.cobertura_temporal_inicio,
    ct.cobertura_temporal_fim,
    ct.cobertura_geografica
FROM dicionario.view_catalogo_base cb
JOIN dicionario.estrutura__tabular et ON cb.id = et.arquivo_id
JOIN dicionario.conteudo__tabular ct ON et.id = ct.estrutura_id
WHERE cb.perfil = 'tabular';

-- View específica para dados geoespaciais vetoriais
CREATE VIEW dicionario.view_catalogo_geoespacial_vetor AS
SELECT 
    cb.*,
    ev.tipo_geometria,
    ev.numero_features,
    ev.srid,
    ST_AsGeoJSON(ev.bbox) as bbox_geojson,
    cv.tema_geografico,
    cv.escala,
    cv.data_levantamento,
    cv.precisao_horizontal
FROM dicionario.view_catalogo_base cb
JOIN dicionario.estrutura__geoespacial_vetor ev ON cb.id = ev.arquivo_id
JOIN dicionario.conteudo__geoespacial_vetor cv ON ev.id = cv.estrutura_id
WHERE cb.perfil = 'geoespacial_vetor';

-- =============================================================================
-- DADOS DE EXEMPLO PARA TESTE
-- =============================================================================

-- Inserir produtor exemplo
INSERT INTO dicionario.produtor (nome, email, instituicao, departamento) VALUES
('João Silva', 'joao.silva@sigma.gov.br', 'Secretaria de Planejamento', 'Departamento de Geoprocessamento'),
('Maria Santos', 'maria.santos@sigma.gov.br', 'Instituto de Pesquisas', 'Divisão de Estatística');

-- =============================================================================
-- COMENTÁRIOS FINAIS
-- =============================================================================

COMMENT ON DATABASE sigma_pli IS 'Sistema SIGMA-PLI - Plataforma de Informações e Dados';

-- Conceder permissões básicas
GRANT USAGE ON SCHEMA dicionario TO PUBLIC;
GRANT SELECT ON dicionario.view_catalogo_base TO PUBLIC;
GRANT SELECT ON dicionario.perfil TO PUBLIC;
GRANT SELECT ON dicionario.extensao TO PUBLIC;