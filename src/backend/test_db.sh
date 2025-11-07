#!/bin/bash

# Instala as dependências
pip install psycopg2-binary python-dotenv

# Executa o teste de conexão
python /app/test_connection.py
