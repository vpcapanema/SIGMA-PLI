import os
import re
import sys
import psycopg2

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RECOMMENDATIONS_PATH = os.path.join(BASE, 'reports', 'schema_recommendations.sql')
USAGE_REPORT = os.path.join(BASE, 'reports', 'index_usage_report.txt')
USAGE_CSV = os.path.join(BASE, 'reports', 'index_usage_report.csv')
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


def query_usage(cfg, index_names):
    conn = psycopg2.connect(**cfg)
    cur = conn.cursor()
    rows = []
    for idx_name, table in index_names:
        cur.execute("""
            SELECT c.oid, c.relname as indexname,
                   pg_size_pretty(pg_relation_size(c.oid)) as index_size,
                   COALESCE(s.idx_scan,0) as idx_scan,
                   COALESCE(s.idx_tup_read,0) as idx_tup_read,
                   COALESCE(s.idx_tup_fetch,0) as idx_tup_fetch,
                   pg_get_indexdef(c.oid) as indexdef
            FROM pg_class c
            LEFT JOIN pg_stat_user_indexes s ON s.indexrelid = c.oid
            WHERE c.relname = %s AND c.relkind = 'i'
        """, (idx_name,))
        r = cur.fetchone()
        if r:
            rows.append({
                'indexname': r[1],
                'index_size': r[2],
                'idx_scan': int(r[3]),
                'idx_tup_read': int(r[4]),
                'idx_tup_fetch': int(r[5]),
                'indexdef': r[6]
            })
        else:
            rows.append({
                'indexname': idx_name,
                'index_size': '0',
                'idx_scan': 0,
                'idx_tup_read': 0,
                'idx_tup_fetch': 0,
                'indexdef': ''
            })
    cur.close()
    conn.close()
    return rows


def save_report_txt(path, rows):
    with open(path, 'w', encoding='utf-8') as f:
        f.write('indexname|index_size|idx_scan|idx_tup_read|idx_tup_fetch|indexdef\n')
        for r in rows:
            line = f"{r['indexname']}|{r['index_size']}|{r['idx_scan']}|{r['idx_tup_read']}|{r['idx_tup_fetch']}|{r['indexdef']}\n"
            f.write(line)


def save_report_csv(path, rows):
    import csv
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f)
        w.writerow(['indexname','index_size','idx_scan','idx_tup_read','idx_tup_fetch','indexdef'])
        for r in rows:
            w.writerow([r['indexname'], r['index_size'], r['idx_scan'], r['idx_tup_read'], r['idx_tup_fetch'], r['indexdef']])


def summarize(rows):
    used = [r for r in rows if r['idx_scan'] > 0]
    unused = [r for r in rows if r['idx_scan'] == 0]
    largest = sorted(rows, key=lambda x: parse_size(x['index_size']), reverse=True)[:10]
    top_used = sorted(rows, key=lambda x: x['idx_scan'], reverse=True)[:10]
    return used, unused, largest, top_used


def parse_size(s):
    # convert human readable sizes to bytes roughly
    if not s:
        return 0
    m = re.match(r'(\d+(?:\.\d+)?)([KMGTP]?)B?$', s)
    if not m:
        return 0
    val = float(m.group(1))
    unit = m.group(2)
    mul = {'':1, 'K':1024, 'M':1024**2, 'G':1024**3, 'T':1024**4}
    return int(val * mul.get(unit,1))


def main():
    cfg = load_db_config()
    if not cfg:
        print('Configuração do banco não encontrada. Abortando.')
        sys.exit(1)
    idxs = parse_index_names(RECOMMENDATIONS_PATH)
    print(f'Coletando estatísticas para {len(idxs)} índices...')
    rows = query_usage(cfg, idxs)
    save_report_txt(USAGE_REPORT, rows)
    save_report_csv(USAGE_CSV, rows)
    used, unused, largest, top_used = summarize(rows)
    print(f'Total índices: {len(rows)}. Usados: {len(used)}. Não usados: {len(unused)}')
    print('Maiores índices (top 5):')
    for r in largest[:5]:
        print(f" - {r['indexname']} {r['index_size']}")
    print('Mais usados (top 5):')
    for r in top_used[:5]:
        print(f" - {r['indexname']} scans={r['idx_scan']}")


if __name__ == '__main__':
    main()
