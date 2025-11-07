-- Extensões necessárias
CREATE EXTENSION
IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION
IF NOT EXISTS postgis;

-- Criar esquemas
CREATE SCHEMA
IF NOT EXISTS dicionario;
CREATE SCHEMA
IF NOT EXISTS usuarios;
CREATE SCHEMA
IF NOT EXISTS cadastro;

-- Esquema dicionario
CREATE TABLE dicionario.arquivo
(
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT NOT NULL,
    hash TEXT NOT NULL,
    mime_type TEXT NOT NULL,
    tamanho_bytes BIGINT NOT NULL,
    data_upload TIMESTAMP
    WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    caminho_storage TEXT NOT NULL,
    metadata JSONB
);

    CREATE TABLE dicionario.perfil
    (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        nome TEXT NOT NULL UNIQUE,
        descricao TEXT,
        metadados_obrigatorios JSONB
    );

    CREATE TABLE dicionario.extensao
    (
        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
        nome TEXT NOT NULL UNIQUE,
        mime_types TEXT
        [],
    perfil_id UUID REFERENCES dicionario.perfil
        (id)
);

        CREATE TABLE dicionario.produtor
        (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            arquivo_id UUID REFERENCES dicionario.arquivo(id),
            instituicao_id UUID,
            pessoa_id UUID,
            data_producao DATE,
            versao TEXT,
            observacoes TEXT
        );

        -- Tabelas específicas por perfil
        CREATE TABLE dicionario.estrutura__tabular
        (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            arquivo_id UUID REFERENCES dicionario.arquivo(id),
            colunas JSONB NOT NULL,
            delimitador TEXT,
            tem_cabecalho BOOLEAN DEFAULT true,
            encoding TEXT DEFAULT 'UTF-8'
        );

        CREATE TABLE dicionario.conteudo__tabular
        (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            estrutura_id UUID REFERENCES dicionario.estrutura__tabular(id),
            total_linhas INTEGER,
            colunas_vazias JSONB,
            estatisticas JSONB
        );

        CREATE TABLE dicionario.estrutura__geoespacial_vetor
        (
            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            arquivo_id UUID REFERENCES dicionario.arquivo(id),
            srid INTEGER,
            tipo_geometria TEXT,
            atributos JSONB,
            bbox GEOMETRY(POLYGON,
            4326)
);

            CREATE TABLE dicionario.conteudo__geoespacial_vetor
            (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                estrutura_id UUID REFERENCES dicionario.estrutura__geoespacial_vetor(id),
                total_feicoes INTEGER,
                estatisticas JSONB
            );

            -- Esquema usuarios
            CREATE TABLE usuarios.usuario
            (
                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                nome TEXT NOT NULL,
                ativo BOOLEAN DEFAULT true,
                data_criacao TIMESTAMP
                WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

                CREATE TABLE usuarios.papel
                (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    nome TEXT UNIQUE NOT NULL,
                    descricao TEXT
                );

                CREATE TABLE usuarios.usuario_papel
                (
                    usuario_id UUID REFERENCES usuarios.usuario(id),
                    papel_id UUID REFERENCES usuarios.papel(id),
                    PRIMARY KEY (usuario_id, papel_id)
                );

                CREATE TABLE usuarios.permissao
                (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    recurso TEXT NOT NULL,
                    acao TEXT NOT NULL,
                    UNIQUE(recurso, acao)
                );

                CREATE TABLE usuarios.papel_permissao
                (
                    papel_id UUID REFERENCES usuarios.papel(id),
                    permissao_id UUID REFERENCES usuarios.permissao(id),
                    PRIMARY KEY (papel_id, permissao_id)
                );

                CREATE TABLE usuarios.auditoria_login
                (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    usuario_id UUID REFERENCES usuarios.usuario(id),
                    data_hora TIMESTAMP
                    WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip TEXT,
    sucesso BOOLEAN,
    detalhes TEXT
);

                    CREATE TABLE usuarios.tarefa
                    (
                        id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                        usuario_id UUID REFERENCES usuarios.usuario(id),
                        titulo TEXT NOT NULL,
                        descricao TEXT,
                        prioridade INTEGER DEFAULT 1,
                        status TEXT NOT NULL,
                        data_criacao TIMESTAMP
                        WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    data_conclusao TIMESTAMP
                        WITH TIME ZONE
);

                        CREATE TABLE usuarios.evento
                        (
                            id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                            usuario_id UUID REFERENCES usuarios.usuario(id),
                            titulo TEXT NOT NULL,
                            descricao TEXT,
                            data_inicio TIMESTAMP
                            WITH TIME ZONE NOT NULL,
    data_fim TIMESTAMP
                            WITH TIME ZONE NOT NULL,
    tipo TEXT NOT NULL
);

                            CREATE TABLE usuarios.homeoffice
                            (
                                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                                usuario_id UUID REFERENCES usuarios.usuario(id),
                                data DATE NOT NULL,
                                status TEXT NOT NULL,
                                UNIQUE(usuario_id, data)
                            );

                            -- Esquema cadastro
                            CREATE TABLE cadastro.instituicao
                            (
                                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                                nome TEXT NOT NULL,
                                nome_fantasia TEXT,
                                sigla TEXT,
                                cnpj TEXT UNIQUE,
                                email TEXT UNIQUE,
                                telefone TEXT,
                                telefone_secundario TEXT,
                                site TEXT,
                                tipo TEXT,
                                ativo BOOLEAN DEFAULT true,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            );

                            CREATE TABLE cadastro.departamento
                            (
                                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                                instituicao_id UUID REFERENCES cadastro.instituicao(id),
                                nome TEXT NOT NULL,
                                sigla TEXT,
                                ativo BOOLEAN DEFAULT true
                            );

                            CREATE TABLE cadastro.pessoa
                            (
                                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                                nome_completo TEXT NOT NULL,
                                cpf TEXT UNIQUE,
                                email TEXT UNIQUE,
                                telefone TEXT,
                                cargo TEXT,
                                instituicao_id UUID REFERENCES cadastro.instituicao(id) ON DELETE SET NULL,
                                departamento_id UUID REFERENCES cadastro.departamento(id) ON DELETE SET NULL,
                                ativa BOOLEAN DEFAULT true,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            );

                            CREATE TABLE cadastro.produto
                            (
                                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                                nome TEXT NOT NULL,
                                descricao TEXT,
                                tipo TEXT,
                                data_inicio DATE,
                                data_fim DATE,
                                status TEXT
                            );

                            CREATE TABLE cadastro.entrega
                            (
                                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                                produto_id UUID REFERENCES cadastro.produto(id),
                                titulo TEXT NOT NULL,
                                descricao TEXT,
                                data_prevista DATE,
                                data_entrega DATE,
                                status TEXT
                            );

                            CREATE TABLE cadastro.documento_normativo
                            (
                                id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                                titulo TEXT NOT NULL,
                                numero TEXT,
                                ano INTEGER,
                                tipo TEXT,
                                url TEXT,
                                arquivo_id UUID REFERENCES dicionario.arquivo(id)
                            );

                            -- Índices
                            CREATE INDEX idx_arquivo_nome ON dicionario.arquivo(nome);
                            CREATE INDEX idx_arquivo_data_upload ON dicionario.arquivo(data_upload);
                            CREATE INDEX idx_produtor_arquivo ON dicionario.produtor(arquivo_id);
                            CREATE INDEX idx_usuario_email ON usuarios.usuario(email);
                            CREATE INDEX idx_tarefa_usuario ON usuarios.tarefa(usuario_id);
                            CREATE INDEX idx_evento_data ON usuarios.evento(data_inicio, data_fim);
                            CREATE INDEX idx_homeoffice_data ON usuarios.homeoffice(data);
                            CREATE INDEX idx_instituicao_nome ON cadastro.instituicao(nome);
                            CREATE INDEX idx_pessoa_nome ON cadastro.pessoa(nome);
                            CREATE INDEX idx_produto_status ON cadastro.produto(status);

                            -- Inserir papéis básicos
                            INSERT INTO usuarios.papel
                                (nome, descricao)
                            VALUES
                                ('admin', 'Administrador do sistema'),
                                ('usuario', 'Usuário padrão'),
                                ('curador', 'Curador de conteúdo');

                            -- Inserir permissões básicas
                            INSERT INTO usuarios.permissao
                                (recurso, acao)
                            VALUES
                                ('arquivo', 'criar'),
                                ('arquivo', 'ler'),
                                ('arquivo', 'atualizar'),
                                ('arquivo', 'deletar'),
                                ('metadados', 'criar'),
                                ('metadados', 'ler'),
                                ('metadados', 'atualizar'),
                                ('usuarios', 'gerenciar');
