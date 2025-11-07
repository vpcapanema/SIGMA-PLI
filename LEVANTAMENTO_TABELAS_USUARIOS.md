# 📊 LEVANTAMENTO DE TABELAS - Schema `usuarios`

**Data**: 3 de novembro de 2025  
**Objetivo**: Análise para remoção de `usuarios.usuario` e manutenção de `usuarios.conta_usuario`

---

## 🔴 TABELAS RELACIONADAS A `usuarios.usuario` (PARA REMOÇÃO)

### **Tabela Principal:**

- `usuarios.usuario` (0 registros) ✅ VAZIA

### **Tabelas Dependentes (Foreign Keys):**

1. `usuarios.usuario_papel` (0 registros) ✅ VAZIA

   - FK: `usuario_id` → `usuarios.usuario(id)` ON DELETE CASCADE

2. `usuarios.auditoria_login` (0 registros) ✅ VAZIA

   - FK: `usuario_id` → `usuarios.usuario(id)`

3. `usuarios.evento` (0 registros) ✅ VAZIA

   - FK: `usuario_id` → `usuarios.usuario(id)` ON DELETE CASCADE

4. `usuarios.homeoffice` (0 registros) ✅ VAZIA

   - FK: `usuario_id` → `usuarios.usuario(id)` ON DELETE CASCADE

5. `usuarios.tarefa` (0 registros) ✅ VAZIA
   - FK: `usuario_id` → `usuarios.usuario(id)` ON DELETE CASCADE

### **Triggers em `usuarios.usuario`:**

- `trigger_auditoria_usuario`
- `trigger_update_usuario_updated_at`

### **✅ STATUS: SEGURO PARA REMOÇÃO**

- Todas as tabelas estão **VAZIAS** (0 registros)
- Não há dados a preservar

---

## 🟢 TABELAS RELACIONADAS A `usuarios.conta_usuario` (MANTER)

### **Tabela Principal:**

- `usuarios.conta_usuario` (1 registro) ⚠️ **COM DADOS**

### **Tabelas Dependentes (Foreign Keys):**

1. `usuarios.sessao` (1 registro) ⚠️ **COM DADOS**

   - FK: `conta_usuario_id` → `usuarios.conta_usuario(id)` ON DELETE CASCADE

2. `usuarios.tentativa_login` (0 registros) ✅ VAZIA

   - FK: `conta_usuario_id` → `usuarios.conta_usuario(id)`

3. `usuarios.token_recuperacao` (0 registros) ✅ VAZIA
   - FK: `conta_usuario_id` → `usuarios.conta_usuario(id)` ON DELETE CASCADE

### **Triggers:**

- `trigger_auditoria_conta_usuario` (em `usuarios.conta_usuario`)
- `trigger_update_conta_usuario_updated_at` (em `usuarios.conta_usuario`)
- `trigger_auditoria_sessao` (em `usuarios.sessao`)

### **Relacionamento com `usuarios.pessoa`:**

- `usuarios.conta_usuario.pessoa_id` → FK para `usuarios.pessoa(id)` ON DELETE CASCADE

### **⚠️ STATUS: MANTER E PROTEGER**

- Tabela **EM USO** com 1 conta cadastrada
- Sistema de sessões **ATIVO** (1 sessão)
- Infraestrutura de autenticação **FUNCIONAL**

---

## 📋 PLANO DE REMOÇÃO

### **Ordem de Execução (CASCADE automático):**

```sql
-- PASSO 1: Remover tabelas dependentes (ordem inversa de criação)
DROP TABLE IF EXISTS usuarios.tarefa CASCADE;
DROP TABLE IF EXISTS usuarios.homeoffice CASCADE;
DROP TABLE IF EXISTS usuarios.evento CASCADE;
DROP TABLE IF EXISTS usuarios.auditoria_login CASCADE;
DROP TABLE IF EXISTS usuarios.usuario_papel CASCADE;

-- PASSO 2: Remover tabela principal
DROP TABLE IF EXISTS usuarios.usuario CASCADE;
```

### **Verificação Pós-Remoção:**

```sql
-- Verificar que apenas as tabelas corretas permanecem
SELECT tablename
FROM pg_tables
WHERE schemaname = 'usuarios'
ORDER BY tablename;

-- Resultado esperado:
-- conta_usuario
-- grupo
-- papel
-- pessoa
-- pessoa_grupo
-- sessao
-- tentativa_login
-- token_recuperacao
```

---

## ⚠️ OBSERVAÇÕES IMPORTANTES

1. **Nenhum dado será perdido**: Todas as tabelas a serem removidas estão vazias
2. **Sistema em produção**: `usuarios.conta_usuario` está ativa com 1 usuário
3. **Backup recomendado**: Sempre fazer dump antes de DROP em produção
4. **Triggers**: Serão removidos automaticamente com CASCADE
5. **Aplicação**: Verificar se há código referenciando `usuarios.usuario` antes de remover

---

## 🔍 VERIFICAÇÃO DE CÓDIGO

Antes de executar a remoção, verificar se há código Python/SQL que referencia:

- `usuarios.usuario`
- `usuarios.usuario_papel`
- `usuarios.auditoria_login`
- `usuarios.evento`
- `usuarios.homeoffice`
- `usuarios.tarefa`

**Comando para busca:**

```bash
grep -r "usuarios.usuario" app/
grep -r "usuario_papel" app/
grep -r "auditoria_login" app/
```
