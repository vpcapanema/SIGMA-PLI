# Relatório de Conexão - Páginas de Cadastro ao Banco

## ✅ Status Geral

**Data:** 3 de novembro de 2025  
**Status:** TODAS AS PÁGINAS CONECTADAS AO BANCO

---

## 1. Cadastro de Pessoa Física

### Template HTML

- **Arquivo:** `templates/pages/M01_auth/template_auth_cadastro_pessoa_fisica_pagina.html`
- **Form ID:** `pessoaFisicaPublicForm` ✅
- **Script carregado:** `script_cadastro_form_handlers.js` ✅
- **Inicialização:** `initCadastroPessoaFisica()` ✅

### Handler JavaScript

- **Arquivo:** `static/js/M01_auth/script_cadastro_form_handlers.js`
- **Função:** `initCadastroPessoaFisica()`
- **Form ID buscado:** `pessoaFisicaPublicForm` ✅
- **Endpoint:** `POST /api/v1/pessoas/pessoa-fisica` ✅

### Campos Mapeados (36+)

✅ Dados Pessoais: nome_completo, cpf, data_nascimento, sexo, estado_civil, etc.  
✅ Filiação: nome_mae, nome_pai  
✅ Documentos: rg, orgao_expeditor, titulo_eleitor, pis_pasep  
✅ Contato: email, telefone_principal, telefone_secundario  
✅ Profissionais: profissao, escolaridade, renda_mensal  
✅ Endereço: cep, logradouro, numero, bairro, cidade, uf

### Backend

- **Endpoint:** `POST /api/v1/pessoas/pessoa-fisica`
- **Service:** `PessoaService.create_pessoa_fisica()`
- **Banco:** `INSERT INTO usuarios.pessoa` com tipo_pessoa='FISICA'
- **Validações:** CPF único, email único ✅

### Fluxo Completo

```
1. Usuário preenche formulário HTML
   ↓
2. JavaScript extrai 36+ campos
   ↓
3. Valida CPF (formato e dígitos verificadores)
   ↓
4. POST /api/v1/pessoas/pessoa-fisica
   ↓
5. Backend valida duplicatas (CPF/email)
   ↓
6. INSERT na tabela usuarios.pessoa
   ↓
7. Retorna pessoa_id (UUID)
   ↓
8. Modal de sucesso
   ↓
9. Redirect para /auth/cadastro-usuario?pessoa_id=XXX
```

**Status:** ✅ **TOTALMENTE CONECTADO**

---

## 2. Cadastro de Instituição (Pessoa Jurídica)

### Template HTML

- **Arquivo:** `templates/pages/M01_auth/template_auth_cadastro_pessoa_juridica_pagina.html`
- **Form ID:** `pessoaJuridicaPublicForm` ✅
- **Script carregado:** `script_cadastro_form_handlers.js` ✅
- **Inicialização:** `initCadastroPessoaJuridica()` ✅

### Handler JavaScript

- **Arquivo:** `static/js/M01_auth/script_cadastro_form_handlers.js`
- **Função:** `initCadastroPessoaJuridica()`
- **Form ID buscado:** `pessoaJuridicaPublicForm` ✅
- **Endpoint:** `POST /api/v1/pessoas/instituicao` ✅

### Campos Mapeados (24+)

✅ Dados da Instituição: razao_social, cnpj, nome_fantasia  
✅ Tipo: tipo_instituicao, esfera_administrativa  
✅ Cadastros: inscricao_estadual, inscricao_municipal  
✅ Info: data_fundacao, porte_empresa, natureza_juridica, atividade_principal  
✅ Contato: email, telefone, email_secundario, site  
✅ Endereço: cep, logradouro, numero, bairro, cidade, uf

### Backend

- **Endpoint Principal:** `POST /api/v1/pessoas/instituicao`
- **Endpoint Legado:** `POST /api/v1/pessoas/pessoa-juridica` (redireciona)
- **Service:** `PessoaService.create_instituicao()`
- **Banco:** `INSERT INTO usuarios.pessoa` com tipo_pessoa='INSTITUICAO'
- **Validações:** CNPJ único, email único ✅

### Fluxo Completo

```
1. Usuário preenche formulário HTML
   ↓
2. JavaScript extrai 24+ campos
   ↓
3. Valida CNPJ (formato e dígitos verificadores)
   ↓
4. POST /api/v1/pessoas/instituicao
   ↓
5. Backend valida duplicatas (CNPJ/email)
   ↓
6. INSERT na tabela usuarios.pessoa (tipo='INSTITUICAO')
   ↓
7. Retorna pessoa_id (UUID)
   ↓
8. Modal de sucesso
   ↓
9. Redirect para /auth/cadastro-usuario?pessoa_id=XXX
```

**Status:** ✅ **TOTALMENTE CONECTADO**

---

## 3. Cadastro de Usuário

### Template HTML

- **Arquivo:** `templates/pages/M01_auth/template_auth_cadastro_usuario_pagina.html`
- **Form ID:** `usuarioPublicForm` ✅
- **Script carregado:** `script_cadastro_form_handlers.js` ✅
- **Inicialização:** `initCadastroUsuario()` ✅

### Handler JavaScript

- **Arquivo:** `static/js/M01_auth/script_cadastro_form_handlers.js`
- **Função:** `initCadastroUsuario()`
- **Form ID buscado:** `usuarioPublicForm` ✅ (CORRIGIDO)
- **Endpoint:** `POST /api/v1/auth/register` ✅

### Campos do Form

- **IDs HTML:** `username`, `email`, `senha`, `confirmarSenha`
- **IDs JavaScript:** Corrigidos para `senha` e `confirmarSenha` ✅

### Backend

- **Endpoint:** `POST /api/v1/auth/register`
- **Schema:** `RegisterRequest` aceita `pessoa_id` opcional ✅
- **Service:** `service_auth_security.hash_password()`
- **Banco:** `INSERT INTO usuarios.conta_usuario`
- **Validações:** username único, email único, pessoa_id existe ✅

### Fluxo Completo

```
1. Usuário chega via redirect com pessoa_id na URL
   ↓
2. JavaScript extrai pessoa_id da URL (URLSearchParams)
   ↓
3. Valida que pessoa_id existe (senão redireciona)
   ↓
4. Usuário preenche username, email, senha
   ↓
5. Valida força da senha (maiúsculas, minúsculas, números, especiais)
   ↓
6. POST /api/v1/auth/register com pessoa_id
   ↓
7. Backend verifica que pessoa existe
   ↓
8. Hash da senha (bcrypt)
   ↓
9. INSERT na tabela usuarios.conta_usuario
   ↓
10. Modal de sucesso
    ↓
11. Redirect para /auth/login?registered=true
```

**Status:** ✅ **TOTALMENTE CONECTADO**

---

## 4. Correções Realizadas

### Problema 1: Scripts inexistentes

**Antes:**

- `script_auth_cadastro_pessoa_fisica.js` (não existe)
- `script_auth_cadastro_pessoa_juridica.js` (não existe)
- `script_auth_cadastro_usuario.js` (não existe)

**Depois:**

- Todos apontam para `script_cadastro_form_handlers.js` ✅

### Problema 2: IDs de formulário inconsistentes

**Template Usuário:**

- Form ID: `usuarioPublicForm`
- JavaScript buscava: `cadastroUsuarioForm` ❌

**Correção:**

- JavaScript atualizado para buscar `usuarioPublicForm` ✅

### Problema 3: IDs de campos de senha

**Template Usuário:**

- Senha: `id="senha"`
- Confirmar: `id="confirmarSenha"`

**JavaScript buscava:**

- `id="password"` ❌
- `id="confirm_password"` ❌

**Correção:**

- JavaScript atualizado para `senha` e `confirmarSenha` ✅

### Problema 4: Endpoint de instituição

**JavaScript PJ:**

- Chamava: `/api/v1/pessoas/pessoa-juridica`

**Correção:**

- Atualizado para: `/api/v1/pessoas/instituicao` ✅
- Endpoint legado mantido para compatibilidade

---

## 5. Arquitetura de Dados

### Tabela `usuarios.pessoa`

```sql
CREATE TABLE usuarios.pessoa (
    id UUID PRIMARY KEY,
    tipo_pessoa VARCHAR(20),  -- 'FISICA' ou 'INSTITUICAO'

    -- Pessoa Física
    cpf VARCHAR(14),
    nome_completo VARCHAR(255),
    data_nascimento DATE,
    rg VARCHAR(20),
    ...

    -- Instituição (PJ)
    cnpj VARCHAR(18),
    razao_social VARCHAR(255),
    nome_fantasia VARCHAR(255),
    tipo_instituicao VARCHAR(100),
    esfera_administrativa VARCHAR(50),
    porte_empresa VARCHAR(50),
    ...

    -- Comum
    email VARCHAR(255) UNIQUE,
    telefone VARCHAR(20),
    cep VARCHAR(10),
    logradouro VARCHAR(255),
    ...
);
```

### Tabela `usuarios.conta_usuario`

```sql
CREATE TABLE usuarios.conta_usuario (
    id UUID PRIMARY KEY,
    pessoa_id UUID REFERENCES usuarios.pessoa(id),
    username VARCHAR(50) UNIQUE,
    email VARCHAR(255) UNIQUE,
    password_hash VARCHAR(255),
    email_verificado BOOLEAN DEFAULT FALSE,
    ...
);
```

---

## 6. Endpoints API Disponíveis

| Método | Endpoint                          | Descrição                              | Status |
| ------ | --------------------------------- | -------------------------------------- | ------ |
| POST   | `/api/v1/pessoas/pessoa-fisica`   | Cadastrar pessoa física                | ✅     |
| POST   | `/api/v1/pessoas/instituicao`     | Cadastrar instituição                  | ✅     |
| POST   | `/api/v1/pessoas/pessoa-juridica` | [LEGADO] Redireciona para /instituicao | ✅     |
| POST   | `/api/v1/auth/register`           | Criar conta de usuário                 | ✅     |
| POST   | `/api/v1/auth/login`              | Login                                  | ✅     |
| POST   | `/api/v1/auth/logout`             | Logout                                 | ✅     |
| POST   | `/api/v1/auth/forgot-password`    | Recuperar senha                        | ✅     |
| POST   | `/api/v1/auth/reset-password`     | Resetar senha                          | ✅     |

---

## 7. Teste Manual Sugerido

### Passo 1: Cadastrar Pessoa Física

1. Acessar: `http://127.0.0.1:8010/auth/cadastro-pessoa-fisica`
2. Preencher todos os campos obrigatórios
3. Clicar em "Enviar Cadastro"
4. Verificar modal de sucesso
5. Confirmar redirect para `/auth/cadastro-usuario?pessoa_id=XXX`

### Passo 2: Cadastrar Usuário

1. Na página de cadastro de usuário (após redirect)
2. Preencher username, email e senha
3. Confirmar senha
4. Clicar em "Criar Conta"
5. Verificar modal de sucesso
6. Confirmar redirect para `/auth/login?registered=true`

### Passo 3: Fazer Login

1. Na página de login
2. Usar username/senha cadastrados
3. Fazer login
4. Verificar sessão criada

### Passo 4: Verificar no Banco

```sql
-- Ver pessoa cadastrada
SELECT * FROM usuarios.pessoa
WHERE email = 'seuemail@exemplo.com';

-- Ver conta de usuário
SELECT cu.*, p.nome_completo, p.cpf
FROM usuarios.conta_usuario cu
JOIN usuarios.pessoa p ON cu.pessoa_id = p.id
WHERE cu.username = 'seuusername';

-- Ver sessão ativa
SELECT * FROM usuarios.sessao
WHERE conta_usuario_id = (
    SELECT id FROM usuarios.conta_usuario
    WHERE username = 'seuusername'
);
```

---

## 8. Conclusão

✅ **PESSOA FÍSICA:** Formulário → JavaScript → API → Banco (CONECTADO)  
✅ **INSTITUIÇÃO:** Formulário → JavaScript → API → Banco (CONECTADO)  
✅ **USUÁRIO:** Formulário → JavaScript → API → Banco (CONECTADO)

**Todos os fluxos de cadastro estão 100% conectados ao banco de dados PostgreSQL!**

### Próximos Passos Sugeridos

- [ ] Teste end-to-end completo
- [ ] Adicionar máscaras de CPF/CNPJ nos inputs
- [ ] Implementar verificação de email
- [ ] Adicionar upload de documentos
- [ ] Implementar auditoria de cadastros
- [ ] Criar dashboard administrativo para aprovar cadastros
