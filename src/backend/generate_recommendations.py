import json
import os

REPORT_JSON = os.path.join(os.getcwd(), 'reports', 'schema_report.json')
OUT_SQL = os.path.join(os.getcwd(), 'reports', 'schema_recommendations.sql')

def main():
    with open(REPORT_JSON, 'r', encoding='utf-8') as f:
        report = json.load(f)

    d = report.get('dicionario', {})
    sql = []
    rec_count = 0

    # Helper to check if gin/index exists for column
    def has_gin(table_info, col_name):
        for idx in table_info.get('indexes', []):
            if 'gin' in idx.get('def', '').lower() and col_name in idx.get('def', ''):
                return True
        return False

    # Prepare set of existing tables for FK inference
    existing_tables = set(d.keys())

    for table, info in d.items():
        cols = info.get('columns', [])
        indexes = info.get('indexes', [])

        # Recommend GIN indexes for ARRAY or jsonb columns missing them
        for c in cols:
            name = c['column_name']
            dtype = c['data_type'].lower()
            if dtype in ('jsonb',) or dtype == 'array' or 'array' in dtype:
                if not has_gin(info, name):
                    idx_name = f"gin_{table}_{name}"
                    sql.append(f"CREATE INDEX IF NOT EXISTS {idx_name} ON dicionario.{table} USING gin ({name});")
                    rec_count += 1

        # Recommend FK constraints for *_id columns if missing and referenced table exists
        fk_cols = {fk['column'] for fk in info.get('foreign_keys', [])} if info.get('foreign_keys') else set()
        for c in cols:
            name = c['column_name']
            if name.endswith('_id') and name not in fk_cols:
                # infer referenced table names heuristically
                candidate = None
                # produtor_id -> produtor
                if name == 'produtor_id' and 'produtor' in existing_tables:
                    candidate = 'produtor'
                # estrutura_id -> try to find matching estrutura__* table (most likely exists)
                if name == 'estrutura_id':
                    # prefer exact matching by looking at table prefixes
                    # if table is conteudo__X, reference estrutura__X
                    if table.startswith('conteudo__'):
                        suffix = table.split('conteudo__',1)[1]
                        ref = f"estrutura__{suffix}"
                        if ref in existing_tables:
                            candidate = ref
                # versao_id -> versao_arquivo
                if name == 'versao_id' and 'versao_arquivo' in existing_tables:
                    candidate = 'versao_arquivo'

                if candidate:
                    constraint_name = f"fk_{table}_{name}"
                    sql.append(f"ALTER TABLE dicionario.{table} ADD CONSTRAINT {constraint_name} FOREIGN KEY ({name}) REFERENCES dicionario.{candidate}(id) DEFERRABLE INITIALLY DEFERRED;")
                    rec_count += 1

    if rec_count == 0:
        sql.append('-- Nenhuma recomendação automática gerada (já consistente com regras aplicadas).')

    with open(OUT_SQL, 'w', encoding='utf-8') as f:
        f.write('\n'.join(sql))

    print(f"Geradas {rec_count} recomendações em: {OUT_SQL}")

if __name__ == '__main__':
    main()
