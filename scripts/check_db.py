import asyncio
from app.config import settings
import asyncpg


async def main():
    print("Trying to connect with:")
    print("host", settings.postgres_host)
    print("port", settings.postgres_port)
    print("db", settings.postgres_database)
    print("user", settings.postgres_user)
    pw = (
        settings.postgres_password.get_secret_value()
        if hasattr(settings.postgres_password, "get_secret_value")
        else settings.postgres_password
    )
    print("pwd set?", bool(pw))
    try:
        conn = await asyncpg.connect(
            host=settings.postgres_host,
            port=settings.postgres_port,
            database=settings.postgres_database,
            user=settings.postgres_user,
            password=pw,
            ssl=None,
        )
        print("CONNECTED")
        recs = await conn.fetch(
            "SELECT table_schema,table_name FROM information_schema.tables WHERE table_schema='usuarios' LIMIT 10"
        )
        print("Tables in usuarios schema:", recs)
        await conn.close()
    except Exception as e:
        print("ERROR", e)


asyncio.run(main())
