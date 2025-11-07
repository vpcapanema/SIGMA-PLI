# 🚀 COMO INICIAR A APLICAÇÃO SIGMA-PLI

## ⚠️ REGRA OBRIGATÓRIA

**SEMPRE** inicie a aplicação usando a tarefa configurada do VS Code:

### 🎯 Método CORRETO (escolha um):

1. **Atalho de teclado** (MAIS RÁPIDO):

   ```
   Ctrl + Shift + B
   ```

2. **Menu de tarefas**:
   - Pressione `Ctrl + Shift + P`
   - Digite: `Tasks: Run Task`
   - Selecione: `▶️ INICIAR APLICAÇÃO COMPLETA`

---

## ✅ O que a tarefa faz automaticamente:

1. 🔴 **Mata processos na porta 8010** (evita conflitos)
2. 🟢 **Inicia o FastAPI** (servidor backend)
3. 🔵 **Verifica PostgreSQL** (conectividade)
4. 🟡 **Verifica Neo4j** (conectividade)
5. 🌐 **Abre o navegador** em http://127.0.0.1:8010/

---

## ❌ NÃO FAÇA ISSO:

```bash
# ❌ ERRADO - Não execute manualmente:
python -m uvicorn app.main:app --reload
uvicorn app.main:app --host 127.0.0.1 --port 8010
python app/main.py

# ❌ Também não execute no terminal integrado sem a tarefa
```

---

## 📝 Por que usar a tarefa?

- ✅ Garante que a porta 8010 está livre
- ✅ Verifica conexões com bancos de dados
- ✅ Abre o navegador automaticamente
- ✅ Terminal dedicado (não interfere em outros comandos)
- ✅ Configuração centralizada e padronizada

---

## 🛑 Para parar a aplicação:

1. Vá até o terminal `Executar FastAPI (SIGMA-PRINCIPAL)`
2. Pressione `Ctrl + C`
3. Ou feche o terminal

---

## 🔄 Para reiniciar:

Pressione novamente `Ctrl + Shift + B`

A tarefa vai automaticamente:

- Matar processos antigos
- Iniciar uma nova instância
- Verificar tudo novamente

---

## 📚 Documentação Adicional

- **Arquitetura**: Veja `ARQUITETURA_AUTENTICACAO.md`
- **Sistema de Usuários**: Veja `SISTEMA_USUARIOS_EXPLICADO.md`
- **Migrations**: Pasta `migrations/`
- **Testes**: Execute `pytest tests/`

---

**Lembre-se**: `Ctrl + Shift + B` é seu melhor amigo! 🚀
