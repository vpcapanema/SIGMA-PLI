import asyncio
from app.database import init_postgres, get_postgres_connection
from app.services.M01_auth import service_auth_accounts


async def t():
    await init_postgres()
    conn = await get_postgres_connection()
    try:
        acc = await service_auth_accounts.fetch_account_by_identifier(
            conn, "joao.silva"
        )
        print("account", bool(acc))
        if acc:
            print("password_hash", acc["password_hash"][:20])
            ok = service_auth_accounts.authenticate_user(
                "sigma123", acc["password_hash"]
            )
            print("verify ok", ok)
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(t())
