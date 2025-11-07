# FLUXO COMPLETO DE CADASTRO E APROVAÇÃO DE USUÁRIO

## Sistema SIGMA-PLI - Análise Baseada no PLI-CADASTRO

**Data da Análise:** 03/11/2025  
**Baseado em:** PLI-CADASTRO (Node.js/Express) → SIGMA-PRINCIPAL (FastAPI/Python)

---

## 📋 ÍNDICE

1. [Visão Geral do Fluxo](#visão-geral-do-fluxo)
2. [Estrutura do Banco de Dados](#estrutura-do-banco-de-dados)
3. [Etapas do Fluxo Detalhadas](#etapas-do-fluxo-detalhadas)
4. [Serviços Implementados](#serviços-implementados)
5. [Status e Estados do Usuário](#status-e-estados-do-usuário)
6. [Checklist de Implementação](#checklist-de-implementação)

---

## 🎯 VISÃO GERAL DO FLUXO

```
┌─────────────────────────────────────────────────────────────────────┐
│                    FLUXO DE CADASTRO DE USUÁRIO                     │
└─────────────────────────────────────────────────────────────────────┘

1. SOLICITAÇÃO DE CADASTRO (Usuário)
   ├── Preenche formulário web
   ├── Seleciona pessoa física existente (dropdown)
   ├── Seleciona instituição existente (dropdown)
   ├── Define tipo de acesso (ADMIN, GESTOR, ANALISTA, etc.)
   └── Define credenciais (username, senha, emails)

2. PROCESSAMENTO INICIAL (Backend)
   ├── Valida dados do formulário
   ├── Verifica duplicidade (pessoa_fisica_id + tipo_usuario)
   ├── Hash da senha (bcrypt/pbkdf2)
   ├── Cria registro em usuarios.usuario_sistema
   ├── Status inicial: AGUARDANDO_APROVACAO
   ├── Ativo inicial: false
   ├── Email verificado: false
   └── Gera token de verificação de email (24h)

3. NOTIFICAÇÕES POR EMAIL
   ├── Email para USUÁRIO:
   │   ├── Confirmação de solicitação recebida
   │   ├── Comprovante em anexo (HTML)
   │   ├── Link de verificação de email institucional
   │   └── Protocolo da solicitação
   └── Email para ADMINISTRADORES:
       ├── Notificação de nova solicitação
       ├── Dados do solicitante
       ├── Link para painel de aprovação
       └── Comprovante em anexo

4. VERIFICAÇÃO DE EMAIL (Usuário)
   ├── Clica no link recebido por email
   ├── Token validado (verifica expiração)
   ├── Marca email_institucional_verificado = true
   ├── Redireciona para página de sucesso
   └── Limpa token de verificação

5. ANÁLISE E APROVAÇÃO (Administrador/Gestor)
   ├── Acessa painel de solicitações pendentes
   ├── Visualiza dados do solicitante
   ├── Decide: APROVAR ou REJEITAR
   └── Se APROVAR:
       ├── status = APROVADO
       ├── ativo = true
       ├── Define nivel_acesso (se necessário)
       └── Email de aprovação enviado
   └── Se REJEITAR:
       ├── status = REJEITADO
       ├── ativo = false
       ├── Motivo da rejeição (opcional)
       └── Email de rejeição enviado

6. LOGIN DO USUÁRIO (Após aprovação)
   ├── Validações:
   │   ├── status = APROVADO ✓
   │   ├── ativo = true ✓
   │   └── email_institucional_verificado = true ✓
   ├── Senha correta (bcrypt)
   ├── Gera token JWT (24h)
   ├── Cria sessão em sessao_controle
   ├── Registra login (data, IP, user_agent)
   └── Retorna token + dados do usuário

7. GESTÃO DE SESSÃO (Durante uso)
   ├── Controle de janelas/abas múltiplas
   ├── Renovação automática de sessão
   ├── Rastreamento de última atividade
   ├── Detecção de inatividade
   └── Logout (manual ou automático)
```

---

## 🗄️ ESTRUTURA DO BANCO DE DADOS

### Tabelas Principais

#### 1. `usuarios.usuario_sistema`

```sql
CREATE TABLE usuarios.usuario_sistema (
    -- Identificação
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(100) UNIQUE NOT NULL,

    -- Emails
    email VARCHAR(255) NOT NULL,
    email_institucional TEXT,
    email_institucional_verificado BOOLEAN DEFAULT false,

    -- Autenticação
    senha_hash TEXT NOT NULL,
    salt VARCHAR(64),

    -- Vínculos
    pessoa_fisica_id UUID REFERENCES cadastro.pessoa_fisica(id),
    pessoa_juridica_id UUID REFERENCES cadastro.pessoa_juridica(id),

    -- Perfil
    tipo_usuario VARCHAR(50) NOT NULL,  -- ADMIN, GESTOR, ANALISTA, OPERADOR, VISUALIZADOR
    nivel_acesso INTEGER DEFAULT 1,
    departamento VARCHAR(200),
    cargo VARCHAR(200),

    -- Contatos institucionais
    telefone_institucional TEXT,
    ramal_institucional VARCHAR(20),

    -- Status e controle
    status VARCHAR(30) DEFAULT 'AGUARDANDO_APROVACAO',
    ativo BOOLEAN DEFAULT false,

    -- Verificação de email
    token_verificacao_email VARCHAR(64),
    token_expira_em TIMESTAMP WITH TIME ZONE,

    -- Recuperação de senha
    reset_token VARCHAR(255),
    reset_token_expiry TIMESTAMP,

    -- Segurança
    tentativas_login INTEGER DEFAULT 0,
    bloqueado_ate TIMESTAMP,

    -- Auditoria
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_ultimo_login TIMESTAMP,

    -- Constraints
    CONSTRAINT ck_usuario_sistema_status CHECK (
        status IN ('AGUARDANDO_APROVACAO', 'APROVADO', 'REJEITADO', 'SUSPENSO', 'INATIVO')
    )
);
```

#### 2. `usuarios.sessao_controle`

```sql
CREATE TABLE usuarios.sessao_controle (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    usuario_id UUID REFERENCES usuarios.usuario_sistema(id),

    -- Sessão
    token_jwt_hash VARCHAR(64) NOT NULL,
    session_id VARCHAR(100) UNIQUE NOT NULL,

    -- Datas
    data_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_ultimo_acesso TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_logout TIMESTAMP,
    data_expiracao TIMESTAMP NOT NULL,

    -- Status
    status_sessao VARCHAR(20) DEFAULT 'ATIVA',
    motivo_encerramento VARCHAR(50),

    -- Informações técnicas
    endereco_ip INET NOT NULL,
    user_agent TEXT,
    dispositivo_info JSONB,

    -- Controle
    tentativas_renovacao INTEGER DEFAULT 0,
    flags_seguranca JSONB,

    CONSTRAINT chk_data_logout CHECK (data_logout IS NULL OR data_logout >= data_login)
);
```

#### 3. `usuarios.sessao_janelas`

```sql
CREATE TABLE usuarios.sessao_janelas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sessao_id VARCHAR(100) REFERENCES usuarios.sessao_controle(session_id),
    window_id VARCHAR(100) NOT NULL,
    url TEXT,
    status VARCHAR(20) DEFAULT 'ATIVA',
    data_abertura TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_fechamento TIMESTAMP,
    data_ultimo_acesso TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. `usuarios.recuperacao_senha`

```sql
CREATE TABLE usuarios.recuperacao_senha (
    id SERIAL PRIMARY KEY,
    usuario_id UUID REFERENCES usuarios.usuario_sistema(id),
    token VARCHAR(6) NOT NULL,  -- Token numérico de 6 dígitos
    criado_em TIMESTAMP DEFAULT NOW(),
    expirado BOOLEAN DEFAULT false
);
```

#### 5. `usuarios.verificacao_email` (opcional - pode usar campos direto na usuario_sistema)

```sql
CREATE TABLE usuarios.verificacao_email (
    id SERIAL PRIMARY KEY,
    usuario_id UUID REFERENCES usuarios.usuario_sistema(id),
    token VARCHAR(255) UNIQUE NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expira_em TIMESTAMP NOT NULL,
    usado BOOLEAN DEFAULT FALSE,
    data_verificacao TIMESTAMP
);
```

---

## 🔄 ETAPAS DO FLUXO DETALHADAS

### ETAPA 1: Solicitação de Cadastro

**Endpoint:** `POST /api/v1/usuarios/solicitacao`

**Payload Esperado:**

```json
{
  "pessoa_fisica_id": "uuid-da-pessoa-fisica",
  "pessoa_juridica_id": "uuid-da-instituicao",
  "email": "usuario@example.com",
  "email_institucional": "usuario@instituicao.gov.br",
  "tipo_usuario": "ANALISTA",
  "username": "usuario.silva",
  "senha": "SenhaSegura@123",
  "departamento": "TI",
  "cargo": "Analista de Sistemas",
  "telefone_institucional": "(61) 3333-4444",
  "ramal_institucional": "1234"
}
```

**Validações Realizadas:**

1. Campos obrigatórios presentes
2. Formato de email válido (regex)
3. Senha mínima de 8 caracteres
4. Tipo de usuário válido
5. Não existe usuário com mesmo `pessoa_fisica_id` + `tipo_usuario`

**Processamento:**

```python
# 1. Validar dados
validacao = validar_dados_usuario(dados)
if not validacao.valido:
    return {"sucesso": False, "erros": validacao.mensagens}

# 2. Verificar duplicidade
usuario_existente = await verificar_usuario_existente(
    pessoa_fisica_id, tipo_usuario
)
if usuario_existente:
    return {"sucesso": False, "erro": "USUARIO_DUPLICADO"}

# 3. Hash da senha
salt = crypto.randomBytes(16).toString('hex')
senha_hash = crypto.pbkdf2Sync(senha, salt, 10000, 64, 'sha512')

# 4. Gerar token de verificação
token_verificacao = crypto.randomBytes(32).toString('hex')
expira_em = new Date(Date.now() + 24 * 60 * 60 * 1000)  # 24h

# 5. Inserir no banco
INSERT INTO usuarios.usuario_sistema (
    username, email, senha_hash, salt,
    pessoa_fisica_id, pessoa_juridica_id,
    tipo_usuario, email_institucional,
    telefone_institucional, ramal_institucional,
    departamento, cargo,
    status, ativo, email_institucional_verificado,
    token_verificacao_email, token_expira_em
) VALUES (
    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12,
    'AGUARDANDO_APROVACAO', false, false, $13, $14
)

# 6. Enviar emails
await enviar_confirmacao_solicitacao(usuario, token_verificacao)
await notificar_administradores(usuario)
```

**Resposta de Sucesso:**

```json
{
  "sucesso": true,
  "mensagem": "Solicitação recebida com sucesso!",
  "protocolo": "PLI-ABC123XYZ",
  "usuario": {
    "id": "uuid-gerado",
    "pessoa_fisica_id": "uuid-da-pessoa",
    "email": "usuario@example.com",
    "tipo_usuario": "ANALISTA",
    "data_criacao": "2025-11-03T10:30:00Z"
  },
  "notificacoes": {
    "emailUsuario": true,
    "emailAdmin": true
  }
}
```

---

### ETAPA 2: Verificação de Email Institucional

**Endpoint:** `GET /api/v1/auth/verificar-email/:token`

**Fluxo:**

```python
# 1. Buscar usuário pelo token
SELECT us.id, us.email, us.email_institucional, pf.nome_completo
FROM usuarios.usuario_sistema us
JOIN cadastro.pessoa_fisica pf ON pf.id = us.pessoa_fisica_id
WHERE us.token_verificacao_email = $1
  AND us.email_institucional_verificado = false
  AND us.token_expira_em > NOW()

# 2. Validar token
if not usuario:
    return "Token inválido, já utilizado ou expirado"

# 3. Marcar como verificado
UPDATE usuarios.usuario_sistema
SET email_institucional_verificado = true,
    token_verificacao_email = NULL,
    token_expira_em = NULL,
    data_atualizacao = NOW()
WHERE id = $1

# 4. Redirecionar para página de sucesso
redirect('/email-verificado.html?email={email}&nome={nome}')
```

**Email de Confirmação Enviado na Etapa 1:**

```html
<div style="background-color: #fff3cd; padding: 15px;">
  <h4>⚠️ IMPORTANTE: Verificação de Email Institucional</h4>
  <p>Você precisa verificar seu email institucional para ativar sua conta.</p>
  <a href="http://localhost:8010/api/auth/verificar-email/{token}">
    ✅ VERIFICAR EMAIL INSTITUCIONAL
  </a>
  <p>Este link expira em 24 horas.</p>
  <p><strong>Email a ser verificado:</strong> usuario@instituicao.gov.br</p>
</div>
```

---

### ETAPA 3: Análise e Aprovação (Administrador)

**Endpoint (Listar Pendentes):** `GET /api/v1/usuarios/solicitacoes/pendentes`

**Query:**

```sql
SELECT
    us.id,
    pf.nome_completo,
    us.username,
    us.email,
    us.email_institucional,
    us.email_institucional_verificado,
    pj.razao_social as instituicao,
    us.departamento,
    us.cargo,
    us.tipo_usuario,
    us.status,
    us.ativo,
    us.data_criacao
FROM usuarios.usuario_sistema us
JOIN cadastro.pessoa_fisica pf ON pf.id = us.pessoa_fisica_id
JOIN cadastro.pessoa_juridica pj ON pj.id = us.pessoa_juridica_id
WHERE us.status = 'AGUARDANDO_APROVACAO'
ORDER BY us.data_criacao DESC
LIMIT 200
```

**Endpoint (Aprovar):** `PUT /api/v1/usuarios/solicitacoes/:id/aprovar`

**Payload:**

```json
{
  "nivel_acesso": 3 // Opcional
}
```

**Processamento:**

```python
# 1. Atualizar registro
UPDATE usuarios.usuario_sistema
SET status = 'APROVADO',
    ativo = true,
    nivel_acesso = COALESCE($2, nivel_acesso),
    data_atualizacao = NOW()
WHERE id = $1
RETURNING id, username, email, email_institucional, tipo_usuario, nivel_acesso, ativo

# 2. Buscar dados completos do usuário
SELECT
    us.*,
    pf.nome_completo,
    pj.razao_social as instituicao
FROM usuarios.usuario_sistema us
JOIN cadastro.pessoa_fisica pf ON pf.id = us.pessoa_fisica_id
JOIN cadastro.pessoa_juridica pj ON pj.id = us.pessoa_juridica_id
WHERE us.id = $1

# 3. Enviar email de aprovação
await enviar_aprovacao(usuario)
```

**Email de Aprovação:**

```html
<div style="font-family: Arial, sans-serif;">
  <h2 style="color: #244b72;">Acesso Aprovado!</h2>
  <p>Olá {nome_completo},</p>
  <p>
    Sua solicitação de acesso ao SIGMA-PLI foi
    <strong style="color: green;">APROVADA</strong>.
  </p>
  <p>
    Você já pode acessar o sistema utilizando seu nome de usuário e senha
    cadastrados.
  </p>
  <a href="http://localhost:8010/pages/login">Acessar o Sistema</a>
</div>
```

**Endpoint (Rejeitar):** `PUT /api/v1/usuarios/solicitacoes/:id/rejeitar`

**Payload:**

```json
{
  "motivo": "Instituição não autorizada para este tipo de acesso"
}
```

**Processamento:**

```python
# 1. Atualizar registro
UPDATE usuarios.usuario_sistema
SET status = 'REJEITADO',
    ativo = false,
    data_atualizacao = NOW()
WHERE id = $1

# 2. Enviar email de rejeição
await enviar_rejeicao(usuario, motivo)
```

---

### ETAPA 4: Login do Usuário

**Endpoint:** `POST /api/v1/auth/login`

**Payload:**

```json
{
  "usuario": "usuario.silva", // ou "usuario@instituicao.gov.br"
  "password": "SenhaSegura@123",
  "tipo_usuario": "ANALISTA"
}
```

**Validações (em ordem):**

```python
# 1. Buscar usuário
is_email = '@' in usuario
if is_email:
    query = "SELECT * FROM usuarios.usuario_sistema WHERE email_institucional = $1 AND tipo_usuario = $2"
else:
    query = "SELECT * FROM usuarios.usuario_sistema WHERE username = $1 AND tipo_usuario = $2"

# 2. Verificar se usuário existe
if not user:
    return {"sucesso": False, "mensagem": "Credenciais inválidas"}

# 3. Verificar status = APROVADO
if user.status != 'APROVADO':
    return {
        "sucesso": False,
        "mensagem": "Usuário não aprovado. Aguarde a aprovação do administrador.",
        "codigo": "USUARIO_NAO_APROVADO"
    }

# 4. Verificar ativo = true
if not user.ativo:
    return {
        "sucesso": False,
        "mensagem": "Usuário inativo. Entre em contato com o administrador.",
        "codigo": "USUARIO_INATIVO"
    }

# 5. Verificar email_institucional_verificado = true
if not user.email_institucional_verificado:
    return {
        "sucesso": False,
        "mensagem": "Email institucional não verificado. Verifique seu email antes de fazer login.",
        "codigo": "EMAIL_NAO_VERIFICADO"
    }

# 6. Verificar senha
senha_correta = await bcrypt.compare(password, user.senha_hash)
if not senha_correta:
    # Incrementar tentativas de login
    await incrementar_tentativas_login(user.id)
    return {"sucesso": False, "mensagem": "Credenciais inválidas"}

# 7. Resetar tentativas de login
await resetar_tentativas_login(user.id)

# 8. Gerar token JWT
token = jwt.sign(
    {
        "id": user.id,
        "email": user.email,
        "nome": user.nome_completo,
        "tipo_usuario": user.tipo_usuario,
        "nivel_acesso": user.nivel_acesso
    },
    JWT_SECRET,
    { expiresIn: '24h' }
)

# 9. Criar sessão
sessao = await SessionService.criar_sessao(user.id, token, req)

# 10. Atualizar último login
UPDATE usuarios.usuario_sistema
SET data_ultimo_login = CURRENT_TIMESTAMP
WHERE id = $1
```

**Resposta de Sucesso:**

```json
{
  "sucesso": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "uuid-do-usuario",
    "nome": "João da Silva",
    "email": "joao@example.com",
    "tipo_usuario": "ANALISTA",
    "nivel_acesso": 3
  },
  "mensagem": "Autenticação realizada com sucesso",
  "redirect": "/dashboard.html"
}
```

---

### ETAPA 5: Gestão de Sessão

**Criar Sessão:**

```python
async def criar_sessao(usuario_id, token, req):
    # Hash do token JWT
    token_hash = crypto.createHash('sha256').update(token).digest('hex')

    # ID único da sessão
    session_id = crypto.randomUUID()

    # Extrair informações do request
    ip = req.ip or req.connection.remoteAddress
    user_agent = req.headers['user-agent']
    dispositivo_info = parse_user_agent(user_agent)

    # Expiração (24h)
    data_expiracao = new Date(Date.now() + 24 * 60 * 60 * 1000)

    # Inserir no banco
    INSERT INTO usuarios.sessao_controle (
        usuario_id, token_jwt_hash, session_id,
        data_login, data_ultimo_acesso, data_expiracao,
        endereco_ip, user_agent, dispositivo_info,
        status_sessao
    ) VALUES (
        $1, $2, $3, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, $4,
        $5, $6, $7, 'ATIVA'
    )
```

**Controle de Janelas/Abas:**

```python
async def registrar_janela(session_id, window_id, url, timestamp):
    # Registrar nova janela
    INSERT INTO usuarios.sessao_janelas (
        sessao_id, window_id, url, data_abertura
    ) VALUES ($1, $2, $3, to_timestamp($4 / 1000))

    # Atualizar última atividade da sessão
    UPDATE usuarios.sessao_controle
    SET data_ultimo_acesso = CURRENT_TIMESTAMP
    WHERE session_id = $1
```

**Renovação de Sessão:**

```python
async def renovar_sessao(session_id, window_id, reason):
    # Nova expiração (15 min)
    nova_expiracao = new Date(Date.now() + 15 * 60 * 1000)

    # Atualizar sessão
    UPDATE usuarios.sessao_controle
    SET data_expiracao = $2,
        data_ultimo_acesso = CURRENT_TIMESTAMP
    WHERE session_id = $1 AND status_sessao = 'ATIVA'

    # Registrar evento
    INSERT INTO usuarios.sessao_eventos (
        sessao_id, window_id, tipo_evento, dados_evento
    ) VALUES ($1, $2, 'RENEWAL', $3)
```

**Logout:**

```python
async def registrar_logout(token_hash, motivo='LOGOUT_MANUAL'):
    UPDATE usuarios.sessao_controle
    SET status_sessao = 'LOGOUT',
        data_logout = CURRENT_TIMESTAMP,
        motivo_encerramento = $2
    WHERE token_jwt_hash = $1 AND status_sessao = 'ATIVA'
```

---

## 🎨 SERVIÇOS IMPLEMENTADOS

### 1. **EmailService** (Python - SMTP)

**Funções Principais:**

- `enviar_email(to, subject, html)` - Genérico
- `enviar_confirmacao_solicitacao(usuario, token)` - Confirmação + comprovante + link verificação
- `notificar_administradores(usuario)` - Notifica admins sobre nova solicitação
- `enviar_aprovacao(usuario)` - Email de aprovação
- `enviar_rejeicao(usuario, motivo)` - Email de rejeição
- `enviar_recuperacao_senha(email, nome, token)` - Token de 6 dígitos
- `testar_conexao()` - Verifica SMTP

**Configuração (.env):**

```properties
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=senha_app_aqui  # Senha de app do Gmail
EMAIL_FROM=SIGMA-PLI <noreply@sigma-pli.gov.br>
EMAIL_ADMIN=admin@sigma-pli.gov.br
FRONTEND_URL=http://localhost:8010
```

**Templates de Email:**

- Comprovante HTML em anexo
- Links de verificação com token
- Layout profissional com cores institucionais
- Informações de protocolo e timestamp

---

### 2. **NotificationService** (Python)

**Funções:**

- `notificar_mudanca_status(usuario, status_anterior, status_novo, responsavel)`
- `notificar_mudanca_ativo(usuario, ativo_anterior, ativo_novo, responsavel)`
- `criar_template_email(nome, titulo, conteudo, responsavel)`

**Mapeamento de Status:**

```python
STATUS_MAP = {
    'AGUARDANDO_APROVACAO': {
        'nome': 'Aguardando Aprovação',
        'cor': '#17a2b8',  # Azul
        'emoji': '🔄'
    },
    'APROVADO': {
        'nome': 'Aprovado',
        'cor': '#28a745',  # Verde
        'emoji': '✅'
    },
    'REJEITADO': {
        'nome': 'Rejeitado',
        'cor': '#dc3545',  # Vermelho
        'emoji': '❌'
    },
    'SUSPENSO': {
        'nome': 'Suspenso',
        'cor': '#ffc107',  # Amarelo
        'emoji': '⚠️'
    },
    'INATIVO': {
        'nome': 'Inativo',
        'cor': '#6c757d',  # Cinza
        'emoji': '⭕'
    }
}
```

---

### 3. **SessionService** (Python)

**Funções Principais:**

- `criar_sessao(usuario_id, token, req)`
- `atualizar_ultimo_acesso(token_hash)`
- `registrar_logout(token_hash, motivo)`
- `verificar_sessao(token_hash)`
- `invalidar_sessoes_usuario(usuario_id, motivo)`
- `listar_sessoes_usuario(usuario_id)`
- `limpar_sessoes_expiradas()`
- `registrar_janela(session_id, window_id, url)`
- `desregistrar_janela(session_id, window_id)`
- `renovar_sessao(session_id, window_id, reason)`
- `gerar_hash_token(token)` - SHA256

**Parse de User Agent:**

```python
def parse_user_agent(user_agent):
    return {
        'browser': 'Chrome',  # Chrome, Firefox, Safari, Edge
        'version': '120',
        'os': 'Windows',      # Windows, macOS, Linux, Android, iOS
        'device': 'Desktop'   # Desktop, Mobile, Tablet
    }
```

---

### 4. **AuthService** (Python)

**Funções:**

- `login(email, password, tipo_usuario)`
- `logout(token)`
- `verificar_autenticacao(req)`
- `iniciar_recuperacao_senha(email)`
- `verificar_token_senha(email, token)`
- `confirmar_redefinicao_senha(token, nova_senha)`
- `alterar_senha(usuario_id, senha_atual, nova_senha)`
- `validar_forca_senha(senha)`

**Validação de Senha:**

```python
def validar_forca_senha(senha):
    erros = []
    if len(senha) < 8:
        erros.append("Senha deve ter pelo menos 8 caracteres")
    if not re.search(r'[A-Z]', senha):
        erros.append("Senha deve conter pelo menos uma letra maiúscula")
    if not re.search(r'[a-z]', senha):
        erros.append("Senha deve conter pelo menos uma letra minúscula")
    if not re.search(r'\d', senha):
        erros.append("Senha deve conter pelo menos um número")
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', senha):
        erros.append("Senha deve conter pelo menos um caractere especial")

    return {"valido": len(erros) == 0, "erros": erros}
```

---

## 📊 STATUS E ESTADOS DO USUÁRIO

### Estados do Campo `status`

| Status                 | Descrição                        | Quando ocorre                   | Ações permitidas                                           |
| ---------------------- | -------------------------------- | ------------------------------- | ---------------------------------------------------------- |
| `AGUARDANDO_APROVACAO` | Solicitação pendente de análise  | Criação inicial do usuário      | Admin pode aprovar/rejeitar                                |
| `APROVADO`             | Usuário aprovado pelos admins    | Após aprovação manual           | Pode fazer login se `ativo=true` e `email_verificado=true` |
| `REJEITADO`            | Solicitação rejeitada            | Admin rejeitou                  | Não pode fazer login, pode criar nova solicitação          |
| `SUSPENSO`             | Conta temporariamente suspensa   | Admin suspendeu temporariamente | Não pode fazer login até reativação                        |
| `INATIVO`              | Conta desativada permanentemente | Admin desativou                 | Não pode fazer login                                       |

### Combinações de Estados

**Para LOGIN ser permitido:**

```python
status == 'APROVADO' AND
ativo == true AND
email_institucional_verificado == true AND
senha_correta == true AND
bloqueado_ate IS NULL OR bloqueado_ate < NOW()
```

**Fluxo completo de estados:**

```
CRIAÇÃO
    ├── status = AGUARDANDO_APROVACAO
    ├── ativo = false
    └── email_institucional_verificado = false

VERIFICAÇÃO DE EMAIL
    └── email_institucional_verificado = true

APROVAÇÃO
    ├── status = APROVADO
    └── ativo = true

LOGIN PERMITIDO ✓
```

**Possíveis bloqueios:**

```python
# Bloqueio por tentativas excessivas de login
if tentativas_login >= 5:
    bloqueado_ate = NOW() + INTERVAL '30 minutes'

# Expiração de sessão
if data_expiracao < NOW():
    status_sessao = 'EXPIRADA'

# Inatividade prolongada
if (NOW() - data_ultimo_acesso) > 30 minutes:
    # Marcar como inativo ou expirar sessão
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO NO SIGMA-PRINCIPAL

### Banco de Dados

- [x] Migração 005: Campos `email_institucional` e `telefone_institucional` em `usuarios.usuario`
- [ ] Adicionar campo `status` com constraint
- [ ] Adicionar campo `email_institucional_verificado`
- [ ] Adicionar campos `token_verificacao_email` e `token_expira_em`
- [ ] Criar tabela `usuarios.sessao_controle`
- [ ] Criar tabela `usuarios.sessao_janelas`
- [ ] Criar tabela `usuarios.sessao_eventos`
- [ ] Criar tabela `usuarios.recuperacao_senha`
- [ ] Criar índices de performance
- [ ] Criar triggers de auditoria
- [ ] Criar views de consultas comuns

### Backend/API

- [ ] **Router:** `app/routers/M01_auth/router_auth_*.py`
  - [x] `router_auth_register.py` - Registro de usuário
  - [ ] `router_auth_login.py` - Login
  - [ ] `router_auth_password.py` - Recuperação de senha
  - [ ] `router_auth_verification.py` - Verificação de email
- [ ] **Services:**
  - [x] `service_email.py` - Envio de emails
  - [x] `service_notification.py` - Notificações de status
  - [ ] `service_session.py` - Gestão de sessões
  - [x] `service_auth.py` - Autenticação (parcial)
- [ ] **Schemas:**
  - [ ] `schema_auth_register.py` - Validação de cadastro
  - [ ] `schema_auth_login.py` - Validação de login
  - [ ] `schema_auth_session.py` - Dados de sessão
- [ ] **Middleware:**
  - [ ] `middleware_auth.py` - Verificação de token JWT
  - [ ] `middleware_session.py` - Controle de sessão
  - [ ] `middleware_permissions.py` - Verificação de permissões

### Frontend

- [ ] **Templates:**
  - [ ] `template_auth_cadastro_usuario.html` - Formulário de cadastro
  - [ ] `template_auth_login.html` - Página de login
  - [ ] `template_auth_email_verificado.html` - Confirmação de email
  - [ ] `template_auth_recuperar_senha.html` - Recuperação de senha
  - [ ] `template_admin_solicitacoes_pendentes.html` - Painel de aprovação
- [ ] **JavaScript:**
  - [ ] `script_cadastro_usuario_form.js` - Validação e submit
  - [ ] `script_login_auth.js` - Autenticação
  - [ ] `script_session_manager.js` - Gestão de sessão
  - [ ] `script_email_verification.js` - Verificação de email
- [ ] **CSS:**
  - [ ] `style_auth_forms.css` - Estilos de formulários
  - [ ] `style_auth_pages.css` - Páginas de autenticação

### Testes

- [ ] `test_auth_register.py` - Testes de cadastro
- [ ] `test_auth_login.py` - Testes de login
- [ ] `test_auth_verification.py` - Testes de verificação
- [ ] `test_email_service.py` - Testes de email
- [ ] `test_session_service.py` - Testes de sessão

### Configuração

- [x] `.env` - Variáveis de ambiente SMTP
- [x] `config.py` - Configurações de email
- [ ] `config.py` - Configurações de sessão (timeouts, etc.)
- [ ] `config.py` - Configurações de segurança (bcrypt rounds, JWT, etc.)

### Documentação

- [x] `SERVICO_EMAIL_IMPLEMENTACAO.md` - Documentação do serviço de email
- [x] `FLUXO_CADASTRO_USUARIO_COMPLETO.md` - Este documento
- [ ] `API_ENDPOINTS_AUTH.md` - Documentação de endpoints
- [ ] `GUIA_ADMIN_APROVACAO.md` - Guia para administradores

---

## 🔐 SEGURANÇA E BOAS PRÁTICAS

### Senhas

- ✅ Hash com bcrypt (PLI-CADASTRO) ou pbkdf2 (SIGMA-PRINCIPAL)
- ✅ Salt único por usuário
- ✅ Mínimo de 8 caracteres
- ✅ Validação de força (maiúscula, minúscula, número, especial)
- ✅ Bloqueio após 5 tentativas falhas (30 minutos)
- ✅ Recuperação via token temporário (15 minutos)

### Tokens

- ✅ JWT com expiração de 24h
- ✅ Hash SHA-256 do token armazenado no banco
- ✅ Token de verificação de email (24h)
- ✅ Token de recuperação de senha (15 minutos)
- ✅ Limpeza automática de tokens expirados

### Sessões

- ✅ Sessão expira em 24h
- ✅ Renovação automática em 15 minutos antes de expirar
- ✅ Controle de janelas/abas múltiplas
- ✅ Rastreamento de IP e User-Agent
- ✅ Detecção de dispositivos
- ✅ Logout em todas as janelas
- ✅ Invalidação forçada pelo admin

### Emails

- ✅ Verificação obrigatória de email institucional
- ✅ Links com tokens únicos e temporários
- ✅ Notificação de mudanças de status
- ✅ Comprovante de solicitação em anexo
- ✅ Templates HTML profissionais

### Auditoria

- ✅ Log de todos os logins (data, IP, dispositivo)
- ✅ Log de tentativas falhas
- ✅ Histórico de sessões
- ✅ Rastreamento de mudanças de status
- ✅ Registro de aprovações/rejeições

---

## 📈 MÉTRICAS E ESTATÍSTICAS

### Queries Úteis

**Usuários por status:**

```sql
SELECT status, COUNT(*) as total
FROM usuarios.usuario_sistema
GROUP BY status
ORDER BY total DESC;
```

**Solicitações pendentes:**

```sql
SELECT
    COUNT(*) as total_pendente,
    COUNT(CASE WHEN email_institucional_verificado THEN 1 END) as com_email_verificado,
    COUNT(CASE WHEN NOT email_institucional_verificado THEN 1 END) as sem_email_verificado
FROM usuarios.usuario_sistema
WHERE status = 'AGUARDANDO_APROVACAO';
```

**Logins por dia (últimos 30 dias):**

```sql
SELECT
    DATE(data_login) as data,
    COUNT(*) as total_logins,
    COUNT(DISTINCT usuario_id) as usuarios_unicos
FROM usuarios.sessao_controle
WHERE data_login >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY DATE(data_login)
ORDER BY data DESC;
```

**Sessões ativas:**

```sql
SELECT
    COUNT(*) as sessoes_ativas,
    COUNT(DISTINCT usuario_id) as usuarios_online
FROM usuarios.sessao_controle
WHERE status_sessao = 'ATIVA'
  AND data_expiracao > NOW();
```

**Média de tempo até aprovação:**

```sql
SELECT
    AVG(EXTRACT(EPOCH FROM (data_atualizacao - data_criacao)) / 3600) as horas_media
FROM usuarios.usuario_sistema
WHERE status = 'APROVADO';
```

---

## 🎯 PRÓXIMOS PASSOS PARA IMPLEMENTAÇÃO

### Prioridade ALTA (Crítico)

1. **Migração do Banco de Dados**

   - Adicionar campo `status` com valores válidos
   - Adicionar `email_institucional_verificado`
   - Adicionar `token_verificacao_email` e `token_expira_em`
   - Criar tabela `sessao_controle`

2. **Implementar Verificação de Email**

   - Endpoint `/api/v1/auth/verificar-email/:token`
   - Lógica de validação de token
   - Página de confirmação

3. **Completar Serviço de Sessão**

   - `SessionService.criar_sessao()`
   - `SessionService.verificar_sessao()`
   - `SessionService.registrar_logout()`

4. **Implementar Login Completo**
   - Validações de status
   - Criação de sessão
   - Retorno de token JWT

### Prioridade MÉDIA (Importante)

5. **Painel de Aprovação (Admin)**

   - Template de listagem de solicitações
   - Endpoints de aprovação/rejeição
   - Integração com NotificationService

6. **Recuperação de Senha**

   - Endpoint de solicitação
   - Endpoint de verificação de token
   - Endpoint de redefinição

7. **Gestão de Janelas/Abas**
   - Registro de janelas
   - Renovação de sessão
   - Logout automático

### Prioridade BAIXA (Melhorias)

8. **Estatísticas e Relatórios**

   - Dashboard de usuários
   - Métricas de login
   - Análise de sessões

9. **Testes Automatizados**

   - Testes de unidade
   - Testes de integração
   - Testes E2E

10. **Melhorias de Segurança**
    - Rate limiting
    - CAPTCHA em login
    - 2FA (opcional)

---

## 📝 NOTAS FINAIS

### Diferenças entre PLI-CADASTRO e SIGMA-PRINCIPAL

| Aspecto       | PLI-CADASTRO (Node.js) | SIGMA-PRINCIPAL (Python) |
| ------------- | ---------------------- | ------------------------ |
| Framework     | Express                | FastAPI                  |
| Email         | nodemailer             | smtplib (nativo)         |
| Hash de Senha | bcrypt                 | pbkdf2 / passlib         |
| Token JWT     | jsonwebtoken           | python-jose              |
| Validação     | Manual / Joi           | Pydantic                 |
| Async         | Promises/async-await   | asyncio/async-await      |
| ORM           | SQL direto             | SQLAlchemy (opcional)    |

### Decisões de Design

1. **Email Institucional Obrigatório:** Verificação é obrigatória antes do login
2. **Aprovação Manual:** Administradores devem aprovar cada solicitação
3. **Sessões Longas:** 24h de duração com renovação automática
4. **Múltiplas Janelas:** Suporte para várias abas abertas
5. **Tokens Temporários:** 24h para verificação de email, 15 min para senha
6. **Bloqueio Automático:** 5 tentativas falhas = bloqueio de 30 minutos
7. **Auditoria Completa:** Log de todas as ações importantes

---

**Documento gerado em:** 03/11/2025  
**Versão:** 1.0  
**Autor:** GitHub Copilot  
**Baseado em:** PLI-CADASTRO (Node.js/Express) e SIGMA-PRINCIPAL (FastAPI/Python)
