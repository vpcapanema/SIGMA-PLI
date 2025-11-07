# 📍 MAPA COMPLETO DE URLs - SIGMA-PLI

## Estrutura de Rotas após Consolidação

### 🟢 PÁGINAS PÚBLICAS (sem autenticação)

#### Cadastro

| Rota                             | Método | Descrição                  | Arquivo                                         |
| -------------------------------- | ------ | -------------------------- | ----------------------------------------------- |
| `/auth/cadastro-pessoa-fisica`   | GET    | Página de cadastro PF      | `public/router_pages_cadastro_pessoa_fisica.py` |
| `/auth/cadastro-pessoa`          | GET    | Alias para cadastro PF     | `public/router_pages_cadastro_pessoa_fisica.py` |
| `/auth/cadastro-pessoa-juridica` | GET    | Página de cadastro PJ      | `public/router_pages_cadastro_instituicao.py`   |
| `/auth/cadastro-instituicao`     | GET    | Alias para cadastro PJ     | `public/router_pages_cadastro_instituicao.py`   |
| `/auth/cadastro-usuario`         | GET    | Página de cadastro usuário | `public/router_pages_cadastro_usuario.py`       |

#### APIs Públicas de Cadastro

| Rota                          | Método | Descrição         | Arquivo                         |
| ----------------------------- | ------ | ----------------- | ------------------------------- |
| `/api/cadastro/pessoa-fisica` | POST   | Criar PF          | `public/router_api_cadastro.py` |
| `/api/cadastro/instituicao`   | POST   | Criar instituição | `public/router_api_cadastro.py` |

#### Login

| Rota                    | Método | Descrição             | Arquivo                       |
| ----------------------- | ------ | --------------------- | ----------------------------- |
| `/auth/login`           | GET    | Página de login       | `router_auth_login_logout.py` |
| `/auth/recuperar-senha` | GET    | Página de recuperação | `router_auth_login_logout.py` |
| `/api/v1/auth/login`    | POST   | Endpoint de login     | `router_auth_api.py`          |
| `/api/v1/auth/register` | POST   | Endpoint de registro  | `router_auth_api.py`          |

---

### 🔵 PÁGINAS RESTRITAS (com autenticação)

#### Gerenciamento

| Rota               | Método | Descrição                           | Arquivo                                  |
| ------------------ | ------ | ----------------------------------- | ---------------------------------------- |
| `/pessoa-fisica`   | GET    | Página de gerenciamento PF          | `restrito/router_pages_pessoa_fisica.py` |
| `/pessoa-juridica` | GET    | Página de gerenciamento PJ          | `restrito/router_pages_instituicao.py`   |
| `/usuarios`        | GET    | Página de gerenciamento de usuários | `restrito/router_pages_usuarios.py`      |

---

### 🏠 HOME & STATUS

| Rota             | Método | Descrição           |
| ---------------- | ------ | ------------------- |
| `/`              | GET    | Página home         |
| `/health`        | GET    | Health check        |
| `/api/v1/status` | GET    | Status da aplicação |
| `/api/status`    | GET    | Alias para status   |

---

## 📝 URLs que FORAM REMOVIDAS

❌ `/api/v1/pessoas/fisicas` - REMOVIDO (listava PF)
❌ `/api/v1/pessoas/juridicas` - REMOVIDO (listava PJ)
❌ `/api/v1/pessoas/pessoa-fisica` - REMOVIDO
❌ `/api/v1/pessoas/pessoa-juridica` - REMOVIDO
❌ `/api/v1/pessoas/instituicao` - REMOVIDO
❌ `/api/cadastro/pessoa-juridica` - REMOVIDO (endpoint legado, usar `/api/cadastro/instituicao`)

---

## 🔄 SUBSTITUIÇÕES NECESSÁRIAS NOS SCRIPTS JS

### ❌ REMOVER / DESABILITAR

1. **`script_pessoa_fisica.js`** - Remove referência a `/api/v1/pessoa-fisica` (linha ~22)

   - Esta página é apenas de visualização pós-login
   - Não há endpoint para listar pessoas criadas por usuários
   - Manter apenas estrutura básica

2. **`script_pessoa_juridica.js`** - Remove referência a `/api/v1/pessoa-juridica` (linha ~20)

   - Esta página é apenas de visualização pós-login
   - Não há endpoint para listar instituições criadas por usuários
   - Manter apenas estrutura básica

3. **`script_cadastro_usuario_novo.js`** - Já removido as chamadas para `/api/v1/pessoas/fisicas` e `/api/v1/pessoas/juridicas` ✅

### ✅ URL PADRÃO PARA CADASTROS

Todos os cadastros públicos devem usar:

- **`POST /api/cadastro/pessoa-fisica`** - Para criar PF
- **`POST /api/cadastro/instituicao`** - Para criar instituição

---

## 📌 Referências Cruzadas

| Script                            | Arquivo               | Status       | Ações Necessárias            |
| --------------------------------- | --------------------- | ------------ | ---------------------------- |
| `script_pessoa_fisica.js`         | `static/js/M01_auth/` | ⚠️ OBSOLETO  | Remover DataTable AJAX       |
| `script_pessoa_juridica.js`       | `static/js/M01_auth/` | ⚠️ OBSOLETO  | Remover DataTable AJAX       |
| `script_cadastro_usuario_novo.js` | `static/js/M01_auth/` | ✅ CORRIGIDO | Usar `/api/v1/auth/register` |
| `script_auth_cadastro.js`         | `static/js/M01_auth/` | ❓ REVISAR   | Verificar qual endpoint usa  |

---

## 🚀 FLUXOS DE CADASTRO

### Fluxo 1: Cadastro de Pessoa Física

```
1. GET /auth/cadastro-pessoa-fisica → Página com formulário
2. Preencher e submeter formulário
3. POST /api/cadastro/pessoa-fisica → Cria pessoa
4. Retorna pessoa_id
5. Usar pessoa_id para criar usuário (se necessário)
```

### Fluxo 2: Cadastro de Instituição

```
1. GET /auth/cadastro-instituicao → Página com formulário
2. Preencher e submeter formulário
3. POST /api/cadastro/instituicao → Cria instituição
4. Retorna pessoa_id (UUID da instituição)
5. Usar pessoa_id para criar usuário (se necessário)
```

### Fluxo 3: Cadastro de Usuário

```
1. GET /auth/cadastro-usuario → Página com formulário
2. Selecionar PF e instituição previamente criadas (ou IDs diretos)
3. POST /api/v1/auth/register → Cria usuário
4. Retorna token de sesão
5. Redireciona para login ou area restrita
```

---

## ⚠️ OBSERVAÇÕES

1. **Tabela `usuarios.pessoa` foi DELETADA** - Não use mais
2. **Dados de PF** agora estão em `cadastro.pessoa`
3. **Dados de PJ** agora estão em `cadastro.instituicao`
4. **Links de usuários** agora apontam para `cadastro.pessoa` via `pessoa_id` FK

---

**Última atualização:** 4 de novembro de 2025
**Status:** Em consolidação
