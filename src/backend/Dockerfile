FROM python:3.11-slim

WORKDIR /app

# Instala as dependências necessárias
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copia os arquivos de requisitos
COPY requirements.txt .

# Instala as dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código da aplicação
COPY . .

# Script para testar a conexão com o banco
COPY test_connection.py .

# Torna o script de teste executável
RUN chmod +x test_connection.py

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
