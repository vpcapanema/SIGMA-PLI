"""
Verificar estrutura atual da tabela cadastro.instituicao
"""

import asyncio
import asyncpg
import os


async def check_table():
    conn = await asyncpg.connect(
        os.getenv(
            "DATABASE_URL",
            "postgresql://pli_sigma_admin:Semil%402025@sigma-pli-postgresql-db.cwlmgc4igdh8.us-east-1.rds.amazonaws.com:5432/sigma_pli_db",
        )
    )

    try:
        result = await conn.fetch(
            """
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_schema = 'cadastro' 
            AND table_name = 'instituicao'
            ORDER BY ordinal_position
        """
        )

        print(f"\n✅ Tabela cadastro.instituicao tem {len(result)} colunas:\n")
        for row in result:
            print(
                f"  - {row['column_name']:<30} {row['data_type']:<20} {'NULL' if row['is_nullable'] == 'YES' else 'NOT NULL'}"
            )
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(check_table())
