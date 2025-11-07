import os
import psycopg2

def list_tables_and_columns(schemas_to_check=None):
    config = {
        'host': os.getenv('POSTGRES_HOST'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'database': os.getenv('POSTGRES_DB'),
        'user': os.getenv('POSTGRES_USER'),
        'password': os.getenv('POSTGRES_PASSWORD'),
        'sslmode': os.getenv('POSTGRES_SSLMODE', 'require')
    }

    conn = psycopg2.connect(**config)
    cur = conn.cursor()

    # Find schemas if none provided
    if not schemas_to_check:
        cur.execute("""
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name NOT LIKE 'pg_%' AND schema_name <> 'information_schema'
            ORDER BY schema_name;
        """)
        schemas = [row[0] for row in cur.fetchall()]
    else:
        schemas = schemas_to_check

    print("Schemas to inspect:")
    for s in schemas:
        print(f"- {s}")

    for schema in schemas:
        print(f"\n=== Schema: {schema} ===")
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = %s AND table_type = 'BASE TABLE'
            ORDER BY table_name;
        """, (schema,))
        tables = [r[0] for r in cur.fetchall()]
        if not tables:
            print("(no tables)")
            continue
        for table in tables:
            print(f"\n-- Table: {schema}.{table}")
            cur.execute("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
                ORDER BY ordinal_position;
            """, (schema, table))
            cols = cur.fetchall()
            for col in cols:
                print(f"  - {col[0]}: {col[1]} ({'NULL' if col[2]=='YES' else 'NOT NULL'})")

    cur.close()
    conn.close()


if __name__ == '__main__':
    # Prefer explicit list for quicker output
    default_schemas = ['dicionario', 'public', 'dados_brasil', 'estatisticas_brasil']
    list_tables_and_columns(default_schemas)
