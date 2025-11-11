# 🚀 Deploy no Render - Guia Rápido

## Configuração Inicial

### 1. Criar Web Service

1. Acesse [render.com](https://render.com)
2. **New** → **Web Service**
3. Conecte seu repositório GitHub
4. Configure:
   - **Name**: `sigma-pli`
   - **Region**: `Oregon (US West)` ou mais próximo
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 2. Environment Variables

Adicione no **Render Dashboard** → **Environment**:

```bash
# PostgreSQL (fornecido pelo Render Database)
DATABASE_URL=postgresql://...  # Copie do Render Postgres

# Keep-Alive (IMPORTANTE!)
ENABLE_KEEPALIVE=true
KEEPALIVE_URL=https://sigma-pli.onrender.com  # Sua URL do Render
KEEPALIVE_INTERVAL_MINUTES=10

# JWT
JWT_SECRET_KEY=seu_secret_key_forte_aqui

# Aplicação
DEBUG=false
ENABLE_POSTGRES=true
ENABLE_NEO4J=false  # Até configurar Neo4j Aura
```

### 3. PostgreSQL Database

1. **New** → **PostgreSQL**
2. **Name**: `sigma-pli-db`
3. **Region**: Mesmo do Web Service
4. Copie a **Internal Database URL**
5. Cole em `DATABASE_URL` do Web Service

### 4. Deploy

- **Auto-deploy**: Habilitado (deploy automático a cada push)
- Aguarde o build (~5 minutos)
- Acesse: `https://sigma-pli.onrender.com`

---

## 🎯 Keep-Alive Configuration

### Por que é necessário?

Render suspende serviços gratuitos após **15 minutos de inatividade**. O Keep-Alive:

- ✅ Mantém o servidor sempre ativo
- ✅ Evita cold start (30-60s de espera)
- ✅ Garante resposta instantânea aos usuários

### Configuração

Já está configurado automaticamente! Basta definir as variáveis:

```bash
ENABLE_KEEPALIVE=true
KEEPALIVE_URL=https://sigma-pli.onrender.com  # SUA URL!
```

### Monitoramento

Verifique se está funcionando:

```bash
# 1. Acesse os logs do Render
# Deve aparecer:
🚀 Keep-Alive iniciado - ping a cada 10 minutos
✅ Keep-Alive ping #1 OK - 2025-11-11 14:20:00

# 2. Teste o endpoint de stats
curl https://sigma-pli.onrender.com/api/v1/keepalive/stats
```

---

## 📊 Health Checks

Render automaticamente usa `/health` para verificar se a aplicação está ativa.

```bash
curl https://sigma-pli.onrender.com/health

# Resposta esperada:
{
  "status": "healthy",
  "service": "SIGMA-PLI Backend",
  "version": "1.0.0"
}
```

---

## 🔍 Troubleshooting

### Aplicação não sobe

1. **Verifique os logs**: Render Dashboard → Logs
2. **Erro de dependências**: Verifique `requirements.txt`
3. **Porta incorreta**: Use `$PORT` (fornecido pelo Render)

### Keep-Alive não funciona

1. **Verifique variáveis**:
   - `ENABLE_KEEPALIVE=true`
   - `KEEPALIVE_URL` está correta (SUA URL do Render)
2. **Verifique logs**:

   ```
   🚀 Keep-Alive iniciado...  ← Deve aparecer
   ```

3. **Teste manualmente**:
   ```bash
   curl https://sua-url.onrender.com/health
   ```

### Aplicação ainda suspende

- **Reduza o intervalo**: `KEEPALIVE_INTERVAL_MINUTES=8`
- **Verifique timeout**: Render Free = 15min

---

## 💡 Dicas

### Performance

- Use **Region próxima**: Menor latência
- **Auto-deploy off**: Para controlar deploys manuais
- **Branch separado**: Use `production` em vez de `main`

### Custos

- **Free Tier**: 750 horas/mês (suficiente para 1 serviço 24/7)
- **Keep-Alive**: Zero custo adicional (requisições internas)
- **Database**: 90 dias gratuitos, depois $7/mês

### Segurança

- **Secrets**: Nunca commite chaves no código
- **Environment vars**: Tudo sensível vai no Render
- **HTTPS**: Automático com certificado SSL gratuito

---

## 🔗 Links Úteis

- [Render Dashboard](https://dashboard.render.com)
- [Render Docs](https://render.com/docs)
- [SIGMA-PLI GitHub](https://github.com/vpcapanema/SIGMA-PLI)
- [Keep-Alive Docs](./KEEPALIVE_RENDER.md)

---

## 📞 Suporte

Problemas? Abra uma issue:
https://github.com/vpcapanema/SIGMA-PLI/issues
