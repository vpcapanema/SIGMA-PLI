# 📋 Distribuição de Rotas - Refatoração M01_auth

## 🎯 Mapeamento Proposto

### 📄 **router_auth_pages.py** (PÁGINAS - GET requests)

```
GET  /                                  Redireciona para /auth
GET  /auth                              Página inicial do módulo auth (index)
GET  /auth/index                        Alias para /auth
GET  /auth/login                        Página de login pública
GET  /login                             Alias para /auth/login
GET  /auth/recuperar-senha              Página de recuperação de senha
GET  /auth/sobre                        Página sobre o sistema
GET  /auth/admin-login                  Página de login administrativo
GET  /auth/logout                       ⭐ MOVER DAQUI - Executa logout e redireciona
GET  /acesso-negado                     Página de erro 403
GET  /email-verificado                  Página de sucesso - Email verificado
GET  /selecionar-perfil                 Página de seleção de perfil
GET  /recursos                          Página de recursos/funcionalidades

# 🔐 Restritas (com autenticação)
GET  /dashboard                         Dashboard principal
GET  /admin/panel                       Painel administrativo (ADMIN only)
GET  /meus-dados                        Página de dados do usuário
GET  /solicitacoes-cadastro             Solicitações de cadastro
GET  /sessions-manager                  Gerenciador de sessões
```

**Total**: 18 rotas de páginas

---

### 🔌 **router_auth_api.py** (APIs - POST/GET requests)

```
POST /api/v1/auth/login                 Login com username/email + senha
POST /api/v1/auth/logout                Logout (API - revoga sessão)
POST /api/v1/auth/register              Registro de novo usuário
GET  /api/v1/auth/me                    Obter dados do usuário autenticado
POST /api/v1/auth/refresh               Renovar tokens de sessão
POST /api/v1/auth/password-reset        Solicitar reset de senha
POST /api/v1/auth/password-reset/confirm  Confirmar reset de senha
```

**Total**: 7 endpoints de API

---

### ❌ **router_auth_login_logout.py** (DELETAR)

Atualmente contém:

```python
GET  /auth/logout                       ← MOVER para router_auth_pages.py
_revoke_session_from_request()          ← EXTRAIR para serviço
_release_conn()                         ← EXTRAIR para serviço
_client_ip()                            ← EXTRAIR para utilitário
```

---

## 🔄 O Que Muda

### ANTES (Confuso ❌)

```
router_auth_pages.py
├── GET  /auth/login
├── GET  /auth/logout           ← AQUI (mas pertence à lógica de autenticação)
├── GET  /dashboard
└── ... 15 outras

router_auth_login_logout.py
├── GET  /auth/logout           ← DUPLICADO AQUI (quase vazio)
└── Funções auxiliares órfãs

router_auth_api.py
├── POST /api/v1/auth/login
├── POST /api/v1/auth/logout
├── POST /api/v1/auth/register
└── ... 4 outras
```

### DEPOIS (Claro ✅)

```
router_auth_pages.py              ← TODAS AS PÁGINAS (GET)
├── GET  /auth/login
├── GET  /auth/logout             ← MOVE AQUI
├── GET  /dashboard
└── ... 15 outras

router_auth_api.py                ← TODAS AS APIs
├── POST /api/v1/auth/login
├── POST /api/v1/auth/logout
├── POST /api/v1/auth/register
└── ... 4 outras

❌ router_auth_login_logout.py     ← DELETADO
```

---

## 📊 Estatísticas

| Métrica                | Antes | Depois        |
| ---------------------- | ----- | ------------- |
| **Arquivos de Router** | 3     | 2             |
| **Rotas em pages**     | 17    | 18 (+1 moved) |
| **Endpoints em api**   | 7     | 7             |
| **Arquivos vazios**    | 1     | 0             |
| **Duplicação**         | Sim   | Não           |

---

## ✅ Vantagens da Nova Estrutura

| Aspecto         | Benefício                               |
| --------------- | --------------------------------------- |
| **Clareza**     | Cada arquivo tem responsabilidade única |
| **Localização** | Fácil achar página vs API               |
| **Manutenção**  | Sem comentários órfãos                  |
| **Escala**      | Padrão pronto para crescer              |
| **DRY**         | Sem duplicação de lógica                |

---

## 🚀 Implementação (Passo a Passo)

### Passo 1: Copiar GET /auth/logout para router_auth_pages.py

```python
@router.get("/auth/logout")
async def logout_page(request: Request) -> RedirectResponse:
    """Executa logout e redireciona para a página de login."""
    await _revoke_session_from_request(request)
    redirect = RedirectResponse(url="/auth/login", status_code=302)
    redirect.delete_cookie("auth_token", path="/")
    return redirect
```

### Passo 2: Adicionar imports necessários em router_auth_pages.py

```python
from fastapi.responses import RedirectResponse
from app.services.M01_auth.service_auth_logout import revoke_session_from_request
```

### Passo 3: Extrair lógica para service_auth_logout.py

```python
# app/services/M01_auth/service_auth_logout.py
async def revoke_session_from_request(request: Request) -> None:
    """Revoga sessão do cookie."""
```

### Passo 4: Atualizar app/routers/**init**.py

```python
# Remover
from app.routers.M01_auth.router_auth_login_logout import router as auth_login_logout_router

# Manter
from app.routers.M01_auth.router_auth_pages import router as auth_pages_router
from app.routers.M01_auth.router_auth_api import router as auth_api_router
```

### Passo 5: Deletar arquivo

```bash
rm app/routers/M01_auth/router_auth_login_logout.py
```

---

## 🎯 Resultado Final

### Estrutura Clara

```
app/routers/M01_auth/
├── router_auth_pages.py       ✅ 18 GET routes (páginas)
├── router_auth_api.py         ✅ 7 POST/GET routes (APIs)
├── public/                    ✅ Cadastros públicos
│   ├── router_pages_cadastro_pessoa_fisica.py
│   ├── router_pages_cadastro_instituicao.py
│   └── router_pages_cadastro_usuario.py
└── restrito/                  ✅ Páginas restritas
    ├── router_pages_pessoa_fisica.py
    ├── router_pages_instituicao.py
    └── router_pages_usuarios.py
```

### Padrão Modular Consistente

✅ **Módulo = Páginas + APIs Relacionadas**

- `router_auth_pages.py` = Páginas de autenticação
- `router_auth_api.py` = APIs de autenticação
- `public/router_pages_cadastro_*.py` = Página + API de cadastro
- `restrito/router_pages_*.py` = Página de dados restritos

---

## 🔍 Validação

### Checklist Pré-Refatoração

- [ ] Verificar todos os imports de `router_auth_login_logout` em `__init__.py`
- [ ] Conferir se há outras referências ao arquivo
- [ ] Testar rota `/auth/logout` funciona antes

### Checklist Pós-Refatoração

- [ ] Arquivo novo compilado sem erros
- [ ] `GET /auth/logout` funciona
- [ ] Cookies deletados corretamente
- [ ] Redireciona para `/auth/login`
- [ ] `POST /api/v1/auth/logout` continua funcionando
- [ ] Imports atualizados
- [ ] Arquivo deletado

---

**Status**: 🟡 PRONTO PARA IMPLEMENTAR
**Complexidade**: BAIXA
**Tempo**: ~10 minutos
