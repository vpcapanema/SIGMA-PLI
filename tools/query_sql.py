import os
import re
import sys
import asyncio
from pathlib import Path

import asyncpg

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"


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
        if v.startswith(('"', "'")) and v.endswith(('"', "'")) and len(v) >= 2:
            v = v[1:-1]
        os.environ.setdefault(k, v)


async def run_query(sql_text: str):
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = int(os.getenv("POSTGRES_PORT", "5432"))
    db = os.getenv("POSTGRES_DATABASE", "sigma_pli")
    user = os.getenv("POSTGRES_USER", "sigma_admin")
    pwd = os.getenv("POSTGRES_PASSWORD", "")

    conn = await asyncpg.connect(
        host=host, port=port, database=db, user=user, password=pwd, ssl=None
    )
    try:
        # Use fetch to handle both SELECT and utility by printing a notice
        if sql_text.strip().lower().startswith("select"):
            rows = await conn.fetch(sql_text)
            print(f"ROWS: {len(rows)}")
            for r in rows:
                print(dict(r))
        else:
            res = await conn.execute(sql_text)
            print(res)
    finally:
        await conn.close()


async def main():
    load_env_from_file(ENV_FILE)
    if len(sys.argv) < 2:
        print('Usage: python tools/query_sql.py "<SQL>"')
        return 2
    sql_text = sys.argv[1]
    try:
        await run_query(sql_text)
    except Exception as e:
        print("ERROR:", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
