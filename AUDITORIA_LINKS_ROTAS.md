# 📋 AUDITORIA DE LINKS - Verificação de Rotas

## 🔍 Links Encontrados vs Rotas Criadas

### ✅ LINKS VÁLIDOS (Rotas Existem)

| Link HTML                               | Rota Esperada                        | Status    | Arquivo                                  |
| --------------------------------------- | ------------------------------------ | --------- | ---------------------------------------- |
| `href="/auth"`                          | GET `/auth`                          | ✅ EXISTE | router_auth_pages.py                     |
| `href="/auth/login"`                    | GET `/auth/login`                    | ✅ EXISTE | router_auth_pages.py                     |
| `href="/auth/logout"`                   | GET `/auth/logout`                   | ✅ EXISTE | router_auth_pages.py                     |
| `href="/auth/recuperar-senha"`          | GET `/auth/recuperar-senha`          | ✅ EXISTE | router_auth_pages.py                     |
| `href="/auth/sobre"`                    | GET `/auth/sobre`                    | ✅ EXISTE | router_auth_pages.py                     |
| `href="/auth/admin-login"`              | GET `/auth/admin-login`              | ✅ EXISTE | router_auth_pages.py                     |
| `href="/auth/cadastro-pessoa-fisica"`   | GET `/auth/cadastro-pessoa-fisica`   | ✅ EXISTE | router_pages_cadastro_pessoa_fisica.py   |
| `href="/auth/cadastro-pessoa-juridica"` | GET `/auth/cadastro-pessoa-juridica` | ✅ EXISTE | router_pages_cadastro_instituicao.py     |
| `href="/auth/cadastro-usuario"`         | GET `/auth/cadastro-usuario`         | ✅ EXISTE | router_pages_cadastro_usuario.py         |
| `href="/dashboard"`                     | GET `/dashboard`                     | ✅ EXISTE | router_auth_pages.py                     |
| `href="/pessoa-fisica"`                 | GET `/pessoa-fisica`                 | ✅ EXISTE | router_pages_pessoa_fisica.py (restrito) |
| `href="/pessoa-juridica"`               | GET `/pessoa-juridica`               | ✅ EXISTE | router_pages_instituicao.py (restrito)   |
| `href="/usuarios"`                      | GET `/usuarios`                      | ✅ EXISTE | router_pages_usuarios.py (restrito)      |

**Total**: 13 links válidos ✅

---

### ⚠️ LINKS QUEBRADOS OU PROBLEMAS

| Link HTML                      | Rota Esperada              | Status          | Problema                 | Localização                           |
| ------------------------------ | -------------------------- | --------------- | ------------------------ | ------------------------------------- |
| `href="/api/v1/auth/logout"`   | POST `/api/v1/auth/logout` | ⚠️ PROBLEMA     | É **POST** não GET       | `template_admin_panel_pagina.html:54` |
| `href="/dashboard.html"`       | GET `/dashboard`           | ❌ QUEBRADO     | Link aponta para `.html` | Vários templates legacy               |
| `href="/pessoa-fisica.html"`   | GET `/pessoa-fisica`       | ❌ QUEBRADO     | Link aponta para `.html` | Vários templates legacy               |
| `href="/pessoa-juridica.html"` | GET `/pessoa-juridica`     | ❌ QUEBRADO     | Link aponta para `.html` | Vários templates legacy               |
| `href="/usuarios.html"`        | GET `/usuarios`            | ❌ QUEBRADO     | Link aponta para `.html` | Vários templates legacy               |
| `href="/api/docs"`             | GET `/api/docs`            | ❓ DESCONHECIDO | Swagger/OpenAPI          | `template_home_index_pagina.html:272` |

---

## 🚨 Problemas Encontrados

### 1. **CRÍTICO**: Link para POST como GET

```html
<!-- ❌ ERRADO - template_admin_panel_pagina.html:54 -->
<a href="/api/v1/auth/logout" class="nav-link text-danger"></a>
```

**Problema**: Um link `<a href>` é GET, mas `/api/v1/auth/logout` é POST
**Solução**: Converter em formulário ou usar JavaScript para POST

---

### 2. **CRÍTICO**: Links legados com extensão .html

```html
<!-- ❌ ERRADO - template_pli_base_pagina.html:60 -->
<a class="pli-navbar__brand" href="/dashboard.html">
  <!-- ❌ ERRADO - template_pli_base_pagina.html:69 -->
  <a class="pli-navbar__dropdown-link" href="/pessoa-fisica.html"></a
></a>
```

**Problema**: Apontam para arquivos `.html` que não existem
**Localização**:

- `templates/pages/PLI_base/template_pli_base_pagina.html`
- `templates/legacy_pli/base_from_pli.html`
- `templates/pages/M01_auth/legacy/base_from_pli.html`

**Solução**: Remover extensão `.html`

---

### 3. **DESCONHECIDO**: Link para API docs

```html
<!-- ❓ VERIFICAR - template_home_index_pagina.html:272 -->
<li><a href="/api/docs">Documentação API</a></li>
```

**Problema**: Não tenho certeza se `/api/docs` existe
**Solução**: Testar ou remover

---

## 📁 Arquivos com Problemas

### Arquivos com Links `.html` (LEGACY)

1. `templates/pages/PLI_base/template_pli_base_pagina.html` - ❌ 4 links `.html`
2. `templates/legacy_pli/base_from_pli.html` - ❌ 4 links `.html`
3. `templates/pages/M01_auth/legacy/base_from_pli.html` - ❌ 4 links `.html`

### Arquivos com POST como GET

1. `templates/pages/M01_auth/admin/template_admin_panel_pagina.html:54` - ⚠️ `/api/v1/auth/logout`

---

## ✅ Checklist de Correção

### PRIORIDADE ALTA

- [ ] Converter `/api/v1/auth/logout` em formulário POST

  - Local: `template_admin_panel_pagina.html:54`
  - Criar formulário oculto ou usar JavaScript

- [ ] Remover/Atualizar links `.html` em templates legacy

  - Local: `template_pli_base_pagina.html` (4 links)
  - Local: `base_from_pli.html` (2 arquivos, 4 links cada)
  - Converter: `/dashboard.html` → `/dashboard`
  - Converter: `/pessoa-fisica.html` → `/pessoa-fisica`
  - Converter: `/pessoa-juridica.html` → `/pessoa-juridica`
  - Converter: `/usuarios.html` → `/usuarios`

- [ ] Verificar se `/api/docs` existe
  - Local: `template_home_index_pagina.html:272`

### VERIFICAÇÃO

- [ ] Testar cada link no navegador
- [ ] Verificar se cookies de logout são deletados
- [ ] Verificar redirects funcionam

---

## 🎯 Rotas Confirmadas como Existentes

✅ **Públicas (sem autenticação):**

- `GET /` - Home
- `GET /auth` - Auth index
- `GET /auth/login` - Login page
- `GET /auth/logout` - Logout (novo!)
- `GET /auth/recuperar-senha` - Password reset
- `GET /auth/sobre` - About
- `GET /auth/admin-login` - Admin login
- `GET /auth/cadastro-pessoa-fisica` - PF registration
- `GET /auth/cadastro-pessoa-juridica` - PJ registration
- `GET /auth/cadastro-usuario` - User registration

✅ **Restritas (com autenticação):**

- `GET /dashboard` - Dashboard
- `GET /pessoa-fisica` - PF dashboard
- `GET /pessoa-juridica` - PJ dashboard
- `GET /usuarios` - Users dashboard

✅ **APIs:**

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/logout`
- `POST /api/v1/auth/register`
- `GET /api/v1/auth/me`

---

## 🔗 Template Componentes

Componentes usados em vários templates:

- `templates/pages/M01_auth/components/navbar.html` - ✅ Todos links corretos
- `templates/pages/M01_auth/components/footer.html` - ✅ Links corretos

---

## 📊 Resumo

| Categoria           | Total  | Válidos | Quebrados | Ação               |
| ------------------- | ------ | ------- | --------- | ------------------ |
| Links públicos      | 13     | 13 ✅   | 0         | Nenhuma            |
| Links legacy        | 12     | 0 ❌    | 12        | Corrigir `.html`   |
| Links POST como GET | 1      | 0 ⚠️    | 1         | Converter form     |
| Desconhecidos       | 1      | ?       | ?         | Testar             |
| **TOTAL**           | **27** | **13**  | **13**    | ⚠️ AÇÃO NECESSÁRIA |

---

**Status**: 🟡 **AUDITORIA COMPLETA - AÇÃO NECESSÁRIA**
**Próximo Passo**: Corrigir links `.html` e converter POST como GET
