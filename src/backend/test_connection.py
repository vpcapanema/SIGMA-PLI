import os
import psycopg2
import time

def test_connection():
    try:
        # Pega as configurações do ambiente
        config = {
            'host': os.getenv('POSTGRES_HOST'),
            'port': os.getenv('POSTGRES_PORT'),
            'database': os.getenv('POSTGRES_DB'),
            'user': os.getenv('POSTGRES_USER'),
            'password': os.getenv('POSTGRES_PASSWORD'),
            'sslmode': os.getenv('POSTGRES_SSLMODE', 'require')
        }
        
        print("Tentando conectar com as seguintes configurações:")
        for key, value in config.items():
            if key != 'password':
                print(f"{key}: {value}")
        
        # Tenta estabelecer a conexão
        conn = psycopg2.connect(**config)
        
        # Se chegou aqui, a conexão foi bem sucedida
        print("\n✅ Conexão estabelecida com sucesso!")
        
        # Testa uma query simples
        cur = conn.cursor()
        cur.execute("SELECT current_database(), current_user, version();")
        db, user, version = cur.fetchone()
        
        print(f"\nInformações do Banco:")
        print(f"Database: {db}")
        print(f"Usuário: {user}")
        print(f"Versão: {version}")
        
        # Lista os schemas
        cur.execute("""
            SELECT schema_name 
            FROM information_schema.schemata 
            WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_temp_1', 'pg_toast')
            ORDER BY schema_name;
        """)
        schemas = cur.fetchall()
        
        print("\nSchemas disponíveis:")
        for schema in schemas:
            print(f"- {schema[0]}")
        
        # Fecha a conexão
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Erro ao conectar: {str(e)}")

if __name__ == "__main__":
    test_connection()
