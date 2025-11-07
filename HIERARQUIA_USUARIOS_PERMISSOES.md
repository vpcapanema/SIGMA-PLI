# HIERARQUIA DE USUÁRIOS E PERMISSÕES - SIGMA-PLI

## Baseado no PLI-CADASTRO (Sistema de Login Administrativo)

**Data:** 03/11/2025  
**Fonte:** PLI-CADASTRO `documentation/SISTEMA-LOGIN-ADMIN-IMPLEMENTADO.md` e `authMiddleware.js`

---

## 📊 HIERARQUIA DE TIPOS DE USUÁRIO

### **5 Tipos de Usuário (do Maior para o Menor Nível)**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    HIERARQUIA DE USUÁRIOS                           │
└─────────────────────────────────────────────────────────────────────┘

🔴 ADMIN (Administrador)         - Nível 5 - Acesso Total
   └─ Pode: TUDO (aprovar, rejeitar, suspender, gerenciar sistema)
   └─ Login: Página separada (/admin-login.html)

🟠 GESTOR                         - Nível 4 - Gerenciamento
   └─ Pode: Aprovar/rejeitar solicitações, gerenciar usuários
   └─ Login: Página regular (/login.html)

🟡 ANALISTA                       - Nível 3 - Análise
   └─ Pode: Analisar dados, gerar relatórios
   └─ Login: Página regular (/login.html)

🟢 OPERADOR                       - Nível 2 - Operação
   └─ Pode: Executar operações básicas
   └─ Login: Página regular (/login.html)

🔵 VISUALIZADOR                   - Nível 1 - Somente Leitura
   └─ Pode: Apenas visualizar dados
   └─ Login: Página regular (/login.html)
```

---

## 🔐 REGRAS DE PERMISSÃO

### Middleware de Autenticação (authMiddleware.js)

**1. `verificarAutenticacao()`**

- Verifica se usuário está autenticado (token JWT válido)
- Aplica-se a: **TODOS os tipos de usuário**
- Retorna 401 se não autenticado

**2. `verificarPermissaoAdminGestor()`**

- Verifica se usuário é **ADMIN** ou **GESTOR**
- Usado para: Aprovar/rejeitar solicitações, gerenciar usuários
- Retorna 403 se não tiver permissão

**3. `verificarPermissaoAdmin()`**

- Verifica se usuário é **ADMIN** apenas
- Usado para: Operações críticas do sistema
- Retorna 403 se não for ADMIN

---

## 🎯 MATRIZ DE PERMISSÕES

| Funcionalidade              | ADMIN | GESTOR | ANALISTA | OPERADOR | VISUALIZADOR |
| --------------------------- | ----- | ------ | -------- | -------- | ------------ |
| **Autenticação**            |
| Login na aplicação          | ✅    | ✅     | ✅       | ✅       | ✅           |
| Redefinir própria senha     | ✅    | ✅     | ✅       | ✅       | ✅           |
| **Gestão de Usuários**      |
| Criar solicitação de acesso | ✅    | ✅     | ✅       | ✅       | ✅           |
| Aprovar solicitações        | ✅    | ✅     | ❌       | ❌       | ❌           |
| Rejeitar solicitações       | ✅    | ✅     | ❌       | ❌       | ❌           |
| Suspender usuários          | ✅    | ✅     | ❌       | ❌       | ❌           |
| Alterar nivel_acesso        | ✅    | ❌     | ❌       | ❌       | ❌           |
| Excluir usuários            | ✅    | ❌     | ❌       | ❌       | ❌           |
| **Cadastro**                |
| Criar pessoa física         | ✅    | ✅     | ✅       | ✅       | ❌           |
| Editar pessoa física        | ✅    | ✅     | ✅       | ❌       | ❌           |
| Excluir pessoa física       | ✅    | ✅     | ❌       | ❌       | ❌           |
| Visualizar pessoa física    | ✅    | ✅     | ✅       | ✅       | ✅           |
| **Relatórios**              |
| Gerar relatórios            | ✅    | ✅     | ✅       | ❌       | ❌           |
| Exportar dados              | ✅    | ✅     | ✅       | ❌       | ❌           |
| Visualizar estatísticas     | ✅    | ✅     | ✅       | ✅       | ✅           |
| **Sistema**                 |
| Acessar painel admin        | ✅    | ❌     | ❌       | ❌       | ❌           |
| Configurar sistema          | ✅    | ❌     | ❌       | ❌       | ❌           |
| Visualizar logs             | ✅    | ✅     | ❌       | ❌       | ❌           |
| Gerenciar sessões           | ✅    | ✅     | ❌       | ❌       | ❌           |

---

## 🔒 SEPARAÇÃO DE ACESSO (Login)

### **Login Regular** (`/login.html`)

- **Para:** GESTOR, ANALISTA, OPERADOR, VISUALIZADOR
- **Opções visíveis:** Apenas os 4 tipos não-admin
- **Acesso ao Admin:** Link discreto no footer ("Admin" com ícone de engrenagem)

### **Login Administrativo** (`/admin-login.html`)

- **Para:** ADMIN apenas
- **Campo tipo_usuario:** Fixo como "ADMIN" (hidden)
- **Visual:** Diferenciado (ícone escudo, cor warning/amarelo)
- **Segurança:** Validação dupla (frontend + backend)
- **Link de retorno:** Para login regular

---

## 📋 IMPLEMENTAÇÃO NO SIGMA-PRINCIPAL

### 1. Estrutura do Banco de Dados

**Campo `tipo_usuario`:**

```sql
ALTER TABLE usuarios.usuario
ADD COLUMN tipo_usuario VARCHAR(50) NOT NULL DEFAULT 'VISUALIZADOR';

ALTER TABLE usuarios.usuario
ADD CONSTRAINT ck_usuario_tipo_usuario CHECK (
    tipo_usuario IN ('ADMIN', 'GESTOR', 'ANALISTA', 'OPERADOR', 'VISUALIZADOR')
);

-- Índice para consultas por tipo
CREATE INDEX idx_usuario_tipo_usuario ON usuarios.usuario(tipo_usuario);
```

**Campo `nivel_acesso`:**

```sql
-- Mapeamento automático de tipo_usuario para nivel_acesso
CREATE OR REPLACE FUNCTION usuarios.calcular_nivel_acesso()
RETURNS TRIGGER AS $$
BEGIN
    NEW.nivel_acesso := CASE NEW.tipo_usuario
        WHEN 'ADMIN' THEN 5
        WHEN 'GESTOR' THEN 4
        WHEN 'ANALISTA' THEN 3
        WHEN 'OPERADOR' THEN 2
        WHEN 'VISUALIZADOR' THEN 1
        ELSE 1
    END;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER tr_usuario_calcular_nivel
    BEFORE INSERT OR UPDATE OF tipo_usuario ON usuarios.usuario
    FOR EACH ROW
    EXECUTE FUNCTION usuarios.calcular_nivel_acesso();
```

---

### 2. Backend (FastAPI/Python)

**Middleware de Permissão (`app/middleware/auth_middleware.py`):**

```python
from fastapi import HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List

security = HTTPBearer()

class PermissionChecker:
    """Verificador de permissões baseado em tipo de usuário"""

    def __init__(self, tipos_permitidos: List[str]):
        self.tipos_permitidos = tipos_permitidos

    def __call__(self, usuario: dict = Depends(get_current_user)):
        if usuario["tipo_usuario"] not in self.tipos_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado. Permissão insuficiente."
            )
        return usuario

# Instâncias reutilizáveis
verificar_admin = PermissionChecker(["ADMIN"])
verificar_admin_gestor = PermissionChecker(["ADMIN", "GESTOR"])
verificar_admin_gestor_analista = PermissionChecker(["ADMIN", "GESTOR", "ANALISTA"])
```

**Uso em Routers:**

```python
from app.middleware.auth_middleware import verificar_admin, verificar_admin_gestor

# Rota apenas para ADMIN
@router.delete("/usuarios/{usuario_id}")
async def excluir_usuario(
    usuario_id: str,
    current_user: dict = Depends(verificar_admin)
):
    # Apenas ADMIN pode excluir usuários
    pass

# Rota para ADMIN e GESTOR
@router.put("/solicitacoes/{id}/aprovar")
async def aprovar_solicitacao(
    id: str,
    current_user: dict = Depends(verificar_admin_gestor)
):
    # ADMIN e GESTOR podem aprovar
    pass
```

---

### 3. Frontend (Templates)

**Estrutura de Templates:**

```
templates/pages/M01_auth/
├── template_auth_login_regular.html      # Para GESTOR, ANALISTA, OPERADOR, VISUALIZADOR
└── template_auth_login_admin.html        # Para ADMIN apenas
```

**Login Regular (`template_auth_login_regular.html`):**

```html
<select id="tipo_usuario" name="tipo_usuario" required>
  <option value="">Selecione o tipo de acesso</option>
  <option value="GESTOR">Gestor</option>
  <option value="ANALISTA">Analista</option>
  <option value="OPERADOR">Operador</option>
  <option value="VISUALIZADOR">Visualizador</option>
</select>

<!-- Link discreto para acesso administrativo -->
<div class="text-center mt-3">
  <a href="/admin-login" class="text-muted small">
    <i class="fas fa-cog"></i> Admin
  </a>
</div>
```

**Login Admin (`template_auth_login_admin.html`):**

```html
<!-- Campo fixo -->
<input type="hidden" id="tipo_usuario" name="tipo_usuario" value="ADMIN" />

<!-- Visual diferenciado -->
<div class="card border-warning">
  <div class="card-header bg-warning text-dark">
    <i class="fas fa-shield-alt"></i> Acesso Administrativo
  </div>
  <!-- ... -->
</div>

<!-- Link de retorno -->
<div class="text-center mt-3">
  <a href="/login" class="text-muted small">
    <i class="fas fa-arrow-left"></i> Voltar ao login regular
  </a>
</div>
```

---

### 4. Validações de Login

**authController.py (login):**

```python
async def login(request: LoginRequest):
    # 1. Validar credenciais
    user = await get_user_by_credentials(request.usuario, request.tipo_usuario)

    # 2. Verificar status
    if user.status != "APROVADO":
        raise HTTPException(
            status_code=403,
            detail="Usuário não aprovado. Aguarde a aprovação do administrador.",
            headers={"X-Error-Code": "USUARIO_NAO_APROVADO"}
        )

    # 3. Verificar ativo
    if not user.ativo:
        raise HTTPException(
            status_code=403,
            detail="Usuário inativo. Entre em contato com o administrador.",
            headers={"X-Error-Code": "USUARIO_INATIVO"}
        )

    # 4. Verificar email verificado
    if not user.email_institucional_verificado:
        raise HTTPException(
            status_code=403,
            detail="Email institucional não verificado.",
            headers={"X-Error-Code": "EMAIL_NAO_VERIFICADO"}
        )

    # 5. Verificar senha
    if not verify_password(request.password, user.senha_hash):
        await incrementar_tentativas_login(user.id)
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    # 6. Gerar token JWT com tipo_usuario e nivel_acesso
    token = create_access_token(
        data={
            "id": str(user.id),
            "email": user.email,
            "nome": user.nome_completo,
            "tipo_usuario": user.tipo_usuario,
            "nivel_acesso": user.nivel_acesso
        }
    )

    return {
        "token": token,
        "user": {
            "id": str(user.id),
            "nome": user.nome_completo,
            "tipo_usuario": user.tipo_usuario,
            "nivel_acesso": user.nivel_acesso
        }
    }
```

---

## 🎯 ROTAS POR TIPO DE USUÁRIO

### **Rotas Públicas** (Sem autenticação)

- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/recuperar-senha` - Recuperação de senha
- `GET /api/v1/auth/verificar-email/:token` - Verificação de email
- `POST /api/v1/usuarios/solicitacao` - Criar solicitação

### **Rotas ADMIN Apenas**

- `DELETE /api/v1/usuarios/:id` - Excluir usuário
- `PUT /api/v1/usuarios/:id/nivel-acesso` - Alterar nível de acesso
- `GET /api/v1/admin/configuracoes` - Configurações do sistema
- `GET /api/v1/admin/logs` - Logs do sistema
- `POST /api/v1/admin/backup` - Backup do sistema

### **Rotas ADMIN + GESTOR**

- `GET /api/v1/usuarios/solicitacoes/pendentes` - Listar solicitações
- `PUT /api/v1/usuarios/solicitacoes/:id/aprovar` - Aprovar solicitação
- `PUT /api/v1/usuarios/solicitacoes/:id/rejeitar` - Rejeitar solicitação
- `PUT /api/v1/usuarios/:id/suspender` - Suspender usuário
- `PUT /api/v1/usuarios/:id/ativar` - Ativar usuário
- `GET /api/v1/usuarios` - Listar todos usuários
- `GET /api/v1/sessoes/ativas` - Sessões ativas

### **Rotas ADMIN + GESTOR + ANALISTA**

- `GET /api/v1/relatorios/usuarios` - Relatório de usuários
- `GET /api/v1/relatorios/acessos` - Relatório de acessos
- `GET /api/v1/estatisticas` - Estatísticas gerais
- `POST /api/v1/export/csv` - Exportar dados

### **Rotas Autenticadas (Todos)**

- `GET /api/v1/auth/me` - Dados do usuário logado
- `PUT /api/v1/auth/senha` - Alterar própria senha
- `POST /api/v1/auth/logout` - Logout
- `GET /api/v1/auth/sessoes` - Minhas sessões

---

## 🚀 CHECKLIST DE IMPLEMENTAÇÃO

### Banco de Dados

- [ ] Adicionar campo `tipo_usuario` com constraint
- [ ] Criar função `calcular_nivel_acesso()`
- [ ] Criar trigger para calcular nível automaticamente
- [ ] Atualizar migration 005 com campos de hierarquia
- [ ] Criar índices de performance

### Backend

- [ ] Criar `app/middleware/auth_middleware.py`
- [ ] Implementar `PermissionChecker`
- [ ] Criar instâncias de verificação (`verificar_admin`, etc.)
- [ ] Atualizar `service_auth.py` com validação de tipo
- [ ] Atualizar JWT para incluir `tipo_usuario` e `nivel_acesso`
- [ ] Aplicar middlewares em routers

### Frontend

- [ ] Criar `template_auth_login_regular.html`
- [ ] Criar `template_auth_login_admin.html`
- [ ] Criar `script_login_regular.js`
- [ ] Criar `script_login_admin.js`
- [ ] Criar `style_auth_login.css` com visuais diferenciados

### Routers

- [ ] `router_auth_login.py` - Login (ambos tipos)
- [ ] `router_admin_usuarios.py` - Gestão de usuários (ADMIN)
- [ ] `router_admin_sistema.py` - Configurações (ADMIN)
- [ ] Aplicar decoradores de permissão em todas rotas

### Testes

- [ ] Testar login de cada tipo de usuário
- [ ] Testar middleware de permissões
- [ ] Testar acesso negado (403)
- [ ] Testar separação ADMIN vs regular

---

## 📊 EXEMPLO DE FLUXO COMPLETO

### Cenário: GESTOR aprovando solicitação

```
1. GESTOR faz login em /login.html
   ├── Seleciona "Gestor" no dropdown
   ├── Envia credenciais
   └── Recebe token JWT com:
       {
         "id": "uuid",
         "tipo_usuario": "GESTOR",
         "nivel_acesso": 4
       }

2. GESTOR acessa painel de solicitações pendentes
   ├── GET /api/v1/usuarios/solicitacoes/pendentes
   ├── Middleware verifica_admin_gestor
   ├── tipo_usuario = "GESTOR" ✓ (permitido)
   └── Retorna lista de solicitações

3. GESTOR aprova uma solicitação
   ├── PUT /api/v1/usuarios/solicitacoes/:id/aprovar
   ├── Middleware verifica_admin_gestor
   ├── tipo_usuario = "GESTOR" ✓ (permitido)
   ├── Backend atualiza: status=APROVADO, ativo=true
   ├── Email de aprovação enviado
   └── Retorna sucesso

4. GESTOR tenta alterar nivel_acesso (NÃO permitido)
   ├── PUT /api/v1/usuarios/:id/nivel-acesso
   ├── Middleware verifica_admin
   ├── tipo_usuario = "GESTOR" ✗ (esperado: ADMIN)
   └── Retorna 403 Forbidden
```

---

## 🔐 SEGURANÇA E BOAS PRÁTICAS

1. **Princípio do Menor Privilégio:** Usuários têm apenas as permissões necessárias
2. **Separação de Login:** ADMIN em página separada, menos exposta
3. **Validação Dupla:** Frontend (UX) + Backend (segurança)
4. **Auditoria:** Log de todas operações sensíveis
5. **Token JWT:** Inclui tipo e nível para verificação rápida
6. **Middleware Reutilizável:** DRY (Don't Repeat Yourself)
7. **Mensagens Claras:** Usuário sabe por que foi negado
8. **Link Discreto:** Acesso ADMIN não é óbvio para usuários comuns

---

**Documento atualizado em:** 03/11/2025  
**Versão:** 1.0  
**Status:** Pronto para implementação no SIGMA-PRINCIPAL
