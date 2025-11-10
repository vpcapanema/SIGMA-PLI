# Dockerfile para testar build do SIGMA-PLI
FROM python:3.13-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY app ./app
COPY templates ./templates
COPY static ./static

# Expor porta
EXPOSE 8000

# Comando para rodar
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
