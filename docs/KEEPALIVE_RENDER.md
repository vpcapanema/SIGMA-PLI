# Keep-Alive Service - Render Deployment

## 📖 Visão Geral

O **Keep-Alive Service** mantém o backend SIGMA-PLI sempre ativo em plataformas de deploy como Render, evitando o "cold start" (inicialização fria) causado pela suspensão automática de serviços inativos.

### Problema

Plataformas como Render (plano gratuito) suspendem aplicações após **15 minutos de inatividade**. Isso causa:

- ⏰ **Cold Start**: 30-60 segundos para a primeira requisição
- 😞 **Má experiência do usuário**: Páginas lentas ao acessar pela primeira vez
- 🔄 **Reconexões de banco**: PostgreSQL e Neo4j precisam reconectar

### Solução

O Keep-Alive faz **auto-ping periódico** no próprio servidor, simulando atividade constante e evitando a suspensão.

---

## 🚀 Como Funciona

1. **Startup**: Serviço inicia junto com o FastAPI
2. **Loop Assíncrono**: A cada N minutos (padrão: 10), faz GET em `/health`
3. **Logging**: Registra cada ping com timestamp e estatísticas
4. **Shutdown**: Para graciosamente ao desligar a aplicação

```
[Startup] → [Wait 2min] → [Ping /health] → [Wait 10min] → [Ping /health] → ...
```

---

## ⚙️ Configuração

### 1. Variáveis de Ambiente

Adicione ao **Render Dashboard** → **Environment**:

```bash
# Ativar Keep-Alive
ENABLE_KEEPALIVE=true

# URL do próprio serviço (substitua pela sua URL do Render)
KEEPALIVE_URL=https://sigma-pli.onrender.com

# Intervalo entre pings (em minutos)
KEEPALIVE_INTERVAL_MINUTES=10
```

### 2. Local Development

No arquivo `.env` local, mantenha **desabilitado**:

```bash
ENABLE_KEEPALIVE=false
```

Isso evita auto-ping desnecessário durante desenvolvimento.

---

## 📊 Monitoramento

### Endpoint de Estatísticas

```bash
GET /api/v1/keepalive/stats
```

**Resposta**:

```json
{
  "status": "active",
  "stats": {
    "is_running": true,
    "base_url": "https://sigma-pli.onrender.com",
    "interval_minutes": 10,
    "ping_count": 42,
    "failed_pings": 0,
    "last_ping": "2025-11-11T14:30:00"
  }
}
```

### Logs do Render

Acesse **Render Dashboard** → **Logs** para ver:

```
🚀 Keep-Alive iniciado - ping a cada 10 minutos
🎯 Target URL: https://sigma-pli.onrender.com/health
✅ Keep-Alive ping #1 OK - 2025-11-11 14:20:00
✅ Keep-Alive ping #2 OK - 2025-11-11 14:30:00
```

---

## 🔧 Arquitetura

### Arquivo Principal: `app/services/service_keepalive.py`

```python
class KeepAliveService:
    def __init__(self, base_url: str, interval_minutes: int = 10):
        # Configuração inicial

    async def ping(self) -> bool:
        # Faz GET em /health

    async def _run_loop(self):
        # Loop assíncrono periódico

    def start(self):
        # Inicia em background

    async def stop(self):
        # Para graciosamente
```

### Integração no `main.py`

```python
@app.on_event("startup")
async def startup_event():
    if settings.enable_keepalive and settings.keepalive_url:
        keepalive = init_keepalive_service(
            base_url=settings.keepalive_url,
            interval_minutes=settings.keepalive_interval_minutes
        )
        keepalive.start()

@app.on_event("shutdown")
async def shutdown_event():
    keepalive = get_keepalive_service()
    if keepalive:
        await keepalive.stop()
```

---

## ⚡ Performance

### Impacto Mínimo

- **Memória**: ~1 MB adicional
- **CPU**: <0.1% (apenas durante ping)
- **Rede**: ~10 KB/request × 6 pings/hora = 60 KB/hora
- **Custo**: Zero (requisições internas não contam no limite do Render)

### Benefícios

- ✅ **Zero Cold Start**: Aplicação sempre pronta
- ✅ **Resposta instantânea**: <100ms para primeira requisição
- ✅ **Conexões persistentes**: Banco de dados sempre conectado
- ✅ **Melhor UX**: Usuários não esperam carregamento inicial

---

## 🎯 Intervalos Recomendados

| Plataforma   | Timeout     | Intervalo Recomendado |
| ------------ | ----------- | --------------------- |
| Render Free  | 15 min      | **10 minutos**        |
| Render Pro   | Sem timeout | Desabilitar           |
| Heroku Free  | 30 min      | 20 minutos            |
| Railway Free | 5 min       | **3 minutos**         |

**Regra geral**: Intervalo = 66% do timeout da plataforma

---

## 🐛 Troubleshooting

### Keep-Alive não está funcionando

1. **Verifique as variáveis**:

   ```bash
   echo $ENABLE_KEEPALIVE  # deve ser "true"
   echo $KEEPALIVE_URL     # deve estar preenchida
   ```

2. **Verifique os logs**:

   ```bash
   # Deve aparecer ao iniciar:
   🚀 Keep-Alive iniciado - ping a cada 10 minutos
   ```

3. **Teste o endpoint manualmente**:
   ```bash
   curl https://sigma-pli.onrender.com/health
   # Deve retornar: {"status": "healthy", ...}
   ```

### Muitos pings falhando

- **Causa**: URL incorreta ou servidor inacessível
- **Solução**: Corrija `KEEPALIVE_URL` no Render

### Aplicação ainda suspende

- **Causa**: Intervalo muito longo
- **Solução**: Reduza `KEEPALIVE_INTERVAL_MINUTES` para 5-8 minutos

---

## 🔒 Segurança

### Proteção Contra Abuso

O endpoint `/health` é:

- ✅ **Público** (sem autenticação necessária)
- ✅ **Leve** (não acessa banco de dados)
- ✅ **Rate-limited** internamente (1 req/min máximo)

### Alternativas Externas

Se preferir serviços externos:

1. **UptimeRobot** (free): https://uptimerobot.com
2. **Cron-job.org** (free): https://cron-job.org
3. **Better Uptime** (paid): https://betteruptime.com

Configure para fazer GET em `https://sigma-pli.onrender.com/health` a cada 10 minutos.

---

## 📚 Referências

- [Render Docs - Service Sleeping](https://render.com/docs/free#free-web-services)
- [FastAPI Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [HTTPX Async Client](https://www.python-httpx.org/async/)

---

## 🆘 Suporte

Problemas ou dúvidas? Abra uma issue no GitHub:
https://github.com/vpcapanema/SIGMA-PLI/issues
