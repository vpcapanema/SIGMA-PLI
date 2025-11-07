-- =============================================================================
-- SIGMA-PLI - DDL MÓDULO AUTENTICAÇÃO (M01_auth)
-- Compatível com nomes utilizados no Neo4j (Pessoa, Instituicao) e esquema dicionário (produtor)
-- =============================================================================

-- Extensões necessárias (já criadas no DDL principal)

-- =============================================================================
-- ESQUEMA USUARIOS - EXPANSÃO PARA AUTENTICAÇÃO
-- =============================================================================

-- Tabela: pessoa (compatível com Neo4j:Pessoa e dicionario:produtor)
-- Extende ou substitui o conceito de produtor para usuários autenticados
CREATE TABLE usuarios.pessoa (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome_completo TEXT NOT NULL,
    primeiro_nome TEXT,
    ultimo_nome TEXT,
    email TEXT UNIQUE,
    telefone TEXT,
    cpf TEXT UNIQUE,
    data_nascimento DATE,
    genero TEXT,
    foto_url TEXT,
    instituicao_id UUID REFERENCES cadastro.instituicao(id),
    departamento_id UUID REFERENCES cadastro.departamento(id),
    cargo TEXT,
    matricula TEXT,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE usuarios.pessoa IS 'Entidade pessoa - compatível com Neo4j:Pessoa e dicionario:produtor';

-- Tabela: conta_usuario (extensão de usuarios.usuario para autenticação)
CREATE TABLE usuarios.conta_usuario (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id UUID REFERENCES usuarios.pessoa(id) ON DELETE CASCADE,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    salt TEXT,
    email_verificado BOOLEAN DEFAULT FALSE,
    telefone_verificado BOOLEAN DEFAULT FALSE,
    dois_fatores_habilitado BOOLEAN DEFAULT FALSE,
    secreto_2fa TEXT,
    ultimo_login TIMESTAMP,
    ultimo_ip INET,
    tentativas_falha INTEGER DEFAULT 0,
    bloqueado_ate TIMESTAMP,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE usuarios.conta_usuario IS 'Conta de usuário para autenticação - extensão do usuarios.usuario';

-- Tabela: sessao
CREATE TABLE usuarios.sessao (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conta_usuario_id UUID REFERENCES usuarios.conta_usuario(id) ON DELETE CASCADE,
    token TEXT UNIQUE NOT NULL,
    refresh_token TEXT UNIQUE,
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP
);

COMMENT ON TABLE usuarios.sessao IS 'Sessões ativas de usuários autenticados';

-- Tabela: token_recuperacao
CREATE TABLE usuarios.token_recuperacao (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conta_usuario_id UUID REFERENCES usuarios.conta_usuario(id) ON DELETE CASCADE,
    token TEXT UNIQUE NOT NULL,
    tipo TEXT DEFAULT 'password_reset' CHECK (tipo IN ('password_reset', 'email_verification')),
    expires_at TIMESTAMP NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    usado_em TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE usuarios.token_recuperacao IS 'Tokens para recuperação de senha e verificação de email';

-- Tabela: tentativa_login (extensão de usuarios.auditoria_login)
CREATE TABLE usuarios.tentativa_login (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username TEXT,
    email TEXT,
    ip_address INET,
    user_agent TEXT,
    sucesso BOOLEAN DEFAULT FALSE,
    motivo_falha TEXT,
    conta_usuario_id UUID REFERENCES usuarios.conta_usuario(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE usuarios.tentativa_login IS 'Log detalhado de tentativas de login';

-- Tabela: grupo (grupos de usuários para permissões coletivas)
CREATE TABLE usuarios.grupo (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    nome TEXT UNIQUE NOT NULL,
    descricao TEXT,
    tipo TEXT DEFAULT 'manual' CHECK (tipo IN ('manual', 'automatico', 'departamento', 'instituicao')),
    instituicao_id UUID REFERENCES cadastro.instituicao(id),
    departamento_id UUID REFERENCES cadastro.departamento(id),
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE usuarios.grupo IS 'Grupos de usuários para organização e permissões';

-- Tabela: pessoa_grupo (relacionamento N:N)
CREATE TABLE usuarios.pessoa_grupo (
    pessoa_id UUID REFERENCES usuarios.pessoa(id) ON DELETE CASCADE,
    grupo_id UUID REFERENCES usuarios.grupo(id) ON DELETE CASCADE,
    PRIMARY KEY (pessoa_id, grupo_id),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela: permissao_grupo (relacionamento N:N entre grupo e permissao)
CREATE TABLE usuarios.permissao_grupo (
    grupo_id UUID REFERENCES usuarios.grupo(id) ON DELETE CASCADE,
    permissao_id UUID REFERENCES usuarios.permissao(id) ON DELETE CASCADE,
    PRIMARY KEY (grupo_id, permissao_id),
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- ÍNDICES PARA AUTENTICAÇÃO
-- =============================================================================

CREATE INDEX idx_pessoa_email ON usuarios.pessoa(email);
CREATE INDEX idx_pessoa_cpf ON usuarios.pessoa(cpf);
CREATE INDEX idx_pessoa_instituicao ON usuarios.pessoa(instituicao_id);
CREATE INDEX idx_pessoa_departamento ON usuarios.pessoa(departamento_id);

CREATE INDEX idx_conta_usuario_pessoa ON usuarios.conta_usuario(pessoa_id);
CREATE INDEX idx_conta_usuario_username ON usuarios.conta_usuario(username);
CREATE INDEX idx_conta_usuario_email ON usuarios.conta_usuario(email);
CREATE INDEX idx_conta_usuario_ativo ON usuarios.conta_usuario(ativo);

CREATE INDEX idx_sessao_conta_usuario ON usuarios.sessao(conta_usuario_id);
CREATE INDEX idx_sessao_token ON usuarios.sessao(token);
CREATE INDEX idx_sessao_refresh_token ON usuarios.sessao(refresh_token);
CREATE INDEX idx_sessao_expires_at ON usuarios.sessao(expires_at);

CREATE INDEX idx_token_recuperacao_conta_usuario ON usuarios.token_recuperacao(conta_usuario_id);
CREATE INDEX idx_token_recuperacao_token ON usuarios.token_recuperacao(token);
CREATE INDEX idx_token_recuperacao_expires_at ON usuarios.token_recuperacao(expires_at);

CREATE INDEX idx_tentativa_login_conta_usuario ON usuarios.tentativa_login(conta_usuario_id);
CREATE INDEX idx_tentativa_login_email ON usuarios.tentativa_login(email);
CREATE INDEX idx_tentativa_login_ip ON usuarios.tentativa_login(ip_address);
CREATE INDEX idx_tentativa_login_created_at ON usuarios.tentativa_login(created_at);

CREATE INDEX idx_grupo_instituicao ON usuarios.grupo(instituicao_id);
CREATE INDEX idx_grupo_departamento ON usuarios.grupo(departamento_id);

-- =============================================================================
-- TRIGGERS PARA AUDITORIA E ATUALIZAÇÃO
-- =============================================================================

-- Trigger para updated_at em pessoa
CREATE TRIGGER trigger_update_pessoa_updated_at
    BEFORE UPDATE ON usuarios.pessoa
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Trigger para updated_at em conta_usuario
CREATE TRIGGER trigger_update_conta_usuario_updated_at
    BEFORE UPDATE ON usuarios.conta_usuario
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Triggers de auditoria para tabelas críticas
CREATE TRIGGER trigger_auditoria_conta_usuario
    AFTER INSERT OR UPDATE OR DELETE ON usuarios.conta_usuario
    FOR EACH ROW EXECUTE FUNCTION auditoria.trigger_auditoria();

CREATE TRIGGER trigger_auditoria_sessao
    AFTER INSERT OR UPDATE OR DELETE ON usuarios.sessao
    FOR EACH ROW EXECUTE FUNCTION auditoria.trigger_auditoria();

-- =============================================================================
-- DADOS DE EXEMPLO PARA TESTE
-- =============================================================================

INSERT INTO usuarios.pessoa (nome_completo, primeiro_nome, ultimo_nome, email, telefone, cpf, cargo, instituicao_id, departamento_id)
VALUES
('João Silva Santos', 'João', 'Silva Santos', 'joao.silva@sigma.gov.br', '+55 11 99999-9999', '123.456.789-00', 'Analista de Sistemas', NULL, NULL);

-- Inserir conta_usuario exemplo
INSERT INTO usuarios.conta_usuario (pessoa_id, username, email, password_hash, email_verificado)
SELECT
    p.id,
    'joao.silva',
    'joao.silva@sigma.gov.br',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj8JZwHdQcO', -- senha: sigma123
    TRUE
FROM usuarios.pessoa p WHERE p.email = 'joao.silva@sigma.gov.br';

-- Inserir grupos padrão
INSERT INTO usuarios.grupo (nome, descricao, tipo) VALUES
('admin_global', 'Administradores globais do sistema', 'manual'),
('gestores_sigma', 'Gestores do SIGMA-PLI', 'departamento'),
('analistas_dados', 'Analistas de dados', 'manual'),
('usuarios_consulta', 'Usuários com acesso apenas consulta', 'automatico');

-- =============================================================================
-- COMENTÁRIOS FINAIS
-- =============================================================================

COMMENT ON SCHEMA usuarios IS 'Sistema de usuários, papéis, permissões e autenticação (expandido para M01_auth)';

-- Conceder permissões
GRANT USAGE ON SCHEMA usuarios TO PUBLIC;
GRANT SELECT ON usuarios.pessoa TO PUBLIC;
GRANT SELECT ON usuarios.grupo TO PUBLIC;