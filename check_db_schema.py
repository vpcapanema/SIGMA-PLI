#!/usr/bin/env python3
import asyncio
from app.database import get_postgres_connection


async def check_views():
    conn = await get_postgres_connection()
    try:
        # Procurar Views
        query = """
            SELECT 
                table_schema,
                table_name,
                table_type
            FROM information_schema.tables 
            WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
            ORDER BY table_schema, table_name
        """
        rows = await conn.fetch(query)
        print("📋 Tables and Views:")
        for row in rows:
            print(f"  {row['table_schema']}.{row['table_name']} ({row['table_type']})")

        # Procurar por RULEs
        query2 = """
            SELECT 
                schemaname,
                tablename,
                rulename,
                definition
            FROM pg_rules 
            WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
        """
        rules = await conn.fetch(query2)
        if rules:
            print("\n⚠️  Database Rules Found:")
            for rule in rules:
                print(f"  {rule['schemaname']}.{rule['tablename']}: {rule['rulename']}")
                if "tipo_pessoa" in str(rule.get("definition", "")).lower():
                    print(f"    ⚠️  References 'tipo_pessoa'!")
    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(check_views())
