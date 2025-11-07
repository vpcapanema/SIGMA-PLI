# 📘 SISTEMA DE USUÁRIOS - SIGMA-PLI (Explicação Completa)

**Data:** 03/11/2025  
**Objetivo:** Documentar como funciona o sistema de usuários, suas tabelas e relacionamentos

---

## 🎯 CONCEITO FUNDAMENTAL

O sistema SIGMA-PLI possui **DUAS CAMADAS DE PESSOA**:

### 1️⃣ **Camada de Cadastro** (Schema `cadastro`)

- **`cadastro.pessoa`**: Pessoas físicas cadastradas no sistema (público geral)
- **`cadastro.instituicao`**: Instituições cadastradas no sistema
- **Propósito**: Registro público de pessoas e instituições (não necessariamente usuários do sistema)

### 2️⃣ **Camada de Usuários** (Schema `usuarios`)

- **`usuarios.pessoa`**: Cópia/extensão de dados da pessoa para usuários autenticados
- **`usuarios.conta_usuario`**: Credenciais de login (username, senha, tokens)
- **Propósito**: Autenticação e controle de acesso ao sistema

---

## 📊 ARQUITETURA DE TABELAS

```
┌─────────────────────────────────────────────────────────────────┐
│                        SCHEMA: cadastro                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  cadastro.pessoa (36 colunas - PÚBLICO)                         │
│  ┌───────────────────────────────────────────────────┐          │
│  │ • id (PK)                                         │          │
│  │ • nome_completo, cpf, email, telefone             │          │
│  │ • nome_social, data_nascimento, sexo              │          │
│  │ • estado_civil, nacionalidade, naturalidade       │          │
│  │ • nome_pai, nome_mae                              │          │
│  │ • rg, orgao_expeditor, uf_rg, data_expedicao_rg   │          │
│  │ • titulo_eleitor, zona_eleitoral, secao_eleitoral │          │
│  │ • pis_pasep, email_secundario, telefone_secundario│          │
│  │ • profissao, escolaridade, renda_mensal           │          │
│  │ • cep, logradouro, numero, complemento            │          │
│  │ • bairro, cidade, uf, pais                        │          │
│  │ • ativa, created_at                               │          │
│  └───────────────────────────────────────────────────┘          │
│                                                                 │
│  cadastro.instituicao (11 colunas)                              │
│  ┌───────────────────────────────────────────────────┐          │
│  │ • id (PK)                                         │          │
│  │ • nome, sigla, cnpj                               │          │
│  │ • tipo (federal/estadual/municipal/privada)       │          │
│  │ • endereco (texto livre)                          │          │
│  │ • telefone, email, site                           │          │
│  │ • ativa, created_at                               │          │
│  └───────────────────────────────────────────────────┘          │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                        SCHEMA: usuarios                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  usuarios.pessoa (17 colunas - USUÁRIOS AUTENTICADOS)           │
│  ┌───────────────────────────────────────────────────┐          │
│  │ • id (PK)                                         │          │
│  │ • nome_completo, primeiro_nome, ultimo_nome       │          │
│  │ • email, telefone, cpf                            │          │
│  │ • data_nascimento, genero, foto_url               │          │
│  │ • instituicao_id (FK → cadastro.instituicao)      │          │
│  │ • departamento_id (FK → cadastro.departamento)    │          │
│  │ • cargo, matricula                                │          │
│  │ • ativo, criado_em, atualizado_em                 │          │
│  └───────────────────────────────────────────────────┘          │
│                         │                                       │
│                         │ pessoa_id (FK)                        │
│                         ▼                                       │
│  usuarios.conta_usuario (17 colunas - CREDENCIAIS)              │
│  ┌───────────────────────────────────────────────────┐          │
│  │ • id (PK)                                         │          │
│  │ • pessoa_id (FK → usuarios.pessoa)                │          │
│  │ • username (UNIQUE), email (UNIQUE)               │          │
│  │ • password_hash, salt                             │          │
│  │ • email_verificado, telefone_verificado           │          │
│  │ • dois_fatores_habilitado, secreto_2fa            │          │
│  │ • ultimo_login, ultimo_ip                         │          │
│  │ • tentativas_falha, bloqueado_ate                 │          │
│  │ • ativo, criado_em, atualizado_em                 │          │
│  └───────────────────────────────────────────────────┘          │
│                         │                                       │
│          ┌──────────────┼──────────────┐                        │
│          │              │              │                        │
│          ▼              ▼              ▼                        │
│  ┌─────────────┐ ┌─────────────┐ ┌──────────────┐              │
│  │  sessao     │ │ token_recup │ │tentativa_login│              │
│  │─────────────│ │─────────────│ │──────────────│              │
│  │ token       │ │ token       │ │ username     │              │
│  │ refresh_*   │ │ tipo        │ │ ip_address   │              │
│  │ expires_at  │ │ usado       │ │ sucesso      │              │
│  └─────────────┘ └─────────────┘ └──────────────┘              │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 FLUXO: Como uma Pessoa se Torna Usuário

### **Passo 1: Cadastro Inicial (Público)**

```
Pessoa física preenche formulário
         ↓
INSERT em cadastro.pessoa (36 colunas)
         ↓
Recebe ID: pessoa_publica_id
```

### **Passo 2: Solicitação de Acesso ao Sistema**

```
Pessoa solicita criar conta de usuário
         ↓
1. Criar registro em usuarios.pessoa
   - Copia dados básicos de cadastro.pessoa
   - Adiciona: instituicao_id, departamento_id, cargo
         ↓
2. Criar registro em usuarios.conta_usuario
   - Associa com usuarios.pessoa (FK pessoa_id)
   - Define: username, password_hash, salt
         ↓
3. Usuário agora pode fazer login!
```

---

## ⚠️ PROBLEMA IDENTIFICADO NO SISTEMA ATUAL

### **Confusão entre `cadastro.pessoa` e `usuarios.pessoa`**

**Situação atual:**

```python
# service_pessoa.py (ERRADO)
def create_pessoa_fisica():
    # Está inserindo em usuarios.pessoa
    # Deveria inserir em cadastro.pessoa
    INSERT INTO usuarios.pessoa  # ❌ ERRADO!
```

**Como deveria ser:**

```python
# service_cadastro.py (CORRETO)
def create_pessoa_fisica():
    # Cadastro público usa cadastro.pessoa
    INSERT INTO cadastro.pessoa  # ✅ CORRETO!

# service_usuario.py (CORRETO)
def create_conta_usuario(pessoa_publica_id):
    # 1. Criar usuarios.pessoa com dados da pessoa_publica
    INSERT INTO usuarios.pessoa (
        SELECT dados FROM cadastro.pessoa
        WHERE id = pessoa_publica_id
    )

    # 2. Criar conta com credenciais
    INSERT INTO usuarios.conta_usuario (
        pessoa_id = usuarios_pessoa_id,
        username = ...,
        password_hash = ...
    )
```

---

## 🔑 FK CRÍTICA: `usuarios.conta_usuario.pessoa_id`

### **Problema:**

```sql
CREATE TABLE usuarios.conta_usuario (
    pessoa_id UUID REFERENCES usuarios.pessoa(id)  -- ⚠️ Aponta para usuarios.pessoa
);
```

### **Opções de Solução:**

#### **Opção A: Manter FK para `usuarios.pessoa` (ATUAL)**

```
Fluxo:
1. Cadastro público → cadastro.pessoa
2. Criar conta:
   a) Copiar dados → usuarios.pessoa
   b) Criar credenciais → usuarios.conta_usuario (FK → usuarios.pessoa)

Vantagem: usuarios.pessoa pode ter campos extras (cargo, matricula)
Desvantagem: Duplicação de dados
```

#### **Opção B: Apontar FK para `cadastro.pessoa`** (ALTERNATIVA)

```sql
ALTER TABLE usuarios.conta_usuario
DROP CONSTRAINT conta_usuario_pessoa_id_fkey;

ALTER TABLE usuarios.conta_usuario
ADD CONSTRAINT conta_usuario_pessoa_id_fkey
FOREIGN KEY (pessoa_id) REFERENCES cadastro.pessoa(id);
```

```
Fluxo:
1. Cadastro público → cadastro.pessoa
2. Criar conta:
   a) Criar credenciais → usuarios.conta_usuario (FK → cadastro.pessoa)

Vantagem: Sem duplicação
Desvantagem: Perde campos extras de usuarios.pessoa (cargo, matricula)
```

#### **Opção C: Usar Trigger para Sincronizar** (HÍBRIDA)

```sql
CREATE TRIGGER sync_usuarios_pessoa
AFTER INSERT ON cadastro.pessoa
FOR EACH ROW
EXECUTE FUNCTION sync_to_usuarios_pessoa();
```

```
Fluxo:
1. Cadastro público → cadastro.pessoa
   ↓ (trigger automático)
2. Cópia automática → usuarios.pessoa
3. Criar conta → usuarios.conta_usuario (FK → usuarios.pessoa)

Vantagem: Sincronização automática
Desvantagem: Complexidade
```

---

## 🎯 DECISÃO RECOMENDADA

### **Solução: Opção A (Manter arquitetura atual com correção)**

**Justificativa:**

1. `usuarios.pessoa` tem campos específicos de usuário (cargo, matricula, instituicao_id)
2. `cadastro.pessoa` é cadastro público completo (36 campos)
3. Nem toda pessoa cadastrada precisa ser usuário
4. Usuários podem ter dados específicos de vínculo institucional

**Implementação:**

```python
# 1. Cadastro Público (página de cadastro de PF)
async def cadastrar_pessoa_fisica(dados):
    """Insere em cadastro.pessoa"""
    pessoa_id = await db.execute("""
        INSERT INTO cadastro.pessoa (
            nome_completo, cpf, email, telefone,
            data_nascimento, sexo, rg, ...
        ) VALUES ($1, $2, $3, ...)
        RETURNING id
    """, dados)
    return pessoa_id

# 2. Criar Conta de Usuário (requer aprovação/convite)
async def criar_conta_usuario(pessoa_cadastro_id, cargo, instituicao_id):
    """Promove pessoa de cadastro.pessoa para usuário"""

    # Copiar dados básicos para usuarios.pessoa
    usuarios_pessoa_id = await db.execute("""
        INSERT INTO usuarios.pessoa (
            nome_completo, email, telefone, cpf,
            cargo, instituicao_id, departamento_id
        )
        SELECT
            nome_completo, email, telefone, cpf,
            $1, $2, $3
        FROM cadastro.pessoa
        WHERE id = $4
        RETURNING id
    """, cargo, instituicao_id, departamento_id, pessoa_cadastro_id)

    # Criar credenciais
    await db.execute("""
        INSERT INTO usuarios.conta_usuario (
            pessoa_id, username, email, password_hash, salt
        ) VALUES ($1, $2, $3, $4, $5)
    """, usuarios_pessoa_id, username, email, hash, salt)
```

---

## 📝 RESUMO DAS TABELAS

| Tabela            | Schema     | Propósito                             | Colunas | Quem usa                                |
| ----------------- | ---------- | ------------------------------------- | ------- | --------------------------------------- |
| `pessoa`          | `cadastro` | Cadastro público de pessoas físicas   | 36      | Qualquer pessoa que preenche formulário |
| `instituicao`     | `cadastro` | Cadastro público de instituições      | 11      | Instituições cadastradas                |
| `pessoa`          | `usuarios` | Dados de pessoas com conta de usuário | 17      | Apenas usuários autenticados            |
| `conta_usuario`   | `usuarios` | Credenciais de login                  | 17      | Apenas usuários autenticados            |
| `sessao`          | `usuarios` | Tokens e sessões ativas               | 10      | Sistema de autenticação                 |
| `tentativa_login` | `usuarios` | Auditoria de logins                   | 9       | Sistema de segurança                    |

---

## 🔐 SISTEMA DE AUTENTICAÇÃO

### **Hash de Senha**

```python
# PBKDF2-HMAC-SHA256
iterations = 100_000  # OWASP recommended
salt = secrets.token_hex(16)  # 16 bytes = 32 caracteres hex
password_hash = hashlib.pbkdf2_hmac(
    'sha256',
    password.encode(),
    salt.encode(),
    iterations
).hex()
```

### **Sessão e Tokens**

```python
session_token = secrets.token_urlsafe(32)   # 43 caracteres base64
refresh_token = secrets.token_urlsafe(32)   # 43 caracteres base64
expires_at = now + timedelta(hours=24)      # 24 horas
```

### **Proteção Brute Force**

```python
# Após 5 tentativas falhadas:
bloqueado_ate = now + timedelta(minutes=30)
# Conta fica bloqueada por 30 minutos
```

---

## 🚀 PRÓXIMOS PASSOS

### 1. **Corrigir Service Layer**

- [ ] Renomear `service_pessoa.py` → `service_cadastro.py`
- [ ] Criar `service_usuario.py` para usuários autenticados
- [ ] Separar rotas: `/api/cadastro/*` vs `/api/usuario/*`

### 2. **Implementar Fluxo de Aprovação**

- [ ] Cadastro público → `cadastro.pessoa`
- [ ] Admin aprova → cria `usuarios.pessoa` + `usuarios.conta_usuario`
- [ ] Envia email com credenciais temporárias

### 3. **Página de Usuário**

- [ ] Criar formulário específico para criar conta
- [ ] Selecionar pessoa de `cadastro.pessoa`
- [ ] Definir cargo, instituição, departamento
- [ ] Gerar username e senha inicial

---

## 📚 DOCUMENTOS DE REFERÊNCIA

1. **`ARQUITETURA_AUTENTICACAO.md`** - Diagramas e fluxos
2. **`ddl_modulo_autenticacao.sql`** - DDL completo das tabelas
3. **`RELATORIO_INTEGRACAO_BD_AUTENTICACAO.md`** - Serviços implementados
4. **`RELATORIO_ANALISE_CAMPOS_VS_COLUNAS.md`** - Análise de campos vs colunas

---

## ✅ CONCLUSÃO

O sistema possui uma arquitetura em **2 camadas**:

1. **Camada Pública** (`cadastro`): Qualquer pessoa/instituição pode se cadastrar
2. **Camada Restrita** (`usuarios`): Apenas pessoas aprovadas têm conta de usuário

**Relacionamento:**

```
cadastro.pessoa (cadastro público)
    ↓ (quando aprovado)
usuarios.pessoa (dados de usuário)
    ↓ (FK pessoa_id)
usuarios.conta_usuario (credenciais)
```

**Status Atual:**

- ✅ Tabelas criadas e estruturadas
- ✅ Sistema de autenticação implementado
- ✅ `cadastro.pessoa` expandida com 36 colunas
- ⚠️ Service layer precisa ser refatorado para usar tabelas corretas
- ⚠️ Páginas HTML precisam ser ajustadas para campos corretos
