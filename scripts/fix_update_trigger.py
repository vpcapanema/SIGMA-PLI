import asyncio
from app.database import init_postgres, get_postgres_connection

SQL = """
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    -- Tenta setar updated_at se a coluna existir
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
    EXCEPTION WHEN SQLSTATE '42703' THEN
        -- coluna updated_at não existe nesta tabela, ignora
        NULL;
    END;

    -- Tenta setar atualizado_em se a coluna existir
    BEGIN
        NEW.atualizado_em = CURRENT_TIMESTAMP;
    EXCEPTION WHEN SQLSTATE '42703' THEN
        -- coluna atualizado_em não existe nesta tabela, ignora
        NULL;
    END;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""


async def run():
    await init_postgres()
    conn = await get_postgres_connection()
    try:
        await conn.execute(SQL)
        print("replaced function public.update_updated_at_column")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run())
