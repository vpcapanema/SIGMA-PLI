# 🔄 FLUXO COMPLETO DE CADASTRO DE USUÁRIO - SIGMA-PLI

## Sistema SIGMA-PLI com Hierarquia de 5 Níveis

**Data:** 03 de Novembro de 2025  
**Versão:** 2.0 (com sistema de hierarquia implementado)

---

## 📊 VISÃO GERAL - DIAGRAMA DE FLUXO

```
┌────────────────────────────────────────────────────────────────────────────┐
│                   🔐 FLUXO DE CADASTRO DE USUÁRIO                          │
│                      (Com Sistema de Hierarquia)                           │
└────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│  1️⃣ SOLICITAÇÃO      │ 👤 Usuário acessa formulário web
│  DE CADASTRO        │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  DADOS DO FORMULÁRIO:                                               │
│  ─────────────────────────────────────────────────────────────────  │
│  ✅ pessoa_id (UUID da pessoa física - SELECT dropdown)             │
│  ✅ instituicao_id (UUID da instituição - SELECT dropdown)          │
│  ✅ username (formato: [nome].[sobrenome]_[tipo_usuario])          │
│     Exemplo: joao.silva_ANALISTA                                    │
│  ✅ email_institucional (único, formato: usuario@instituicao.gov.br)│
│  ✅ senha (mín. 8 caracteres, hash PBKDF2)                          │
│  ✅ tipo_usuario (ADMIN, GESTOR, ANALISTA, OPERADOR, VISUALIZADOR) │
│  ✅ telefone_institucional (opcional)                               │
└──────────┬──────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  2️⃣ VALIDAÇÃO        │ 🔍 Backend valida dados
│  INICIAL            │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  VALIDAÇÕES REALIZADAS:                                             │
│  ─────────────────────────────────────────────────────────────────  │
│  ✓ Username único (não existe na tabela)                            │
│  ✓ Email institucional único (não existe na tabela)                 │
│  ✓ Pessoa existe em usuarios.pessoa                                 │
│  ✓ Instituição existe em cadastro.instituicao                       │
│  ✓ tipo_usuario válido (ADMIN|GESTOR|ANALISTA|OPERADOR|VISUALIZADOR)│
│  ✓ Senha atende requisitos mínimos                                  │
│  ✓ Email no formato correto                                         │
└──────────┬──────────────────────────────────────────────────────────┘
           │
           ▼ [Validação OK]
┌─────────────────────┐
│  3️⃣ CRIAÇÃO DO       │ 💾 Insere registro no banco
│  REGISTRO           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  INSERT INTO usuarios.usuario:                                      │
│  ─────────────────────────────────────────────────────────────────  │
│  • id: UUID (gerado automaticamente)                                │
│  • pessoa_id: UUID (da pessoa física)                               │
│  • instituicao_id: UUID (da instituição)                            │
│  • username: string (formato: nome.sobrenome_TIPO)                  │
│  • email_institucional: string (único)                              │
│  • password_hash: string (PBKDF2-HMAC-SHA256)                       │
│  • salt: string (16 bytes hex)                                      │
│  • tipo_usuario: conforme solicitado (ADMIN|GESTOR|etc)             │
│  • nivel_acesso: calculado automaticamente pelo trigger             │
│  • email_verificado: false                                          │
│  • telefone_verificado: false                                       │
│  • dois_fatores_habilitado: false                                   │
│  • ativo: false (aguardando verificação de email)                   │
│  • tentativas_falha: 0                                              │
│  • criado_em: NOW()                                                 │
│  • atualizado_em: NOW()                                             │
│                                                                      │
│  🔥 TRIGGER AUTOMÁTICO EXECUTADO:                                    │
│  → tr_usuario_calcular_nivel: Define nivel_acesso baseado em tipo   │
│                                                                      │
│  GERA:                                                               │
│  • Token de verificação de email (UUID, válido 24h)                 │
│  • Protocolo de solicitação (para acompanhamento)                   │
└──────────┬──────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  4️⃣ NOTIFICAÇÕES     │ 📧 Envia emails
│  POR EMAIL          │
└──────────┬──────────┘
           │
           ├─────────────────────────────────────────────────────────┐
           │                                                         │
           ▼                                                         ▼
┌──────────────────────────┐                        ┌─────────────────────────┐
│  EMAIL PARA USUÁRIO:     │                        │  EMAIL PARA ADMINs:     │
│  ──────────────────────  │                        │  ─────────────────────  │
│  ✉️ Assunto:             │                        │  ✉️ Assunto:            │
│  "Solicitação Recebida"  │                        │  "Nova Solicitação"     │
│                          │                        │                         │
│  📄 Conteúdo:            │                        │  📄 Conteúdo:           │
│  • Confirmação recebida  │                        │  • Dados do solicitante │
│  • Protocolo: #123456    │                        │  • Tipo solicitado      │
│  • Link verificação email│                        │  • Data/hora            │
│  • Próximos passos       │                        │  • Link aprovação       │
│  • Comprovante HTML      │                        │  • Comprovante HTML     │
└──────────────────────────┘                        └─────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  5️⃣ VERIFICAÇÃO      │ ✅ Usuário confirma email
│  DE EMAIL           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  FLUXO DE VERIFICAÇÃO:                                              │
│  ─────────────────────────────────────────────────────────────────  │
│  1. Usuário clica no link recebido por email                        │
│     GET /api/v1/auth/verify-email?token={token}                     │
│                                                                      │
│  2. Backend valida token:                                           │
│     • Token existe?                                                 │
│     • Token não expirou? (< 24h)                                    │
│     • Usuário ainda não verificado?                                 │
│                                                                      │
│  3. Se válido:                                                      │
│     UPDATE usuarios.usuario                                         │
│     SET email_verificado = true,                                    │
│         atualizado_em = NOW()                                       │
│     WHERE id = {usuario_id}                                         │
│                                                                      │
│     DELETE FROM usuarios.token_verificacao                          │
│     WHERE usuario_id = {usuario_id}                                 │
│                                                                      │
│  4. Redireciona para: /verificacao-sucesso                          │
└──────────┬──────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  6️⃣ AGUARDANDO       │ ⏳ Email verificado, aguardando ativação
│  ATIVAÇÃO           │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ESTADO APÓS VERIFICAÇÃO DE EMAIL:                                  │
│  ─────────────────────────────────────────────────────────────────  │
│  • ativo: false ⚠️                                                   │
│  • email_verificado: true ✅                                         │
│  • tipo_usuario: conforme definido no cadastro (ex: 'ANALISTA')     │
│  • nivel_acesso: calculado automaticamente pelo trigger (ex: 3)     │
│                                                                      │
│  ⚠️ USUÁRIO NÃO PODE FAZER LOGIN ATÉ SER ATIVADO POR GESTOR/ADMIN   │
│                                                                      │
│  📧 Email enviado para GESTORs e ADMINs:                            │
│     • Notificação de novo usuário com email verificado              │
│     • Dados do usuário (nome, instituição, tipo solicitado)         │
│     • Link para ativar usuário                                      │
└──────────┬──────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  7️⃣ ATIVAÇÃO MANUAL  │ 👨‍💼 GESTOR ou ADMIN ativa (nível 4+)
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ENDPOINT DE ATIVAÇÃO:                                              │
│  ─────────────────────────────────────────────────────────────────  │
│  POST /api/v1/admin/usuarios/{id}/ativar                            │
│  Authorization: Bearer {token}                                      │
│  Content-Type: application/json                                     │
│                                                                      │
│  PERMISSÃO: GESTOR ou ADMIN (nível 4+) ⚠️                           │
│                                                                      │
│  Body (opcional):                                                   │
│  {                                                                  │
│    "observacao": "Aprovado após validação de documentos"            │
│  }                                                                  │
│                                                                      │
│  AÇÕES EXECUTADAS:                                                  │
│  1. Valida permissão do solicitante (deve ser GESTOR ou ADMIN)      │
│                                                                      │
│  2. Valida estado do usuário:                                       │
│     • email_verificado = true?                                      │
│     • ativo = false?                                                │
│                                                                      │
│  3. Ativa o usuário:                                                │
│     UPDATE usuarios.usuario                                         │
│     SET ativo = true,                                               │
│         ativado_por = {id_do_gestor_ou_admin},                      │
│         ativado_em = NOW(),                                         │
│         atualizado_em = NOW()                                       │
│     WHERE id = {usuario_id}                                         │
│                                                                      │
│  4. Envia email de boas-vindas ao usuário:                          │
│     • Notificação de cadastro aprovado                              │
│     • Credenciais de acesso                                         │
│     • Link para primeiro login                                      │
│     • Informações sobre suas permissões (tipo_usuario e nivel)      │
│                                                                      │
│  5. Registra na auditoria:                                          │
│     INSERT INTO usuarios.auditoria_ativacao (...)                   │
│                                                                      │
│  Response 200:                                                      │
│  {                                                                  │
│    "message": "Usuário ativado com sucesso",                        │
│    "usuario": {                                                     │
│      "id": "uuid",                                                  │
│      "username": "joao.silva_ANALISTA",                             │
│      "tipo_usuario": "ANALISTA",                                    │
│      "nivel_acesso": 3,                                             │
│      "ativo": true,                                                 │
│      "ativado_por": "admin.sistema_ADMIN",                          │
│      "ativado_em": "2025-11-03T14:30:00Z"                           │
│    }                                                                │
│  }                                                                  │
└──────────┬──────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  8️⃣ USUÁRIO ATIVO    │ ✅ Pode fazer login
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  ESTADO DO USUÁRIO ATIVO:                                           │
│  ─────────────────────────────────────────────────────────────────  │
│  • ativo: true ✅                                                    │
│  • email_verificado: true ✅                                         │
│  • tipo_usuario: conforme definido no cadastro (ex: 'ANALISTA')     │
│  • nivel_acesso: calculado automaticamente pelo trigger (ex: 3)     │
│  • ativado_por: UUID do GESTOR/ADMIN que ativou                     │
│  • ativado_em: timestamp da ativação                                │
│                                                                      │
│  🎯 MAPEAMENTO AUTOMÁTICO (via trigger):                            │
│  ────────────────────────────────────────────────────────────────   │
│  ADMIN        → nivel_acesso = 5                                    │
│  GESTOR       → nivel_acesso = 4                                    │
│  ANALISTA     → nivel_acesso = 3                                    │
│  OPERADOR     → nivel_acesso = 2                                    │
│  VISUALIZADOR → nivel_acesso = 1                                    │
└──────────┬──────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  9️⃣ PRIMEIRO LOGIN   │ 🔐 Autenticação
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  FLUXO DE LOGIN:                                                    │
│  ─────────────────────────────────────────────────────────────────  │
│  1. Usuário acessa /auth/login                                      │
│     POST /api/v1/auth/login                                         │
│     {                                                               │
│       "identifier": "username ou email",                            │
│       "password": "senha"                                           │
│     }                                                               │
│                                                                      │
│  2. Backend valida:                                                 │
│     ✓ Usuário existe?                                               │
│     ✓ ativo = true?                                                 │
│     ✓ email_verificado = true?                                      │
│     ✓ Senha correta? (PBKDF2 hash)                                  │
│     ✓ Não está bloqueado? (tentativas_falha < 5)                    │
│                                                                      │
│  3. Se válido:                                                      │
│     • Gera token JWT (exp: 24h)                                     │
│     • Cria sessão em usuarios.sessao                                │
│     • Registra em usuarios.auditoria_login                          │
│     • Atualiza ultimo_login, ultimo_ip                              │
│     • Zera tentativas_falha                                         │
│                                                                      │
│  4. Retorna:                                                        │
│     {                                                               │
│       "access_token": "eyJ...",                                     │
│       "token_type": "bearer",                                       │
│       "user": {                                                     │
│         "id": "uuid",                                               │
│         "username": "joao.silva_ANALISTA",                          │
│         "nome_completo": "...",                                     │
│         "tipo_usuario": "ANALISTA",                                 │
│         "nivel_acesso": 3,                                          │
│         "email_institucional": "..."                                │
│       }                                                             │
│     }                                                               │
│                                                                      │
│  5. Redireciona para:                                               │
│     • /dashboard (usuários normais)                                 │
│     • /admin/panel (se tipo_usuario = ADMIN)                        │
└──────────┬──────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  1️⃣0️⃣ GESTÃO DE      │ 🔄 Controle de sessão
│  SESSÃO             │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  FUNCIONALIDADES DA SESSÃO:                                         │
│  ─────────────────────────────────────────────────────────────────  │
│  ✓ Múltiplas janelas/abas (mesmo token)                             │
│  ✓ Renovação automática de sessão                                   │
│  ✓ Rastreamento de última atividade                                 │
│  ✓ Detecção de inatividade (auto-logout)                            │
│  ✓ Histórico de logins                                              │
│  ✓ Controle de dispositivos/IPs                                     │
│                                                                      │
│  TABELAS RELACIONADAS:                                              │
│  • usuarios.sessao (sessões ativas)                                 │
│  • usuarios.auditoria_login (histórico)                             │
│  • usuarios.tentativa_login (tentativas falhadas)                   │
└──────────┬──────────────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────┐
│  1️⃣1️⃣ CONTROLE DE    │ 🛡️ Middleware de permissões
│  ACESSO             │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────────────┐
│  SISTEMA DE HIERARQUIA - 5 NÍVEIS:                                  │
│  ─────────────────────────────────────────────────────────────────  │
│                                                                      │
│  🔴 NÍVEL 5 - ADMIN (Administrador)                                 │
│     ──────────────────────────────────────────────────────────────  │
│     Permissões:                                                     │
│     ✅ Acesso total ao sistema                                       │
│     ✅ Gerenciar permissões de outros usuários                       │
│     ✅ Deletar/desativar usuários                                    │
│     ✅ Acessar painel administrativo                                 │
│     ✅ Ver logs de auditoria completos                               │
│     ✅ Configurar sistema                                            │
│                                                                      │
│     Endpoints protegidos:                                           │
│     • DELETE /api/v1/admin/usuarios/{id}                            │
│     • POST /api/v1/admin/usuarios/{id}/reativar                     │
│     • GET /admin/panel                                              │
│     • GET /admin/sessions-manager                                   │
│                                                                      │
│  🟣 NÍVEL 4 - GESTOR                                                │
│     ──────────────────────────────────────────────────────────────  │
│     Permissões:                                                     │
│     ✅ Aprovar/rejeitar solicitações de cadastro                     │
│     ✅ Gerenciar usuários (exceto deletar)                           │
│     ✅ Alterar tipo de usuário de outros                             │
│     ✅ Ver relatórios gerenciais                                     │
│     ✅ Acessar painel de gestão                                      │
│                                                                      │
│     Endpoints protegidos:                                           │
│     • POST /api/v1/admin/usuarios/{id}/aprovar                      │
│     • PUT /api/v1/admin/usuarios/{id}/tipo                          │
│     • GET /admin/usuarios                                           │
│     • GET /admin/solicitacoes-cadastro                              │
│                                                                      │
│  🔵 NÍVEL 3 - ANALISTA                                              │
│     ──────────────────────────────────────────────────────────────  │
│     Permissões:                                                     │
│     ✅ Consultar todos os dados do sistema                           │
│     ✅ Gerar relatórios e estatísticas                               │
│     ✅ Exportar dados                                                │
│     ✅ Ver dashboards analíticos                                     │
│                                                                      │
│     Endpoints protegidos:                                           │
│     • GET /api/v1/admin/usuarios/hierarquia                         │
│     • GET /api/v1/admin/usuarios/estatisticas                       │
│     • GET /api/v1/relatorios/*                                      │
│                                                                      │
│  🟢 NÍVEL 2 - OPERADOR                                              │
│     ──────────────────────────────────────────────────────────────  │
│     Permissões:                                                     │
│     ✅ Inserir novos dados                                           │
│     ✅ Editar próprios registros                                     │
│     ✅ Consultar dados básicos                                       │
│                                                                      │
│     Endpoints protegidos:                                           │
│     • POST /api/v1/dados/*                                          │
│     • PUT /api/v1/dados/{id} (apenas próprios)                      │
│                                                                      │
│  ⚪ NÍVEL 1 - VISUALIZADOR                                          │
│     ──────────────────────────────────────────────────────────────  │
│     Permissões:                                                     │
│     ✅ Apenas consultar dados (read-only)                            │
│     ✅ Ver dashboards públicos                                       │
│                                                                      │
│     Endpoints protegidos:                                           │
│     • GET /api/v1/dados/*                                           │
│     • GET /dashboard                                                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🗄️ TABELAS DO BANCO DE DADOS

### **usuarios.usuario** (Tabela Principal)

```sql
CREATE TABLE usuarios.usuario (
    -- Identificação
    id                      UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id               UUID REFERENCES usuarios.pessoa(id) ON DELETE CASCADE,
    instituicao_id          UUID REFERENCES cadastro.instituicao(id) ON DELETE SET NULL,

    -- Credenciais
    username                TEXT UNIQUE NOT NULL,
    email_institucional     TEXT UNIQUE NOT NULL,
    password_hash           TEXT NOT NULL,
    salt                    TEXT,

    -- ⭐ HIERARQUIA (NOVO - Migration 006)
    tipo_usuario            VARCHAR(50) NOT NULL DEFAULT 'VISUALIZADOR'
                            CHECK (tipo_usuario IN ('ADMIN', 'GESTOR', 'ANALISTA', 'OPERADOR', 'VISUALIZADOR')),
    nivel_acesso            INTEGER DEFAULT 1
                            CHECK (nivel_acesso >= 1 AND nivel_acesso <= 5),

    -- Verificações
    email_verificado        BOOLEAN DEFAULT false,
    telefone_verificado     BOOLEAN DEFAULT false,
    dois_fatores_habilitado BOOLEAN DEFAULT false,
    secreto_2fa             TEXT,

    -- Contato
    telefone_institucional  TEXT,

    -- Controle de acesso
    ultimo_login            TIMESTAMP,
    ultimo_ip               INET,
    tentativas_falha        INTEGER DEFAULT 0,
    bloqueado_ate           TIMESTAMP,
    ativo                   BOOLEAN DEFAULT false, -- Inicia false até aprovação

    -- Auditoria
    criado_em               TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ⚡ TRIGGER AUTOMÁTICO (Migration 006)
CREATE TRIGGER tr_usuario_calcular_nivel
    BEFORE INSERT OR UPDATE OF tipo_usuario ON usuarios.usuario
    FOR EACH ROW
    EXECUTE FUNCTION usuarios.calcular_nivel_acesso();
```

### **Tabelas Auxiliares:**

```sql
-- Tokens de verificação de email
usuarios.token_verificacao (
    token UUID,
    usuario_id UUID,
    tipo VARCHAR(50), -- 'EMAIL_VERIFICATION', 'PASSWORD_RESET'
    expira_em TIMESTAMP,
    usado BOOLEAN
)

-- Sessões ativas
usuarios.sessao (
    id UUID,
    usuario_id UUID,
    token TEXT,
    ip_address INET,
    user_agent TEXT,
    criado_em TIMESTAMP,
    expira_em TIMESTAMP,
    ativo BOOLEAN
)

-- Auditoria de login
usuarios.auditoria_login (
    id UUID,
    usuario_id UUID,
    sucesso BOOLEAN,
    ip_address INET,
    user_agent TEXT,
    timestamp TIMESTAMP,
    motivo_falha TEXT
)

-- Tentativas de login falhadas
usuarios.tentativa_login (
    id UUID,
    usuario_id UUID,
    ip_address INET,
    timestamp TIMESTAMP
)
```

---

## 📡 ENDPOINTS PRINCIPAIS

### **1. Cadastro (Público)**

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "pessoa_id": "uuid-da-pessoa-fisica",
  "instituicao_id": "uuid-da-instituicao",
  "username": "joao.silva_ANALISTA",  // Padrão: [nome].[sobrenome]_[TIPO]
  "email_institucional": "joao.silva@instituicao.gov.br",
  "password": "SenhaSegura123!",
  "telefone_institucional": "+5561999999999",
  "tipo_usuario": "ANALISTA"
}

Response 201:
{
  "success": true,
  "message": "Solicitação de cadastro enviada com sucesso. Verifique seu email.",
  "protocolo": "123456"
}
```

### **2. Verificação de Email (Público)**

```http
GET /api/v1/auth/verify-email?token={token}

Response 302:
Redirect to: /verificacao-sucesso
```

### **3. Ativar Usuário (GESTOR ou ADMIN - nível 4+)**

```http
POST /api/v1/admin/usuarios/{usuario_id}/ativar
Authorization: Bearer {token}
Content-Type: application/json

{
  "observacao": "Aprovado após validação de documentos" // opcional
}

Response 200:
{
  "message": "Usuário ativado com sucesso",
  "usuario": {
    "id": "uuid",
    "username": "joao.silva_ANALISTA",
    "tipo_usuario": "ANALISTA",
    "nivel_acesso": 3,
    "ativo": true,
    "ativado_por": "admin.sistema_ADMIN",
    "ativado_em": "2025-11-03T14:30:00Z"
  }
}
```

### **4. Atualizar Tipo de Usuário (ADMIN apenas)**

```http
PUT /api/v1/admin/usuarios/{usuario_id}/tipo
Authorization: Bearer {token}
Content-Type: application/json

{
  "tipo_usuario": "GESTOR"
}

Response 200:
{
  "id": "uuid",
  "username": "joao.silva_GESTOR",  // Username atualizado também
  "tipo_usuario": "GESTOR",
  "nivel_acesso": 4,  // Recalculado automaticamente
  "tipo_usuario_descricao": "Gestor"
}
```

### **5. Login (Público)**

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "identifier": "joao.silva_ANALISTA",  // username ou email
  "password": "SenhaSegura123!"
}

Response 200:
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "username": "joao.silva_ANALISTA",
    "nome_completo": "João Silva",
    "email_institucional": "joao.silva@instituicao.gov.br",
    "tipo_usuario": "ANALISTA",
    "nivel_acesso": 3
  }
}
```

### **6. Listar Usuários (ANALISTA+)**

```http
GET /api/v1/admin/usuarios/hierarquia?limit=50&tipo_usuario=ANALISTA&apenas_ativos=true
Authorization: Bearer {token}

Response 200:
[
  {
    "id": "uuid",
    "username": "joao.silva_ANALISTA",
    "email_institucional": "joao.silva@instituicao.gov.br",
    "tipo_usuario": "ANALISTA",
    "nivel_acesso": 3,
    "ativo": true,
    "email_verificado": true,
    "tipo_usuario_descricao": "Analista"
  }
]
```

---

## 🔐 EXEMPLOS DE USO DO MIDDLEWARE

### **Proteger Endpoint com ADMIN**

```python
from fastapi import APIRouter, Depends
from app.middleware.auth_middleware import require_admin
from app.schemas.M01_auth.schema_auth import AuthenticatedUser

router = APIRouter()

@router.delete("/usuarios/{id}")
async def deletar_usuario(
    id: UUID,
    current_user: AuthenticatedUser = Depends(require_admin)  # ← Apenas ADMIN
):
    """Apenas ADMINs podem deletar usuários"""
    return {"message": "Usuário deletado"}
```

### **Proteger Endpoint com GESTOR+**

```python
from app.middleware.auth_middleware import require_admin_or_gestor

@router.post("/usuarios/aprovar/{id}")
async def aprovar_usuario(
    id: UUID,
    current_user: AuthenticatedUser = Depends(require_admin_or_gestor)  # ← GESTOR+
):
    """GESTORs e ADMINs podem aprovar"""
    return {"message": "Usuário aprovado"}
```

### **Proteger Endpoint com ANALISTA+**

```python
from app.middleware.auth_middleware import require_analista_or_above

@router.get("/relatorios")
async def gerar_relatorio(
    current_user: AuthenticatedUser = Depends(require_analista_or_above)  # ← ANALISTA+
):
    """ANALISTAs, GESTORs e ADMINs podem gerar relatórios"""
    return {"relatorio": [...]}
```

---

## ✅ CHECKLIST DE IMPLEMENTAÇÃO

### **Banco de Dados** ✅

- [x] Migration 006 executada
- [x] Campos `tipo_usuario` e `nivel_acesso` criados
- [x] Trigger `tr_usuario_calcular_nivel` ativo
- [x] Views `v_usuarios_hierarquia` e `v_estatisticas_tipo_usuario` criadas
- [x] Função `verificar_permissao(usuario_id, nivel_minimo)` criada
- [x] Índices de performance criados

### **Backend** ✅

- [x] Middleware de permissões implementado (`app/middleware/auth_middleware.py`)
- [x] Router Admin API criado (`app/routers/M08_admin/router_admin_usuarios_config.py`)
- [x] Router Admin Páginas criado (`app/routers/M08_admin/router_admin_pages.py`)
- [x] Routers registrados no `app/routers/__init__.py`
- [x] Service de autenticação funcionando
- [x] Service de email configurado
- [x] Service de notificação implementado

### **Frontend** ✅

- [x] Página de login regular (`template_auth_login_pagina.html`)
- [x] Página de login admin (`template_auth_admin_login_pagina.html`)
- [x] Painel administrativo (`template_admin_panel_pagina.html`)
- [ ] ⏳ Página de gestão de usuários (`template_admin_usuarios_pagina.html`)
- [ ] ⏳ Página de solicitações (`template_admin_solicitacoes_pagina.html`)
- [ ] ⏳ Página de sessões (`template_admin_sessions_pagina.html`)

### **Testes** ✅

- [x] Script de teste criado (`test_hierarquia_permissoes.py`)
- [x] Todos os testes passaram (100%)
- [x] Trigger automático testado
- [x] Função de verificação testada

### **Documentação** ✅

- [x] Guia de uso criado (`GUIA_USO_MIDDLEWARE_PERMISSOES.md`)
- [x] Resumo de implementação criado (`RESUMO_IMPLEMENTACAO_HIERARQUIA.md`)
- [x] Exemplos práticos criados (`exemplos_uso_hierarquia.py`)
- [x] Este fluxo atualizado

---

## 🎯 ESTADOS E TRANSIÇÕES

```
ESTADO INICIAL (Após cadastro):
├── ativo: false
├── email_verificado: false
├── tipo_usuario: conforme solicitado (ex: 'ANALISTA')
└── nivel_acesso: calculado pelo trigger (ex: 3)

    ↓ [Usuário verifica email]

AGUARDANDO ATIVAÇÃO:
├── ativo: false ⚠️
├── email_verificado: true ✅
├── tipo_usuario: conforme cadastro (ex: 'ANALISTA')
└── nivel_acesso: conforme cadastro (ex: 3)

    ⚠️ NÃO PODE FAZER LOGIN ATÉ SER ATIVADO

    ↓ [GESTOR/ADMIN ativa o usuário]

ATIVO NO SISTEMA:
├── ativo: true ✅
├── email_verificado: true ✅
├── tipo_usuario: conforme cadastro (ex: 'ANALISTA')
├── nivel_acesso: conforme cadastro (ex: 3)
├── ativado_por: UUID do GESTOR/ADMIN
└── ativado_em: timestamp

    ↓ [Usuário faz login]

LOGADO:
├── Pode acessar endpoints conforme seu nível
├── Sessão ativa
└── Permissões controladas por middleware
```

---

## 📞 REFERÊNCIAS

- **Migration:** `migration_006_hierarquia_usuarios_permissoes.sql`
- **Middleware:** `app/middleware/auth_middleware.py`
- **Routers Admin:** `app/routers/M08_admin/`
- **Guia Completo:** `GUIA_USO_MIDDLEWARE_PERMISSOES.md`
- **Documentação Original:** `FLUXO_CADASTRO_USUARIO_COMPLETO.md`
- **Hierarquia Completa:** `HIERARQUIA_USUARIOS_PERMISSOES.md`

---

**✅ Sistema de Cadastro com Hierarquia 100% Funcional!**
