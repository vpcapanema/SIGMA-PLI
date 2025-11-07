# 🗺️ Mapa de Navegação - SIGMA-PLI

## 📋 Visão Geral

Este documento mapeia todas as rotas disponíveis no SIGMA-PLI e como elas se conectam.

---

## 🏠 Módulo Home (M00)

### Rotas Públicas

| Rota             | Descrição                         | Template                                   | Status |
| ---------------- | --------------------------------- | ------------------------------------------ | ------ |
| `/`              | Página inicial do sistema         | `M00_home/template_home_index_pagina.html` | ✅     |
| `/health`        | Health check da aplicação         | JSON response                              | ✅     |
| `/api/v1/status` | Status do sistema (JSON)          | -                                          | ✅     |
| `/api/status`    | Alias para status (usado pelo JS) | -                                          | ✅     |

---

## 🔐 Módulo Autenticação (M01)

### 📄 Páginas Públicas (Login/Cadastro)

| Rota                             | Descrição                  | Template                                             | Botões de Navegação                                     |
| -------------------------------- | -------------------------- | ---------------------------------------------------- | ------------------------------------------------------- |
| `/login`                         | Página de login (alias)    | `template_auth_login_pagina.html`                    | → `/auth/recuperar-senha`<br>→ `/auth/cadastro-usuario` |
| `/auth/login`                    | Página de login (canônica) | `template_auth_login_pagina.html`                    | → `/auth/recuperar-senha`<br>→ `/auth/cadastro-usuario` |
| `/auth/index`                    | Página inicial do módulo   | `template_auth_index_pagina.html`                    | → `/login`<br>→ `/recursos`                             |
| `/auth/recuperar-senha`          | Recuperação de senha       | `template_auth_recuperar_senha_pagina.html`          | → `/auth/login`<br>→ `/`                                |
| `/auth/cadastro-pessoa-fisica`   | Cadastro de PF             | `template_auth_cadastro_pessoa_fisica_pagina.html`   | → `/auth/login`                                         |
| `/auth/cadastro-pessoa-juridica` | Cadastro de PJ             | `template_auth_cadastro_pessoa_juridica_pagina.html` | → `/auth/login`                                         |
| `/auth/cadastro-usuario`         | Cadastro de usuário        | `template_auth_cadastro_usuario_pagina.html`         | → `/auth/login`<br>→ `/auth/cadastro-pessoa-fisica`     |
| `/auth/admin-login`              | Login administrativo       | `template_auth_admin_login_pagina.html`              | → `/auth/login`                                         |
| `/auth/sobre`                    | Sobre o sistema            | `template_auth_sobre_pagina.html`                    | → `/`<br>→ `/recursos`                                  |

### 📄 Páginas Públicas Standalone

| Rota                 | Descrição                       | Template                                               | Botões de Navegação                                                                                              |
| -------------------- | ------------------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------- |
| `/acesso-negado`     | Erro 403 - Acesso Negado        | `public/template_public_acesso_negado_pagina.html`     | → `/auth/login`<br>→ `/`                                                                                         |
| `/email-verificado`  | Sucesso na verificação de email | `public/template_public_email_verificado_pagina.html`  | → `/auth/login` (auto-redirect 10s)<br>→ `/`                                                                     |
| `/selecionar-perfil` | Seleção de perfil (multi-role)  | `public/template_public_selecionar_perfil_pagina.html` | → `/dashboard?perfil=admin`<br>→ `/dashboard?perfil=gestor`<br>→ `/dashboard?perfil=usuario`<br>→ `/auth/logout` |
| `/recursos`          | Recursos e funcionalidades      | `public/template_public_recursos_pagina.html`          | → `/auth/login`<br>→ `/auth/cadastro-usuario`                                                                    |

### 🔒 Páginas com Autenticação Obrigatória

| Rota                     | Descrição                   | Template                                         | Requer Auth | Botões de Navegação                                         |
| ------------------------ | --------------------------- | ------------------------------------------------ | ----------- | ----------------------------------------------------------- |
| `/dashboard`             | Dashboard principal         | `app/template_dashboard_pagina.html`             | ✅          | → `/pessoa-fisica`<br>→ `/pessoa-juridica`<br>→ `/usuarios` |
| `/admin/panel`           | Painel administrativo       | `admin/template_admin_panel_pagina.html`         | ✅ (Admin)  | → `/usuarios`<br>→ `/sessions-manager`                      |
| `/meus-dados`            | Dados do usuário logado     | `app/template_meus_dados_pagina.html`            | ✅          | → `/dashboard`                                              |
| `/pessoa-fisica`         | Gestão de Pessoas Físicas   | `app/template_pessoa_fisica_pagina.html`         | ✅          | → `/dashboard`<br>→ `/pessoa-juridica`                      |
| `/pessoa-juridica`       | Gestão de Pessoas Jurídicas | `app/template_pessoa_juridica_pagina.html`       | ✅          | → `/dashboard`<br>→ `/pessoa-fisica`                        |
| `/usuarios`              | Gestão de Usuários          | `app/template_usuarios_pagina.html`              | ✅          | → `/dashboard`<br>→ `/meus-dados`                           |
| `/solicitacoes-cadastro` | Solicitações de Cadastro    | `app/template_solicitacoes_cadastro_pagina.html` | ✅          | → `/dashboard`<br>→ `/pessoa-fisica`                        |
| `/sessions-manager`      | Gerenciador de Sessões      | `app/template_sessions_manager_pagina.html`      | ✅ (Admin)  | → `/admin/panel`<br>→ `/dashboard`                          |

### 🧪 Rotas de Teste (Desenvolvimento)

| Rota                     | Descrição                   | Mock User                                                  |
| ------------------------ | --------------------------- | ---------------------------------------------------------- |
| `/teste/pessoa-fisica`   | Teste PF sem auth           | `{"nome": "Usuário Teste", "email": "teste@sigma.gov.br"}` |
| `/teste/pessoa-juridica` | Teste PJ sem auth           | `{"nome": "Usuário Teste", "email": "teste@sigma.gov.br"}` |
| `/teste/usuarios`        | Teste Usuários sem auth     | `{"nome": "Usuário Teste", "email": "teste@sigma.gov.br"}` |
| `/teste/solicitacoes`    | Teste Solicitações sem auth | `{"nome": "Usuário Teste", "email": "teste@sigma.gov.br"}` |
| `/teste/dashboard`       | Teste Dashboard sem auth    | `{"nome": "Usuário Teste", "email": "teste@sigma.gov.br"}` |

---

## 🔄 Fluxos de Navegação Principais

### 1️⃣ Fluxo de Login Simples

```
/ (Home)
  ↓
/auth/login (Login)
  ↓ (após autenticação)
/dashboard (Dashboard)
  ↓
/pessoa-fisica, /pessoa-juridica, /usuarios, etc.
```

### 2️⃣ Fluxo de Cadastro de Pessoa Física

```
/ (Home)
  ↓
/auth/cadastro-pessoa-fisica (Formulário PF)
  ↓ (submit)
/email-verificado (Sucesso + auto-redirect 10s)
  ↓
/auth/login (Login)
  ↓
/dashboard
```

### 3️⃣ Fluxo de Cadastro de Usuário

```
/ (Home)
  ↓
/auth/cadastro-usuario (Formulário Usuário)
  ↓ (submit)
/email-verificado (Sucesso + auto-redirect 10s)
  ↓
/auth/login (Login)
  ↓
/dashboard
```

### 4️⃣ Fluxo de Recuperação de Senha

```
/auth/login
  ↓ (clique "Esqueci minha senha")
/auth/recuperar-senha (Cards sequenciais)
  ↓ (envio email)
(Email enviado - verificar inbox)
  ↓ (clique no link do email)
/auth/recuperar-senha?token=XXX (Redefinir senha)
  ↓ (nova senha definida)
/auth/login
```

### 5️⃣ Fluxo de Seleção de Perfil (Multi-Role)

```
/auth/login
  ↓ (usuário tem múltiplos perfis)
/selecionar-perfil
  ↓ (clique no perfil desejado)
/dashboard?perfil=admin (ou gestor/usuario)
```

### 6️⃣ Fluxo de Acesso Negado (403)

```
(qualquer rota protegida sem auth)
  ↓
/acesso-negado (Erro 403)
  ↓
/auth/login (ou / para voltar à home)
```

### 7️⃣ Fluxo de Exploração de Recursos

```
/ (Home)
  ↓
/recursos (Info sobre funcionalidades)
  ↓
/auth/login (CTA "Fazer Login")
  ou
/auth/cadastro-usuario (CTA "Criar Conta")
```

---

## 🎨 Páginas com Design SIGMA Standalone

Estas páginas **não dependem** do `template_base_auth.html` e possuem **todos os estilos inline**:

- ✅ `/acesso-negado` - Erro 403 com ícone pulsante
- ✅ `/email-verificado` - Sucesso com countdown timer
- ✅ `/selecionar-perfil` - Cards de perfil (Admin/Gestor/Usuário)
- ✅ `/recursos` - Hero + Features + Módulos + CTA

**Características**:

- Bootstrap 5.3.2 via CDN
- Font Awesome 6.4.0 via CDN
- Google Fonts Montserrat via CDN
- CSS inline com gradientes SIGMA (#0b1729 → #162a48)
- JavaScript inline (quando necessário)
- Mobile-first e responsivo

---

## 📊 Códigos HTTP Esperados

| Código                    | Significado    | Quando Ocorre                                 |
| ------------------------- | -------------- | --------------------------------------------- |
| 200 OK                    | Sucesso        | Rota pública acessível ou usuário autenticado |
| 403 Forbidden             | Acesso Negado  | Rota protegida sem autenticação válida        |
| 404 Not Found             | Não Encontrado | Rota não existe                               |
| 500 Internal Server Error | Erro Interno   | Problema no servidor/template                 |

---

## 🧪 Como Testar

### Opção 1: Script Python (Recomendado)

```bash
# Instalar dependências
pip install httpx rich

# Executar teste completo
python test_all_routes.py
```

O script testará:

- ✅ Todas as rotas públicas (devem retornar 200)
- ✅ Todas as rotas protegidas (devem retornar 403 sem auth)
- ✅ Todas as rotas de teste (devem retornar 200)
- ✅ Fluxos de navegação completos

### Opção 2: Manualmente no Navegador

1. **Inicie o servidor**:

   ```bash
   uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload
   ```

2. **Teste as rotas públicas** (devem carregar):

   - http://127.0.0.1:8010/
   - http://127.0.0.1:8010/auth/login
   - http://127.0.0.1:8010/recursos
   - http://127.0.0.1:8010/acesso-negado
   - http://127.0.0.1:8010/email-verificado
   - http://127.0.0.1:8010/selecionar-perfil

3. **Teste as rotas protegidas** (devem redirecionar para login ou 403):

   - http://127.0.0.1:8010/dashboard
   - http://127.0.0.1:8010/pessoa-fisica
   - http://127.0.0.1:8010/usuarios

4. **Teste as rotas de desenvolvimento** (devem carregar sem auth):
   - http://127.0.0.1:8010/teste/dashboard
   - http://127.0.0.1:8010/teste/pessoa-fisica
   - http://127.0.0.1:8010/teste/usuarios

### Opção 3: cURL/HTTPie

```bash
# Testar home
curl http://127.0.0.1:8010/

# Testar rota pública
curl http://127.0.0.1:8010/recursos

# Testar rota protegida (deve retornar 403)
curl http://127.0.0.1:8010/dashboard

# Testar API status
curl http://127.0.0.1:8010/api/status
```

---

## 🔗 Links Rápidos para Desenvolvimento

| Tipo              | URL                                         |
| ----------------- | ------------------------------------------- |
| Home              | http://127.0.0.1:8010/                      |
| Login             | http://127.0.0.1:8010/auth/login            |
| Recursos          | http://127.0.0.1:8010/recursos              |
| Dashboard (teste) | http://127.0.0.1:8010/teste/dashboard       |
| PF (teste)        | http://127.0.0.1:8010/teste/pessoa-fisica   |
| PJ (teste)        | http://127.0.0.1:8010/teste/pessoa-juridica |
| Usuários (teste)  | http://127.0.0.1:8010/teste/usuarios        |
| API Docs          | http://127.0.0.1:8010/api/docs              |
| Health Check      | http://127.0.0.1:8010/health                |

---

## 📝 Notas Importantes

1. **Rotas de Teste**: As rotas `/teste/*` foram criadas para desenvolvimento e **não devem** estar disponíveis em produção.

2. **Autenticação**: Rotas protegidas usam `Depends(require_authenticated_user)` do módulo `app.utils.auth_session`.

3. **Templates Base**: A maioria das páginas usa `template_base_auth.html` como base, exceto as 4 páginas standalone em `/public/`.

4. **Ano Dinâmico**: Todas as rotas passam `year: datetime.utcnow().year` para o rodapé.

5. **Mock User**: Rotas de teste injetam `{"nome": "Usuário Teste", "email": "teste@sigma.gov.br"}` para simular usuário autenticado.

---

**Última atualização**: 02/11/2025
