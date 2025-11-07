# MAPA DE ROTAS - M01_AUTH (SIGMA-PLI)

## Atualizado: 04/11/2025

Este documento mapeia todas as rotas ativas do módulo M01_AUTH (Autenticação e Cadastros).

---

## 1. PÁGINAS PÚBLICAS (SEM AUTENTICAÇÃO)

### 1.1 Cadastro de Pessoa Física (PF)

- **Rota HTTP**: `GET /auth/cadastro-pessoa-fisica`
- **Alias**: `GET /auth/cadastro-pessoa`
- **Router File**: `app/routers/M01_auth/public/router_pages_cadastro_pessoa_fisica.py`
- **Template**: `pages/M01_auth/template_auth_cadastro_pessoa_pagina.html`
- **Descrição**: Página pública para registro de pessoa física

### 1.2 Cadastro de Instituição / Pessoa Jurídica (PJ)

- **Rota HTTP**: `GET /auth/cadastro-pessoa-juridica`
- **Alias**: `GET /auth/cadastro-instituicao`
- **Router File**: `app/routers/M01_auth/public/router_pages_cadastro_instituicao.py`
- **Template**: `pages/M01_auth/template_auth_cadastro_instituicao_pagina.html`
- **Descrição**: Página pública para registro de instituição/empresa

### 1.3 Cadastro de Usuário (Criação de Conta)

- **Rota HTTP**: `GET /auth/cadastro-usuario`
- **Router File**: `app/routers/M01_auth/public/router_pages_cadastro_usuario.py`
- **Template**: `pages/M01_auth/template_auth_cadastro_usuario_pagina.html`
- **Descrição**: Página pública para criar usuário (após registrar PF/PJ)

### 1.4 Páginas Públicas Adicionais

- `GET /auth/login` - Login
- `GET /auth/index` - Página inicial do módulo
- `GET /auth/recuperar-senha` - Recuperação de senha
- `GET /auth/sobre` - Página sobre o sistema
- `GET /acesso-negado` - Erro 403
- `GET /email-verificado` - Confirmação de email
- `GET /selecionar-perfil` - Seleção de perfil
- `GET /recursos` - Informações de recursos

---

## 2. PÁGINAS RESTRITAS (COM AUTENTICAÇÃO)

### 2.1 Gerenciamento de Pessoa Física

- **Rota HTTP**: `GET /pessoa-fisica`
- **Router File**: `app/routers/M01_auth/restrito/router_pages_pessoa_fisica.py`
- **Template**: `pages/M01_auth/app/template_pessoa_fisica_pagina.html`
- **Autenticação**: Requerida (Dependência: `require_authenticated_user`)
- **Descrição**: Dashboard para visualizar/gerenciar dados de pessoa física

### 2.2 Gerenciamento de Instituição / Pessoa Jurídica

- **Rota HTTP**: `GET /pessoa-juridica`
- **Router File**: `app/routers/M01_auth/restrito/router_pages_instituicao.py`
- **Template**: `pages/M01_auth/app/template_pessoa_juridica_pagina.html`
- **Autenticação**: Requerida
- **Descrição**: Dashboard para visualizar/gerenciar dados de instituição

### 2.3 Gerenciamento de Usuários

- **Rota HTTP**: `GET /usuarios`
- **Router File**: `app/routers/M01_auth/restrito/router_pages_usuarios.py`
- **Template**: `pages/M01_auth/app/template_usuarios_pagina.html`
- **Autenticação**: Requerida
- **Descrição**: Página para gerenciar usuários do sistema

### 2.4 Páginas Restritas Adicionais

- `GET /dashboard` - Dashboard principal
- `GET /admin/panel` - Painel administrativo
- `GET /meus-dados` - Meus dados pessoais
- `GET /solicitacoes-cadastro` - Solicitações pendentes
- `GET /sessions-manager` - Gerenciador de sessões

---

## 3. APIs REST (Dados)

### 3.1 Autenticação

- **POST** `/api/v1/auth/login` - Realizar login
- **POST** `/api/v1/auth/logout` - Fazer logout
- **GET** `/api/v1/auth/me` - Dados do usuário logado
- **POST** `/api/v1/auth/register` - Registrar novo usuário
- **POST** `/api/v1/auth/refresh` - Renovar token
- **POST** `/api/v1/auth/request-password-reset` - Solicitar reset de senha
- **POST** `/api/v1/auth/forgot-password` - **Alias** para request-password-reset
- **POST** `/api/v1/auth/reset-password` - Executar reset de senha
- **POST** `/api/v1/auth/verify-email` - Verificar email

**Router File**: `app/routers/M01_auth/router_auth_api.py`

### 3.2 Pessoas (Listagem)

- **GET** `/api/v1/pessoas/fisicas` - Listar pessoas físicas (para dropdowns)
- **GET** `/api/v1/pessoas/juridicas` - Listar instituições (para dropdowns)

**Router File**: `app/routers/M01_auth/router_pessoas_api.py`

### 3.3 Cadastro Público de Pessoa Física

- **POST** `/api/v1/cadastro/pessoa` - Criar pessoa física
- **GET** `/api/v1/cadastro/pessoa?cpf=...` - Buscar por CPF
- **GET** `/api/v1/cadastro/pessoa?email=...` - Buscar por email

**Router File**: `app/routers/M01_auth/router_cadastro_pessoa.py`

### 3.4 Cadastro Público de Pessoa Jurídica / Instituição

- **POST** `/api/v1/cadastro/instituicao` - Criar instituição
- **GET** `/api/v1/cadastro/instituicao?cnpj=...` - Buscar por CNPJ

**Router File**: `app/routers/M01_auth/router_cadastro_instituicao.py`

### 3.5 APIs Adicionais

- **POST** `/api/v1/pessoas/pessoa-fisica` - Criar pessoa física (via router pessoas)
- **POST** `/api/v1/pessoas/instituicao` - Criar instituição (via router pessoas)
- **POST** `/api/v1/pessoas/pessoa-juridica` - **Legado**, usa `/instituicao`

---

## 4. ESTRUTURA DE DIRETÓRIOS

```
app/routers/M01_auth/
├── public/                                          # Páginas SEM autenticação
│   ├── __init__.py
│   ├── router_pages_cadastro_pessoa_fisica.py      # GET /auth/cadastro-pessoa-fisica
│   ├── router_pages_cadastro_instituicao.py        # GET /auth/cadastro-pessoa-juridica
│   └── router_pages_cadastro_usuario.py            # GET /auth/cadastro-usuario
├── restrito/                                        # Páginas COM autenticação
│   ├── __init__.py
│   ├── router_pages_pessoa_fisica.py               # GET /pessoa-fisica
│   ├── router_pages_instituicao.py                 # GET /pessoa-juridica
│   └── router_pages_usuarios.py                    # GET /usuarios
├── router_auth_pages.py                            # Páginas públicas core (login, index, etc)
├── router_auth_api.py                              # APIs de autenticação e token
├── router_auth_login_logout.py                     # Página de logout redirect
├── router_pessoas_api.py                           # APIs de listagem de pessoas (fisicas/juridicas)
├── router_cadastro_pessoa.py                       # API pública de cadastro PF
├── router_cadastro_instituicao.py                  # API pública de cadastro PJ
├── router_externas_cpf_cep.py                      # APIs externas (validação de CPF/CEP)
└── router_localizacao_br.py                        # APIs de localização (estados/cidades)
```

---

## 5. FLUXOS DE USUÁRIO

### 5.1 Cadastro de Pessoa Física

1. Usuário acessa `GET /auth/cadastro-pessoa-fisica`
2. Preenche formulário na página
3. Frontend chama `POST /api/v1/cadastro/pessoa` ou `POST /api/v1/pessoas/pessoa-fisica`
4. Backend armazena em `cadastro.pessoa`
5. Retorna `pessoa_id`

### 5.2 Cadastro de Instituição

1. Usuário acessa `GET /auth/cadastro-pessoa-juridica`
2. Preenche formulário na página
3. Frontend chama `POST /api/v1/cadastro/instituicao` ou `POST /api/v1/pessoas/instituicao`
4. Backend armazena em `cadastro.instituicao`
5. Retorna `pessoa_id`

### 5.3 Cadastro de Usuário

1. Usuário acessa `GET /auth/cadastro-usuario`
2. Frontend carrega dropdowns com:
   - `GET /api/v1/pessoas/fisicas` → lista de PF
   - `GET /api/v1/pessoas/juridicas` → lista de PJ
3. Usuário seleciona PF/PJ e preenche dados de login
4. Frontend chama `POST /api/v1/auth/register`
5. Backend cria usuário em `usuarios.usuario` com link a pessoa_id e instituicao_id

### 5.4 Login

1. Usuário acessa `GET /auth/login` ou `GET /login`
2. Preenche email/username e senha
3. Frontend chama `POST /api/v1/auth/login`
4. Backend retorna JWT token
5. Frontend armazena token e redireciona para `/dashboard`

### 5.5 Acesso a Páginas Restritas

1. Usuário logado acessa `GET /pessoa-fisica`, `/pessoa-juridica`, `/usuarios`, etc.
2. Backend valida token via `require_authenticated_user`
3. Se válido, renderiza template com dados do usuário
4. Se inválido, retorna erro 403

---

## 6. BANCO DE DADOS

### Tabelas Principais

- **cadastro.pessoa** - Pessoas físicas (cpf, email, telefone, cargo, etc)
- **cadastro.instituicao** - Instituições/empresas (cnpj, nome, tipo, etc)
- **usuarios.usuario** - Contas de usuário (username, email, hash_senha, pessoa_id, instituicao_id)
- **usuarios.papel** - Papéis/permissões de usuários

---

## 7. MUDANÇAS RECENTES (04/11/2025)

### ✅ Finalizado

- Separação de rotas públicas em `public/`
- Separação de rotas restritas em `restrito/`
- Consolidação de APIs de autenticação em `router_auth_api.py`
- Remoção de rotas de teste duplicadas em `router_auth_pages.py`
- Normalização de field names (aliases) para compatibilidade front/back
- Adição de alias `/api/v1/auth/forgot-password` para `request-password-reset`

### 🔧 Ajustes de Schema

- `cadastro.pessoa`: Adicionadas colunas `cargo`, `instituicao_id`, `departamento_id`
- `cadastro.instituicao`: Usa campos `nome` (antes razao_social), `cnpj`, `email`, `telefone`, `tipo`, `site`
- Services normalizam entre aliases (e.g., `razao_social` → `nome`)

### 📝 Documentação

- Criado este arquivo `MAPA_ROTAS_M01_AUTH.md` como referência central

---

## 8. VALIDAÇÃO / PRÓXIMOS PASSOS

- [ ] Teste `GET /health` → confirma que PostgreSQL está OK
- [ ] Teste `GET /api/v1/pessoas/fisicas` → lista vazia ou com dados
- [ ] Teste `GET /api/v1/pessoas/juridicas` → lista vazia ou com dados
- [ ] Teste `GET /auth/cadastro-pessoa-fisica` → carrega página corretamente
- [ ] Teste `POST /api/v1/cadastro/pessoa` → cria registro em cadastro.pessoa
- [ ] Teste `GET /auth/cadastro-usuario` → carrega dropdowns de PF/PJ
- [ ] Teste `POST /api/v1/auth/register` → cria usuário com pessoa_id e instituicao_id
- [ ] Teste `POST /api/v1/auth/login` → retorna JWT válido
- [ ] Teste `GET /pessoa-fisica` (com token) → carrega página com autenticação

---

**Autor**: Copilot GitHub  
**Data**: 04 de novembro de 2025  
**Status**: ✅ ATIVO
