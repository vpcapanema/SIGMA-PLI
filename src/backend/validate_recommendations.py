import os
import re
import sys
import psycopg2

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RECOMMENDATIONS_PATH = os.path.join(BASE, 'reports', 'schema_recommendations.sql')
VALIDATION_REPORT = os.path.join(BASE, 'reports', 'validation_report.txt')
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.py')

def load_db_config():
    import importlib.util
    spec = importlib.util.spec_from_file_location('cfg', CONFIG_PATH)
    cfg_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cfg_mod)
    cfg = getattr(cfg_mod, 'DB_CONFIG', None)
    if not cfg:
        url = getattr(cfg_mod, 'DATABASE_URL', None)
        if url:
            m = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(\w+)', url)
            if m:
                cfg = dict(user=m.group(1), password=m.group(2), host=m.group(3), port=int(m.group(4)), database=m.group(5))
    return cfg


def parse_index_names(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    names = []
    for line in content.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r'CREATE\s+INDEX\s+(?:IF\s+NOT\s+EXISTS\s+)?(\S+)\s+ON\s+([\w\.\"]+)', line, re.IGNORECASE)
        if m:
            names.append((m.group(1), m.group(2)))
    return names


def validate(cfg, index_list):
    conn = psycopg2.connect(**cfg)
    cur = conn.cursor()
    report_lines = []
    for idx_name, table in index_list:
        # check pg_indexes
        cur.execute("SELECT indexname, indexdef FROM pg_indexes WHERE indexname = %s", (idx_name,))
        row = cur.fetchone()
        if row:
            report_lines.append(f"OK | {idx_name} | found | {row[1]}")
        else:
            # try pg_class
            cur.execute("SELECT relname FROM pg_class WHERE relname = %s", (idx_name,))
            r2 = cur.fetchone()
            if r2:
                report_lines.append(f"OK | {idx_name} | found in pg_class")
            else:
                report_lines.append(f"MISSING | {idx_name} | not found")
    cur.close()
    conn.close()
    return report_lines


def save_report(path, lines):
    with open(path, 'w', encoding='utf-8') as f:
        for l in lines:
            f.write(l + '\n')


def main():
    cfg = load_db_config()
    if not cfg:
        print('Configuração do banco não encontrada. Abortando.')
        sys.exit(1)
    idxs = parse_index_names(RECOMMENDATIONS_PATH)
    print(f'Validação de {len(idxs)} índices...')
    report = validate(cfg, idxs)
    save_report(VALIDATION_REPORT, report)
    print(f'Relatório salvo em {VALIDATION_REPORT}')


if __name__ == '__main__':
    main()
