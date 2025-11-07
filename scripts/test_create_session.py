import asyncio
import secrets
from app.database import init_postgres, get_postgres_connection
from app.services.M01_auth import service_auth_accounts, service_auth_sessions
from app.utils.auth_tokens import build_token
from app.config import settings


async def t():
    await init_postgres()
    conn = await get_postgres_connection()
    try:
        acc = await service_auth_accounts.fetch_account_by_identifier(
            conn, "joao.silva"
        )
        print("acc", bool(acc))
        if not acc:
            return
        session_token = secrets.token_urlsafe(24)
        session_row = await service_auth_sessions.create_session(
            conn,
            acc["conta_id"],
            session_token,
            "127.0.0.1",
            "test-agent",
            settings.jwt_expiration_hours,
        )
        print("session created", session_row)
        payload = {
            "sub": str(acc["conta_id"]),
            "sid": str(session_row["id"]),
            "stk": session_row["token"],
            "name": acc.get("nome_completo"),
        }
        jwt = build_token(payload, settings.jwt_expiration_hours)
        print("jwt len", len(jwt))
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(t())
