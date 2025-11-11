# ⚡ CONFIGURAÇÃO RÁPIDA - RENDER

## 🎯 3 Passos para Manter Seu Backend Sempre Ativo

### 1️⃣ Acesse o Render Dashboard

👉 https://dashboard.render.com → Seu serviço → **Environment**

### 2️⃣ Adicione 3 Variáveis

Clique em **Add Environment Variable** e adicione:

```
Nome: ENABLE_KEEPALIVE
Valor: true
```

```
Nome: KEEPALIVE_URL
Valor: https://sigma-pli.onrender.com
       ↑ SUBSTITUA pela SUA URL do Render!
```

```
Nome: KEEPALIVE_INTERVAL_MINUTES
Valor: 10
```

### 3️⃣ Salve e Aguarde o Redeploy

- Clique em **Save Changes**
- Render fará redeploy automático (~2 minutos)
- Pronto! ✅

---

## 🔍 Como Verificar se Funcionou

### Opção 1: Logs do Render

Acesse **Logs** e procure por:

```
🚀 Keep-Alive iniciado - ping a cada 10 minutos
🎯 Target URL: https://sigma-pli.onrender.com/health
✅ Keep-Alive ping #1 OK - 2025-11-11 14:20:00
✅ Keep-Alive ping #2 OK - 2025-11-11 14:30:00
```

### Opção 2: Endpoint de Estatísticas

Abra no navegador:

```
https://sigma-pli.onrender.com/api/v1/keepalive/stats
```

Deve retornar algo como:

```json
{
  "status": "active",
  "stats": {
    "is_running": true,
    "ping_count": 5,
    "failed_pings": 0,
    "last_ping": "2025-11-11T14:30:00"
  }
}
```

---

## ✅ Resultado

Seu backend agora:

- ✅ **NUNCA** suspende
- ✅ **SEMPRE** responde instantaneamente
- ✅ **ZERO** cold start (aquela espera de 30s)
- ✅ Conexões de banco sempre ativas

---

## ❓ Problemas?

### Não vejo mensagens de Keep-Alive nos logs

**Causas possíveis:**

1. `ENABLE_KEEPALIVE` não está como `true` (letra minúscula!)
2. `KEEPALIVE_URL` está vazia ou incorreta
3. Redeploy ainda não terminou

**Solução:**

- Verifique as variáveis novamente
- Force um redeploy: **Manual Deploy** → **Deploy latest commit**

### Aplicação ainda suspende depois de 15 minutos

**Causa**: Intervalo muito longo

**Solução**: Reduza o intervalo:

```
KEEPALIVE_INTERVAL_MINUTES=8
```

---

## 💰 Custo Adicional?

**ZERO!** 🎉

O Keep-Alive:

- Faz requisições internas (não conta no limite do Render)
- Usa ~60 KB/hora de tráfego
- Não aumenta custo do plano gratuito

---

## 📚 Documentação Completa

Para entender como funciona por baixo dos panos:

- `docs/KEEPALIVE_RENDER.md` - Documentação técnica
- `docs/RENDER_DEPLOY.md` - Guia completo de deploy

---

## 🆘 Ainda com Dúvidas?

Abra uma issue no GitHub:
👉 https://github.com/vpcapanema/SIGMA-PLI/issues

Ou me chame no Discord/Slack! 💬
