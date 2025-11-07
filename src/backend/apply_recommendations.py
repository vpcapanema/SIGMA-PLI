import os
import re
import sys
from datetime import datetime
import psycopg2
from psycopg2 import sql

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RECOMMENDATIONS_PATH = os.path.join(BASE, 'reports', 'schema_recommendations.sql')
ROLLBACK_PATH = os.path.join(BASE, 'reports', 'rollback_recommendations.sql')
LOG_PATH = os.path.join(BASE, 'reports', 'recommendations_applied.log')
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.py')

def load_db_config():
    cfg = {}
    spec = {}
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location('cfg', CONFIG_PATH)
        cfg_mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cfg_mod)
        cfg = getattr(cfg_mod, 'DB_CONFIG', None)
        if not cfg:
            # try DATABASE_URL
            url = getattr(cfg_mod, 'DATABASE_URL', None)
            if url:
                # crude parse
                m = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(\w+)', url)
                if m:
                    cfg = dict(user=m.group(1), password=m.group(2), host=m.group(3), port=int(m.group(4)), database=m.group(5))
    except Exception as e:
        print('Erro carregando config:', e)
    return cfg


def parse_recommendations(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    # split by semicolon or newline if no semicolon
    statements = [s.strip() for s in content.split(';') if s.strip()]
    return statements


def generate_rollback(statements):
    drops = []
    for s in statements:
        s_clean = s.strip()
        # handle CREATE INDEX IF NOT EXISTS ... ON schema.table USING gin (col)
        m = re.match(r'CREATE\s+INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?(\S+)\s+ON\s+([\w\.\"]+)\s+USING\s+\w+\s*\(', s_clean, re.IGNORECASE)
        if m:
            idx = m.group(1)
            drops.append(f'DROP INDEX IF EXISTS {idx};')
            continue
        # handle ALTER TABLE ADD CONSTRAINT ... FOREIGN KEY
        m2 = re.match(r'ALTER\s+TABLE\s+([\w\.\"]+)\s+ADD\s+CONSTRAINT\s+(\S+)\s+FOREIGN\s+KEY', s_clean, re.IGNORECASE)
        if m2:
            constraint = m2.group(2)
            table = m2.group(1)
            drops.append(f'ALTER TABLE {table} DROP CONSTRAINT IF EXISTS {constraint};')
            continue
    return drops


def apply_statements(cfg, statements):
    conn = None
    log_lines = []
    try:
        conn = psycopg2.connect(**cfg)
        conn.autocommit = False
        cur = conn.cursor()
        for i, stmt in enumerate(statements, 1):
            stmt = stmt.strip()
            if not stmt:
                continue
            start = datetime.utcnow()
            try:
                cur.execute(stmt)
                conn.commit()
                duration = (datetime.utcnow() - start).total_seconds()
                preview = stmt[:200].replace('\n', ' ').replace('\r', ' ')
                msg = f"OK | {i} | {duration:.3f}s | {preview}"
                print(msg)
                log_lines.append(msg)
            except Exception as e:
                conn.rollback()
                err = str(e).replace('\n', ' ')
                preview = stmt[:200].replace('\n', ' ').replace('\r', ' ')
                msg = f"ERROR | {i} | {err} | {preview}"
                print(msg)
                log_lines.append(msg)
        cur.close()
    finally:
        if conn:
            conn.close()
    return log_lines


def save_file(path, lines):
    with open(path, 'w', encoding='utf-8') as f:
        if isinstance(lines, list):
            for l in lines:
                f.write(l.rstrip('\n') + '\n')
        else:
            f.write(lines)


def main():
    print('Carregando configuração do banco...')
    cfg = load_db_config()
    if not cfg:
        print('Configuração de banco não encontrada. Abortando.')
        sys.exit(1)
    print('Lendo recomendações...')
    statements = parse_recommendations(RECOMMENDATIONS_PATH)
    print(f'Encontradas {len(statements)} instruções.')
    print('Gerando rollback...')
    drops = generate_rollback(statements)
    save_file(ROLLBACK_PATH, '\n'.join(drops))
    print(f'Rollback escrito em: {ROLLBACK_PATH}')
    print('Aplicando instruções (uma por vez)...')
    logs = apply_statements(cfg, statements)
    save_file(LOG_PATH, logs)
    print(f'Execução finalizada. Log em: {LOG_PATH}')


if __name__ == '__main__':
    main()
