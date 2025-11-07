import os
import psycopg2
from collections import defaultdict


EXPECTED_TABLES = [
    'arquivo', 'produtor', 'perfil', 'extensao', 'versao_arquivo',
    'workflow_aprovacao', 'status_publicacao_geoserver', 'auditoria_evento'
]

PROFILES = [
    'documentos_texto', 'midia', 'tabular', 'geoespacial_vetor',
    'geoespacial_raster', 'nuvem_pontos', 'desenho_2d3d', 'database',
    'geodatabase', 'pacote'
]

EXPECTED_STRUCTURES = [f"estrutura__{p}" for p in PROFILES]
EXPECTED_CONTENTS = [f"conteudo__{p}" for p in PROFILES]


def get_columns(cur, schema, table):
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position;
    """, (schema, table))
    return cur.fetchall()


def table_exists(cur, schema, table):
    cur.execute("""
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = %s AND table_name = %s AND table_type='BASE TABLE'
    """, (schema, table))
    return cur.fetchone() is not None


def pk_is_uuid(cur, schema, table):
    try:
        cur.execute("""
        SELECT a.attname, format_type(a.atttypid, a.atttypmod) as type
        FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = %s::regclass AND i.indisprimary;
        """, (f"{schema}.{table}",))
        rows = cur.fetchall()
        if not rows:
            return False, []
        cols = [r[0] for r in rows]
        types = [r[1] for r in rows]
        is_uuid = any('uuid' in t for t in types)
        return is_uuid, list(zip(cols, types))
    except Exception:
        # Fallback: try a simpler method
        try:
            cur.execute("""
            SELECT a.attname, t.typname
            FROM pg_attribute a
            JOIN pg_type t ON a.atttypid = t.oid
            JOIN pg_class c ON a.attrelid = c.oid
            JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE c.relname = %s AND n.nspname = %s AND a.attnum > 0 AND NOT a.attisdropped
            AND a.attname = (SELECT pg_attribute.attname FROM pg_index JOIN pg_attribute ON pg_attribute.attrelid = pg_index.indrelid AND pg_attribute.attnum = ANY(pg_index.indkey) WHERE pg_index.indrelid = c.oid AND pg_index.indisprimary LIMIT 1)
            """, (table, schema))
            rows = cur.fetchall()
            if not rows:
                return False, []
            is_uuid = any('uuid' in r[1] for r in rows)
            return is_uuid, rows
        except Exception:
            return False, []


def compare():
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

    schema = 'dicionario'
    public = 'public'

    report = defaultdict(dict)

    # Check expected fixed tables
    for t in EXPECTED_TABLES:
        exists = table_exists(cur, schema, t)
        report[schema][t] = {'exists': exists}
        if exists:
            cols = get_columns(cur, schema, t)
            report[schema][t]['columns'] = cols
            is_uuid_pk, pk_cols = pk_is_uuid(cur, schema, t)
            report[schema][t]['pk_uuid'] = is_uuid_pk
            report[schema][t]['pk_cols'] = pk_cols

    # Check structure and content tables per profile
    for t in EXPECTED_STRUCTURES + EXPECTED_CONTENTS:
        exists = table_exists(cur, schema, t)
        report[schema][t] = {'exists': exists}
        if exists:
            cols = get_columns(cur, schema, t)
            report[schema][t]['columns'] = cols
            # quick checks
            col_names = [c[0] for c in cols]
            if t.startswith('estrutura__'):
                report[schema][t]['has_produtor_id'] = 'produtor_id' in col_names
                report[schema][t]['has_id_uuid'] = any('id'==c[0] and 'uuid' in c[1] for c in cols)
            if t.startswith('conteudo__'):
                report[schema][t]['has_estrutura_id'] = 'estrutura_id' in col_names

    # Check public schema basics (spatial_ref_sys expected by PostGIS)
    report[public] = {}
    if table_exists(cur, public, 'spatial_ref_sys'):
        cols = get_columns(cur, public, 'spatial_ref_sys')
        report[public]['spatial_ref_sys'] = {'exists': True, 'columns': cols}
    else:
        report[public]['spatial_ref_sys'] = {'exists': False}

    # Additional checks for arquivo relationships
    if report[schema].get('arquivo', {}).get('exists'):
        col_names = [c[0] for c in report[schema]['arquivo']['columns']]
        report[schema]['arquivo']['has_nome_arquivo'] = 'nome_arquivo' in col_names
        report[schema]['arquivo']['has_extensao'] = 'extensao' in col_names

    cur.close()
    conn.close()

    # Print human-readable report
    print("\n=== Comparação de Esquema (apenas 'dicionario' e 'public') ===\n")
    for sch in [schema, public]:
        print(f"Schema: {sch}")
        for tbl, info in sorted(report[sch].items()):
            if not info.get('exists'):
                print(f"  - MISSING: {tbl}")
                continue
            print(f"  - OK: {tbl}")
            cols = info.get('columns', [])
            print(f"    columns: {len(cols)}")
            # show a few important checks
            if tbl == 'arquivo':
                print(f"    has nome_arquivo: {info.get('has_nome_arquivo', False)}")
                print(f"    has extensao: {info.get('has_extensao', False)}")
                print(f"    pk uuid: {info.get('pk_uuid', False)}")
            if tbl.startswith('estrutura__'):
                print(f"    has produtor_id: {info.get('has_produtor_id', False)}")
                print(f"    id uuid: {info.get('has_id_uuid', False)}")
            if tbl.startswith('conteudo__'):
                print(f"    has estrutura_id: {info.get('has_estrutura_id', False)}")

    # Summary
    missing = []
    for t in EXPECTED_TABLES + EXPECTED_STRUCTURES + EXPECTED_CONTENTS:
        if not report['dicionario'].get(t, {}).get('exists'):
            missing.append(t)

    print("\nResumo:")
    if missing:
        print(f"  Tabelas esperadas ausentes em 'dicionario': {len(missing)}")
        for m in missing:
            print(f"    - {m}")
    else:
        print("  Todas as tabelas esperadas estão presentes em 'dicionario'.")


if __name__ == '__main__':
    try:
        compare()
    except Exception as e:
        import traceback
        print("Erro durante a comparação:\n")
        traceback.print_exc()
        raise
import os
import psycopg2
from collections import defaultdict


EXPECTED_TABLES = [
    'arquivo', 'produtor', 'perfil', 'extensao', 'versao_arquivo',
    'workflow_aprovacao', 'status_publicacao_geoserver', 'auditoria_evento'
]

PROFILES = [
    'documentos_texto', 'midia', 'tabular', 'geoespacial_vetor',
    'geoespacial_raster', 'nuvem_pontos', 'desenho_2d3d', 'database',
    'geodatabase', 'pacote'
]

EXPECTED_STRUCTURES = [f"estrutura__{p}" for p in PROFILES]
EXPECTED_CONTENTS = [f"conteudo__{p}" for p in PROFILES]


def get_columns(cur, schema, table):
    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position;
    """, (schema, table))
    return cur.fetchall()


def table_exists(cur, schema, table):
    cur.execute("""
        SELECT 1 FROM information_schema.tables
        WHERE table_schema = %s AND table_name = %s AND table_type='BASE TABLE'
    """, (schema, table))
    return cur.fetchone() is not None


def pk_is_uuid(cur, schema, table):
    try:
        cur.execute("""
        SELECT a.attname, format_type(a.atttypid, a.atttypmod) as type
        FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = %s::regclass AND i.indisprimary;
        """, (f"{schema}.{table}",))
        rows = cur.fetchall()
        if not rows:
            return False, []
        cols = [r[0] for r in rows]
        types = [r[1] for r in rows]
        is_uuid = any('uuid' in t for t in types)
        return is_uuid, list(zip(cols, types))
    except Exception:
        # Fallback: try a simpler method
        try:
            cur.execute("""
            SELECT a.attname, t.typname
            FROM pg_attribute a
            JOIN pg_type t ON a.atttypid = t.oid
            JOIN pg_class c ON a.attrelid = c.oid
            JOIN pg_namespace n ON c.relnamespace = n.oid
            WHERE c.relname = %s AND n.nspname = %s AND a.attnum > 0 AND NOT a.attisdropped
            AND a.attname = (SELECT pg_attribute.attname FROM pg_index JOIN pg_attribute ON pg_attribute.attrelid = pg_index.indrelid AND pg_attribute.attnum = ANY(pg_index.indkey) WHERE pg_index.indrelid = c.oid AND pg_index.indisprimary LIMIT 1)
            """, (table, schema))
            rows = cur.fetchall()
            if not rows:
                return False, []
            is_uuid = any('uuid' in r[1] for r in rows)
            return is_uuid, rows
        except Exception:
            return False, []


def compare():
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

    schema = 'dicionario'
    public = 'public'

    report = defaultdict(dict)

    # Check expected fixed tables
    for t in EXPECTED_TABLES:
        exists = table_exists(cur, schema, t)
        report[schema][t] = {'exists': exists}
        if exists:
            cols = get_columns(cur, schema, t)
            report[schema][t]['columns'] = cols
            is_uuid_pk, pk_cols = pk_is_uuid(cur, schema, t)
            report[schema][t]['pk_uuid'] = is_uuid_pk
            report[schema][t]['pk_cols'] = pk_cols

    # Check structure and content tables per profile
    for t in EXPECTED_STRUCTURES + EXPECTED_CONTENTS:
        exists = table_exists(cur, schema, t)
        report[schema][t] = {'exists': exists}
        if exists:
            cols = get_columns(cur, schema, t)
            report[schema][t]['columns'] = cols
            # quick checks
            col_names = [c[0] for c in cols]
            if t.startswith('estrutura__'):
                report[schema][t]['has_produtor_id'] = 'produtor_id' in col_names
                report[schema][t]['has_id_uuid'] = any('id'==c[0] and 'uuid' in c[1] for c in cols)
            if t.startswith('conteudo__'):
                report[schema][t]['has_estrutura_id'] = 'estrutura_id' in col_names

    # Check public schema basics (spatial_ref_sys expected by PostGIS)
    report[public] = {}
    if table_exists(cur, public, 'spatial_ref_sys'):
        cols = get_columns(cur, public, 'spatial_ref_sys')
        report[public]['spatial_ref_sys'] = {'exists': True, 'columns': cols}
    else:
        report[public]['spatial_ref_sys'] = {'exists': False}

    # Additional checks for arquivo relationships
    if report[schema].get('arquivo', {}).get('exists'):
        col_names = [c[0] for c in report[schema]['arquivo']['columns']]
        report[schema]['arquivo']['has_nome_arquivo'] = 'nome_arquivo' in col_names
        report[schema]['arquivo']['has_extensao'] = 'extensao' in col_names

    cur.close()
    conn.close()

    # Print human-readable report
    print("\n=== Comparação de Esquema (apenas 'dicionario' e 'public') ===\n")
    for sch in [schema, public]:
        print(f"Schema: {sch}")
        for tbl, info in sorted(report[sch].items()):
            if not info.get('exists'):
                print(f"  - MISSING: {tbl}")
                continue
            print(f"  - OK: {tbl}")
            cols = info.get('columns', [])
            print(f"    columns: {len(cols)}")
            # show a few important checks
            if tbl == 'arquivo':
                print(f"    has nome_arquivo: {info.get('has_nome_arquivo', False)}")
                print(f"    has extensao: {info.get('has_extensao', False)}")
                print(f"    pk uuid: {info.get('pk_uuid', False)}")
            if tbl.startswith('estrutura__'):
                print(f"    has produtor_id: {info.get('has_produtor_id', False)}")
                print(f"    id uuid: {info.get('has_id_uuid', False)}")
            if tbl.startswith('conteudo__'):
                print(f"    has estrutura_id: {info.get('has_estrutura_id', False)}")

    # Summary
    missing = []
    for t in EXPECTED_TABLES + EXPECTED_STRUCTURES + EXPECTED_CONTENTS:
        if not report['dicionario'].get(t, {}).get('exists'):
            missing.append(t)

    print("\nResumo:")
    if missing:
        print(f"  Tabelas esperadas ausentes em 'dicionario': {len(missing)}")
        for m in missing:
            print(f"    - {m}")
    else:
        print("  Todas as tabelas esperadas estão presentes em 'dicionario'.")


if __name__ == '__main__':
    try:
        compare()
    except Exception as e:
        import traceback
        print("Erro durante a comparação:\n")
        traceback.print_exc()
        raise
