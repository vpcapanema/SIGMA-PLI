# 🔐 Guia de Uso: Middleware de Permissões e Hierarquia

## Sistema SIGMA-PLI - Hierarquia de 5 Níveis

---

## 📊 Hierarquia de Usuários

| Nível | Tipo           | Descrição     | Permissões                                    |
| ----- | -------------- | ------------- | --------------------------------------------- |
| **5** | `ADMIN`        | Administrador | Acesso total ao sistema, gestão de permissões |
| **4** | `GESTOR`       | Gestor        | Gerenciar usuários, aprovar cadastros         |
| **3** | `ANALISTA`     | Analista      | Consultar dados, gerar relatórios             |
| **2** | `OPERADOR`     | Operador      | Inserir e editar dados                        |
| **1** | `VISUALIZADOR` | Visualizador  | Apenas consultar dados (read-only)            |

---

## 🚀 Como Usar nos Routers

### 1. **Importar o Middleware**

```python
from app.middleware.auth_middleware import (
    require_admin,              # Nível 5
    require_admin_or_gestor,    # Nível 4+
    require_analista_or_above,  # Nível 3+
    require_operador_or_above,  # Nível 2+
    verify_permission_level,    # Nível customizado
)
from app.schemas.M01_auth.schema_auth import AuthenticatedUser
from fastapi import Depends
```

---

### 2. **Proteger Endpoints com Permissões**

#### ✅ **Exemplo 1: Endpoint ADMIN apenas (Nível 5)**

```python
@router.delete("/usuarios/{id}")
async def deletar_usuario(
    id: UUID,
    current_user: AuthenticatedUser = Depends(require_admin)
):
    """
    Deletar usuário (soft delete)

    Permissão: ADMIN (nível 5)
    """
    # Apenas ADMINs podem executar este código
    return {"message": "Usuário deletado"}
```

---

#### ✅ **Exemplo 2: Endpoint GESTOR ou superior (Nível 4+)**

```python
@router.post("/usuarios/aprovar/{id}")
async def aprovar_cadastro(
    id: UUID,
    current_user: AuthenticatedUser = Depends(require_admin_or_gestor)
):
    """
    Aprovar solicitação de cadastro

    Permissão: GESTOR ou ADMIN (nível 4+)
    """
    # GESTOR e ADMIN podem executar
    return {"message": "Cadastro aprovado"}
```

---

#### ✅ **Exemplo 3: Endpoint ANALISTA ou superior (Nível 3+)**

```python
@router.get("/relatorios/vendas")
async def gerar_relatorio_vendas(
    current_user: AuthenticatedUser = Depends(require_analista_or_above)
):
    """
    Gerar relatório de vendas

    Permissão: ANALISTA, GESTOR ou ADMIN (nível 3+)
    """
    # ANALISTA, GESTOR e ADMIN podem executar
    return {"relatorio": [...]}
```

---

#### ✅ **Exemplo 4: Endpoint OPERADOR ou superior (Nível 2+)**

```python
@router.post("/produtos")
async def criar_produto(
    produto: ProdutoCreate,
    current_user: AuthenticatedUser = Depends(require_operador_or_above)
):
    """
    Criar novo produto

    Permissão: OPERADOR ou superior (nível 2+)
    """
    # OPERADOR, ANALISTA, GESTOR e ADMIN podem executar
    return {"message": "Produto criado"}
```

---

#### ✅ **Exemplo 5: Nível customizado**

```python
from functools import partial

# Criar função customizada para nível 3
require_nivel_3 = partial(verify_permission_level, 3)

@router.get("/dados-sensiveis")
async def listar_dados_sensiveis(
    current_user: AuthenticatedUser = Depends(require_nivel_3)
):
    """
    Permissão: Nível 3 ou superior
    """
    return {"dados": [...]}
```

---

### 3. **Endpoints Públicos (Sem Permissão)**

```python
@router.get("/")
async def status():
    """Endpoint público - não requer autenticação"""
    return {"status": "ok"}
```

---

## 📦 Estrutura de Retorno do `current_user`

Quando você usa `Depends(require_admin)`, você recebe um objeto `AuthenticatedUser`:

```python
{
    "conta_id": "uuid-do-usuario",
    "username": "joao.silva",
    "nome_completo": "João Silva",
    "email": "joao.silva@sigma.gov.br",
    "primeiro_nome": "João",
    "ultimo_nome": "Silva",
    "ultimo_login": "2025-11-03T10:30:00"
}
```

---

## 🔥 Exemplo Completo: Router Admin

```python
from fastapi import APIRouter, Depends
from app.middleware.auth_middleware import (
    require_admin,
    require_admin_or_gestor,
    require_analista_or_above,
)
from app.schemas.M01_auth.schema_auth import AuthenticatedUser

router = APIRouter(prefix="/api/v1/admin", tags=["Admin"])

# Público (não requer permissão)
@router.get("/")
async def status():
    return {"module": "admin", "status": "active"}

# Nível 3+ (ANALISTA, GESTOR, ADMIN)
@router.get("/usuarios")
async def listar_usuarios(
    current_user: AuthenticatedUser = Depends(require_analista_or_above)
):
    return {"usuarios": [...]}

# Nível 4+ (GESTOR, ADMIN)
@router.put("/usuarios/{id}/tipo")
async def atualizar_tipo_usuario(
    id: UUID,
    current_user: AuthenticatedUser = Depends(require_admin_or_gestor)
):
    return {"message": "Tipo atualizado"}

# Nível 5 (ADMIN apenas)
@router.delete("/usuarios/{id}")
async def deletar_usuario(
    id: UUID,
    current_user: AuthenticatedUser = Depends(require_admin)
):
    return {"message": "Usuário deletado"}
```

---

## ⚠️ Tratamento de Erros

### **Erro 401: Não Autenticado**

```json
{
  "detail": "Token de autenticação não fornecido"
}
```

### **Erro 403: Sem Permissão**

```json
{
  "detail": "Acesso negado. Apenas usuários do tipo ADMIN podem realizar esta ação."
}
```

### **Erro 503: Banco Indisponível**

```json
{
  "detail": "Serviço de banco de dados indisponível"
}
```

---

## 🗄️ Banco de Dados

### **Tabela `usuarios.usuario`**

- `tipo_usuario`: VARCHAR(50) - 'ADMIN', 'GESTOR', 'ANALISTA', 'OPERADOR', 'VISUALIZADOR'
- `nivel_acesso`: INTEGER - 1 a 5 (calculado automaticamente por trigger)

### **Trigger Automático**

Quando você atualiza `tipo_usuario`, o `nivel_acesso` é calculado automaticamente:

```sql
UPDATE usuarios.usuario
SET tipo_usuario = 'ADMIN'
WHERE username = 'joao.silva';
-- nivel_acesso será automaticamente definido como 5
```

### **Views Úteis**

#### `usuarios.v_usuarios_hierarquia`

```sql
SELECT * FROM usuarios.v_usuarios_hierarquia;
```

#### `usuarios.v_estatisticas_tipo_usuario`

```sql
SELECT * FROM usuarios.v_estatisticas_tipo_usuario;
```

### **Função de Verificação**

```sql
SELECT usuarios.verificar_permissao(
    'uuid-do-usuario'::uuid,
    4  -- nivel mínimo
);
-- Retorna true se nivel_acesso >= 4
```

---

## 📚 Arquivos Criados

| Arquivo                                                 | Descrição                       |
| ------------------------------------------------------- | ------------------------------- |
| `app/middleware/auth_middleware.py`                     | Middleware de permissões        |
| `app/routers/M08_admin/router_admin_usuarios_config.py` | API Admin (protegida)           |
| `app/routers/M08_admin/router_admin_pages.py`           | Páginas Admin (HTML)            |
| `migration_006_hierarquia_usuarios_permissoes.sql`      | Migration executada com sucesso |

---

## ✅ Status da Implementação

- ✅ Migration 006 executada (campos `tipo_usuario` e `nivel_acesso` criados)
- ✅ Trigger automático funcionando (calcula `nivel_acesso` ao atualizar `tipo_usuario`)
- ✅ Middleware de permissões criado (`app/middleware/auth_middleware.py`)
- ✅ Router admin API criado com 8 endpoints protegidos
- ✅ Router admin páginas criado (renderiza templates HTML)
- ✅ Routers registrados em `app/routers/__init__.py`
- ✅ Views e função de verificação disponíveis
- ✅ Páginas de login existem:
  - `template_auth_login_pagina.html` (login regular)
  - `template_auth_admin_login_pagina.html` (login admin)
  - `template_admin_panel_pagina.html` (painel admin)

---

## 🎯 Próximos Passos

1. **Testar os endpoints:**

   ```bash
   # Iniciar aplicação
   uvicorn app.main:app --host 127.0.0.1 --port 8010

   # Acessar documentação interativa
   http://127.0.0.1:8010/docs
   ```

2. **Criar usuário ADMIN de teste:**

   ```sql
   UPDATE usuarios.usuario
   SET tipo_usuario = 'ADMIN'
   WHERE username = 'joao.silva';
   ```

3. **Testar permissões:**

   - Login como ADMIN → Acesso total
   - Login como GESTOR → Não pode deletar usuários
   - Login como VISUALIZADOR → Apenas consultar

4. **Implementar templates faltantes:**
   - `template_admin_usuarios_pagina.html`
   - `template_admin_solicitacoes_pagina.html`
   - `template_admin_sessions_pagina.html`

---

## 📞 Suporte

Para dúvidas ou problemas, consulte:

- `HIERARQUIA_USUARIOS_PERMISSOES.md` (documentação completa)
- `FLUXO_CADASTRO_USUARIO_COMPLETO.md` (fluxo de cadastro)
- Código-fonte: `app/middleware/auth_middleware.py`
