import asyncio
from app.database import get_postgres_connection


async def check_views():
    conn = await get_postgres_connection()
    try:
        # Verificar Views
        views = await conn.fetch(
            """
            SELECT table_schema, table_name 
            FROM information_schema.tables 
            WHERE table_type = 'VIEW' AND table_schema NOT IN ('pg_catalog', 'information_schema')
        """
        )

        print(f"\n📊 Views encontradas: {len(views)}")
        for view in views:
            print(f"  - {view['table_schema']}.{view['table_name']}")

            # Verificar definição da view
            view_def = await conn.fetch(
                f"""
                SELECT pg_get_viewdef('{view['table_schema']}.{view['table_name']}'::regclass)
            """
            )
            if view_def and view_def[0][0]:
                view_sql = view_def[0][0]
                if "usuarios.pessoa" in view_sql:
                    print(f"    ⚠️ REFERENCIA usuarios.pessoa!")

    except Exception as e:
        print(f"Erro: {e}")
    finally:
        await conn.close()


asyncio.run(check_views())
