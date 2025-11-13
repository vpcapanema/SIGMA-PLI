# 🐳 Docker - Teste Local

## 🚀 Início Rápido

### 1. Build e Start (Backend + PostgreSQL)

```bash
# Build das imagens
docker-compose build

# Iniciar serviços (backend + postgres)
docker-compose up -d

# Ver logs em tempo real
docker-compose logs -f backend
```

**Aguarde ~30 segundos** para os serviços iniciarem.

### 2. Acessar a Aplicação

- **Frontend**: http://localhost:8010
- **API Docs**: http://localhost:8010/api/docs
- **Health Check**: http://localhost:8010/health

### 3. PostgreSQL

```bash
# Conectar no PostgreSQL
docker-compose exec postgres psql -U sigma_user -d sigma_pli_db

# Verificar tabelas
\dt

# Sair
\q
```

---

## 🔧 Comandos Úteis

### Gerenciamento de Containers

```bash
# Parar todos os serviços
docker-compose down

# Parar e remover volumes (LIMPA BANCO!)
docker-compose down -v

# Reiniciar apenas o backend
docker-compose restart backend

# Ver logs de um serviço específico
docker-compose logs -f postgres
docker-compose logs -f backend

# Ver status dos containers
docker-compose ps
```

### Build e Rebuild

```bash
# Rebuild apenas o backend (após mudanças no código)
docker-compose build backend

# Rebuild forçado (ignora cache)
docker-compose build --no-cache backend

# Rebuild e restart
docker-compose up -d --build backend
```

### Executar Comandos Dentro dos Containers

```bash
# Shell no backend
docker-compose exec backend bash

# Python no backend
docker-compose exec backend python

# Ver variáveis de ambiente
docker-compose exec backend env | grep POSTGRES
```

---

## 🧪 Testes e Debugging

### Testar Conexão com PostgreSQL

```bash
# Do host
docker-compose exec postgres pg_isready -U sigma_user

# Health check do backend
curl http://localhost:8010/health
```

### Ver Logs Detalhados

```bash
# Todos os serviços
docker-compose logs --tail=100 -f

# Apenas erros
docker-compose logs --tail=50 backend | grep ERROR
```

### Entrar no Container Backend

```bash
docker-compose exec backend bash

# Dentro do container, você pode:
python -c "from app.config import settings; print(settings.database_url)"
```

---

## 🎯 Incluir Neo4j (Opcional)

Por padrão, Neo4j NÃO inicia. Para incluí-lo:

```bash
# Start com Neo4j
docker-compose --profile neo4j up -d

# Acessar Neo4j Browser
# http://localhost:7474
# User: neo4j
# Pass: sigma123456
```

Para usar Neo4j permanentemente, edite `docker-compose.yml`:

```yaml
backend:
  environment:
    - ENABLE_NEO4J=true # Altere para true
```

---

## 🔄 Hot Reload (Desenvolvimento)

O `docker-compose.yml` já está configurado com volumes para hot reload:

```yaml
volumes:
  - ./app:/app/app
  - ./templates:/app/templates
  - ./static:/app/static
```

**Mudanças no código são refletidas automaticamente!** 🎉

Se não funcionar, adicione `--reload` no Dockerfile:

```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

---

## 🧹 Limpeza Completa

```bash
# Parar tudo e remover volumes
docker-compose down -v

# Remover imagens não usadas
docker image prune -a

# Remover tudo (containers, volumes, networks)
docker system prune -a --volumes
```

---

## 📊 Estrutura de Portas

| Serviço       | Porta Host | Porta Container |
| ------------- | ---------- | --------------- |
| Backend       | 8010       | 8000            |
| PostgreSQL    | 5432       | 5432            |
| Neo4j Browser | 7474       | 7474            |
| Neo4j Bolt    | 7687       | 7687            |

---

## 🐛 Troubleshooting

### Backend não inicia

**Sintoma**: Container para logo após iniciar

**Solução**:

```bash
# Ver logs
docker-compose logs backend

# Verificar se a porta 8010 está livre
netstat -ano | findstr :8010  # Windows
lsof -i :8010  # Linux/Mac

# Se ocupada, mude em docker-compose.yml:
ports:
  - "8011:8000"  # Usar porta 8011
```

### Erro de conexão com PostgreSQL

**Sintoma**: `could not connect to server`

**Solução**:

```bash
# Verificar se postgres está rodando
docker-compose ps

# Recriar o serviço
docker-compose down
docker-compose up -d postgres
docker-compose up -d backend
```

### Mudanças no código não aparecem

**Sintoma**: Alterações não refletem na aplicação

**Solução**:

```bash
# Rebuild
docker-compose build backend
docker-compose up -d backend

# Ou force recreate
docker-compose up -d --force-recreate backend
```

### Volumes ocupando muito espaço

```bash
# Ver tamanho dos volumes
docker system df -v

# Limpar volumes não usados
docker volume prune
```

---

## 🎯 Simulando Ambiente Render

Para testar como vai funcionar no Render:

```bash
# 1. Desabilitar hot reload (edite Dockerfile)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# 2. Ativar Keep-Alive (edite docker-compose.yml)
environment:
  - ENABLE_KEEPALIVE=true
  - KEEPALIVE_URL=http://localhost:8010

# 3. Rebuild
docker-compose build backend
docker-compose up -d backend

# 4. Monitorar keep-alive
docker-compose logs -f backend | grep "Keep-Alive"
```

---

## 📚 Referências

- [Docker Compose Docs](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [Neo4j Docker Image](https://hub.docker.com/_/neo4j)
- [FastAPI Docker Guide](https://fastapi.tiangolo.com/deployment/docker/)

---

## 🆘 Suporte

Problemas? Abra uma issue:
https://github.com/vpcapanema/SIGMA-PLI/issues
