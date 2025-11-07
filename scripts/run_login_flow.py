import asyncio, traceback
from app.database import init_postgres, get_postgres_connection
from app.services.M01_auth import service_auth_accounts, service_auth_sessions
from app.utils.auth_tokens import build_token
from app.config import settings


async def t(identifier, password):
    await init_postgres()
    conn = await get_postgres_connection()
    try:
        account = await service_auth_accounts.fetch_account_by_identifier(
            conn, identifier
        )
        print("account", bool(account))
        if not account:
            print("no account")
            return
        status_error = service_auth_accounts.validate_account_status(account)
        print("status_error", status_error)
        ok = service_auth_accounts.authenticate_user(password, account["password_hash"])
        print("password ok", ok)
        if not ok:
            await service_auth_accounts.register_failed_attempt(
                conn, account["conta_id"]
            )
            print("registered failed attempt")
            return
        await service_auth_accounts.reset_failed_attempts(conn, account["conta_id"])
        ip = "127.0.0.1"
        ua = "test"
        session_token = "st-" + "abc"
        session_row = await service_auth_sessions.create_session(
            conn,
            account["conta_id"],
            session_token,
            ip,
            ua,
            settings.jwt_expiration_hours,
        )
        print("session_row", session_row)
    except Exception as e:
        print("exception")
        traceback.print_exc()
    finally:
        await conn.close()


if __name__ == "__main__":
    asyncio.run(t("joao.silva", "wrongpass"))
