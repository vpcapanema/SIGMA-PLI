import asyncio
from app.database import get_postgres_connection


async def apply_migration():
    with open(
        "sql/migrations/migration_010_remove_usuarios_pessoa_consolidate.sql", "r"
    ) as f:
        sql = f.read()

    conn = await get_postgres_connection()
    try:
        print("Executando migration 010...")
        await conn.execute(sql)
        print("✅ Migration 010 aplicada com sucesso!")

        # Verificar se a tabela foi removida
        check = await conn.fetch(
            "SELECT tablename FROM pg_tables WHERE schemaname='usuarios' AND tablename='pessoa'"
        )
        if check:
            print("❌ Tabela usuarios.pessoa ainda existe!")
        else:
            print("✅ Tabela usuarios.pessoa foi removida com sucesso!")
    except Exception as e:
        print(f"❌ Erro: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await conn.close()


asyncio.run(apply_migration())
