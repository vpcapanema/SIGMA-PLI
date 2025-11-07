#!/usr/bin/env python3
import asyncio
from app.database import get_postgres_connection


async def check_pessoa_table():
    conn = await get_postgres_connection()
    try:
        # Verificar columas de usuarios.pessoa
        query = """
            SELECT 
                column_name,
                data_type,
                is_nullable
            FROM information_schema.columns 
            WHERE table_schema = 'usuarios' 
            AND table_name = 'pessoa'
            ORDER BY ordinal_position
        """
        rows = await conn.fetch(query)
        print("📋 Columns in usuarios.pessoa:")
        if rows:
            for row in rows:
                print(
                    f"  {row['column_name']}: {row['data_type']} (nullable: {row['is_nullable']})"
                )
        else:
            print("  ❌ Table not found!")

        # Verificar se é uma View
        query2 = """
            SELECT 
                table_type
            FROM information_schema.tables 
            WHERE table_schema = 'usuarios' 
            AND table_name = 'pessoa'
        """
        result = await conn.fetchrow(query2)
        if result:
            print(f"\nTable type: {result['table_type']}")

        # Se for uma View, mostrar definição
        if result and result["table_type"] == "VIEW":
            query3 = """
                SELECT 
                    view_definition
                FROM information_schema.views 
                WHERE table_schema = 'usuarios' 
                AND table_name = 'pessoa'
            """
            view_def = await conn.fetchrow(query3)
            if view_def:
                print("\nView Definition:")
                print(view_def["view_definition"])

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(check_pessoa_table())
