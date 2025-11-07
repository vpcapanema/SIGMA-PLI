import os
import sys
import asyncio
from pathlib import Path
import asyncpg

# Garantir que o diretório raiz do projeto esteja no sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("ENABLE_POSTGRES", "true")
os.environ.setdefault("POSTGRES_HOST", os.getenv("POSTGRES_HOST", "localhost"))
os.environ.setdefault("POSTGRES_PORT", os.getenv("POSTGRES_PORT", "5432"))
os.environ.setdefault("POSTGRES_DATABASE", os.getenv("POSTGRES_DATABASE", "sigma_pli"))
os.environ.setdefault("POSTGRES_USER", os.getenv("POSTGRES_USER", "sigma_admin"))
os.environ.setdefault("POSTGRES_PASSWORD", os.getenv("POSTGRES_PASSWORD", ""))


async def main():
    try:
        from app.database import init_db, get_pg_pool
    except Exception as e:
        print("IMPORT_ERROR", e)
        return 1

    try:
        await init_db()
        pool = await get_pg_pool()
    except Exception as e:
        print("INIT_ERROR", e)
        pool = None

    if pool is None:
        # Fallback direto via asyncpg
        try:
            pool = await asyncpg.create_pool(
                host=os.environ.get("POSTGRES_HOST", "localhost"),
                port=int(os.environ.get("POSTGRES_PORT", "5432")),
                database=os.environ.get("POSTGRES_DATABASE", "sigma_pli"),
                user=os.environ.get("POSTGRES_USER", "sigma_admin"),
                password=os.environ.get("POSTGRES_PASSWORD", ""),
                ssl=None,
                min_size=1,
                max_size=5,
            )
            print("✅ Conectado via fallback asyncpg")
        except Exception as e2:
            print("NO_POOL", e2)
            return 3

    async with pool.acquire() as conn:
        print("🔎 Listando triggers na tabela cadastro.pessoa...")
        rows1 = await conn.fetch(
            """
            SELECT n.nspname, c.relname, t.tgname, pg_get_triggerdef(t.oid) as def
            FROM pg_trigger t
            JOIN pg_class c ON c.oid=t.tgrelid
            JOIN pg_namespace n ON n.oid=c.relnamespace
            WHERE n.nspname='cadastro' AND c.relname='pessoa' AND NOT t.tgisinternal
            ORDER BY t.tgname
            """
        )
        print(f"TRIGGERS cadastro.pessoa: {len(rows1)}")
        for r in rows1:
            print(f"- {r['tgname']}: {r['def']}")

        print("\n🔎 Procurando funções que referenciam usuarios.pessoa...")
        rows2 = await conn.fetch(
            """
            SELECT n.nspname, p.proname
            FROM pg_proc p
            JOIN pg_namespace n ON n.oid=p.pronamespace
            WHERE pg_get_functiondef(p.oid) ILIKE '%usuarios.pessoa%'
            ORDER BY 1,2
            """
        )
        print(f"FUNCOES que referenciam usuarios.pessoa: {len(rows2)}")
        for r in rows2:
            print(f"- {r['nspname']}.{r['proname']}")

        print("\n🔎 Verificando RULES em cadastro/usuarios...")
        rows3 = await conn.fetch(
            """
            SELECT schemaname, tablename, rulename, definition
            FROM pg_rules
            WHERE schemaname in ('cadastro','usuarios')
            ORDER BY 1,2,3
            """
        )
        print(f"RULES em cadastro/usuarios: {len(rows3)}")
        for r in rows3:
            if "usuarios.pessoa" in r["definition"]:
                print(
                    f"- RULE {r['rulename']} on {r['schemaname']}.{r['tablename']} :: refs usuarios.pessoa"
                )

    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
