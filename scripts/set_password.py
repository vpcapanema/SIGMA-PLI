import asyncio
from app.database import init_postgres, get_postgres_connection
from app.services.M01_auth import service_auth_security


async def run():
    await init_postgres()
    conn = await get_postgres_connection()
    try:
        new_hash = service_auth_security.hash_password("sigma123")
        await conn.execute(
            "UPDATE usuarios.conta_usuario SET password_hash=$1 WHERE username=$2",
            new_hash,
            "joao.silva",
        )
        print("updated")
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(run())
