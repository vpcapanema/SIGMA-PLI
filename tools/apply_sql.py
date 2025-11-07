import os
import re
import sys
import asyncio
from pathlib import Path

import asyncpg

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"


# Simple .env loader (only the keys we need)
def load_env_from_file(path: Path):
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"([A-Za-z_][A-Za-z0-9_]*)=(.*)", line)
        if not m:
            continue
        k, v = m.group(1), m.group(2)
        # Remove optional surrounding quotes
        if v.startswith(('"', "'")) and v.endswith(('"', "'")) and len(v) >= 2:
            v = v[1:-1]
        os.environ.setdefault(k, v)


async def run_sql(sql_text: str):
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    db = os.getenv("POSTGRES_DATABASE", "sigma_pli")
    user = os.getenv("POSTGRES_USER", "sigma_admin")
    pwd = os.getenv("POSTGRES_PASSWORD", "")

    conn = await asyncpg.connect(
        host=host, port=port, database=db, user=user, password=pwd, ssl=None
    )
    try:
        await conn.execute(sql_text)
        print("✅ SQL aplicado com sucesso")
    finally:
        await conn.close()


async def main():
    load_env_from_file(ENV_FILE)
    # Default migration path or provided arg
    migration_path = (
        sys.argv[1]
        if len(sys.argv) > 1
        else str(
            ROOT / "sql" / "migrations" / "migration_007_add_cargo_cadastro_pessoa.sql"
        )
    )
    migration_path = str(Path(migration_path).resolve())
    if not Path(migration_path).exists():
        print(f"❌ Arquivo SQL não encontrado: {migration_path}")
        return 2
    sql_text = Path(migration_path).read_text(encoding="utf-8")
    try:
        await run_sql(sql_text)
    except Exception as e:
        print("❌ ERRO ao aplicar SQL:", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
