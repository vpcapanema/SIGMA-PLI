import os
import json
import psycopg2
from collections import defaultdict


def fetch_schema_details(cur, schema):
    details = {}
    # tables
    cur.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s AND table_type='BASE TABLE'
        ORDER BY table_name;
    """, (schema,))
    tables = [r[0] for r in cur.fetchall()]

    for table in tables:
        tinfo = {}
        # columns
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position;
        """, (schema, table))
        tinfo['columns'] = [dict(column_name=r[0], data_type=r[1], is_nullable=r[2], default=r[3]) for r in cur.fetchall()]

        # primary keys
        cur.execute("""
            SELECT a.attname
            FROM pg_index i
            JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
            WHERE i.indrelid = %s::regclass AND i.indisprimary;
        """, (f"{schema}.{table}",))
        pk = [r[0] for r in cur.fetchall()]
        tinfo['primary_key'] = pk

        # foreign keys
        cur.execute("""
            SELECT
              kcu.column_name, ccu.table_schema AS foreign_table_schema,
              ccu.table_name AS foreign_table_name, ccu.column_name AS foreign_column_name
            FROM information_schema.key_column_usage kcu
            JOIN information_schema.constraint_column_usage ccu
              ON kcu.constraint_name = ccu.constraint_name
            JOIN information_schema.table_constraints tc
              ON kcu.constraint_name = tc.constraint_name AND kcu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' AND kcu.table_schema = %s AND kcu.table_name = %s;
        """, (schema, table))
        fks = [{'column': r[0], 'ref_schema': r[1], 'ref_table': r[2], 'ref_column': r[3]} for r in cur.fetchall()]
        tinfo['foreign_keys'] = fks

        # indexes
        cur.execute("""
            SELECT indexname, indexdef
            FROM pg_indexes
            WHERE schemaname = %s AND tablename = %s;
        """, (schema, table))
        idxs = [{'name': r[0], 'def': r[1]} for r in cur.fetchall()]
        tinfo['indexes'] = idxs

        details[table] = tinfo

    return details


def main():
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

    report = {'dicionario': fetch_schema_details(cur, 'dicionario'), 'public': fetch_schema_details(cur, 'public')}

    # ensure reports dir
    out_dir = os.path.join(os.getcwd(), 'reports')
    os.makedirs(out_dir, exist_ok=True)

    json_path = os.path.join(out_dir, 'schema_report.json')
    txt_path = os.path.join(out_dir, 'schema_report.txt')

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    with open(txt_path, 'w', encoding='utf-8') as f:
        for sch, tables in report.items():
            f.write(f"Schema: {sch}\n")
            for tbl, info in tables.items():
                f.write(f"  Table: {tbl}\n")
                f.write(f"    Columns ({len(info['columns'])}):\n")
                for c in info['columns']:
                    f.write(f"      - {c['column_name']}: {c['data_type']} {c['is_nullable']} default={c['default']}\n")
                f.write(f"    PK: {info['primary_key']}\n")
                f.write(f"    FKs: {info['foreign_keys']}\n")
                f.write(f"    Indexes: {len(info['indexes'])}\n")
            f.write('\n')

    cur.close()
    conn.close()

    print(f"Relatórios gerados: {json_path} and {txt_path}")


if __name__ == '__main__':
    main()
