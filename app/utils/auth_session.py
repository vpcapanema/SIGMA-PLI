"""Dependências e utilitários para recuperar sessão autenticada."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import asyncpg
from fastapi import HTTPException, Request, status

from app.database import get_postgres_connection, postgres_pool
from app.schemas.M01_auth.schema_auth import AuthenticatedUser, SessionInfo
from app.services.M01_auth import service_auth_sessions
from app.utils.auth_tokens import decode_token


async def _fetch_account_summary(
    conn: asyncpg.Connection,
    conta_id: str,
) -> Optional[asyncpg.Record]:
    return await conn.fetchrow(
        """
        SELECT
            cu.id AS conta_id,
            cu.username,
            cu.email,
            cu.ultimo_login,
            p.nome_completo,
            COALESCE(p.nome_completo, '') AS primeiro_nome,
            COALESCE(p.nome_completo, '') AS ultimo_nome
        FROM usuarios.usuario cu
        LEFT JOIN cadastro.pessoa p ON p.id = cu.pessoa_id
        WHERE cu.id = $1
    """,
        conta_id,
    )


async def require_authenticated_user(
    request: Request,
) -> AuthenticatedUser:
    """Dependency para rotas que necessitam de autenticação."""

    token = request.cookies.get("auth_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from exc

    conta_id = payload.get("sub")
    session_id = payload.get("sid")
    session_token = payload.get("stk")

    if not (conta_id and session_id and session_token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    conn = await get_postgres_connection()
    try:
        session_row = await service_auth_sessions.get_active_session(
            conn,
            session_id,
            session_token,
        )
        if not session_row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        account_row = await _fetch_account_summary(conn, conta_id)
        if not account_row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        return AuthenticatedUser(
            conta_id=str(account_row["conta_id"]),
            username=account_row["username"],
            nome_completo=account_row["nome_completo"] or "Usuário",
            email=account_row["email"],
            primeiro_nome=account_row["primeiro_nome"],
            ultimo_nome=account_row["ultimo_nome"],
            ultimo_login=account_row["ultimo_login"],
        )
    finally:
        if postgres_pool and conn:
            await postgres_pool.release(conn)


async def require_active_session(
    request: Request,
) -> SessionInfo:
    """Retorna dados da sessão ativa, lançando 401 caso inválida."""

    token = request.cookies.get("auth_token")
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    try:
        payload = decode_token(token)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from exc

    session_id = payload.get("sid")
    session_token = payload.get("stk")
    expires_at_raw = payload.get("exp")

    if not (session_id and session_token and expires_at_raw):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    conn = await get_postgres_connection()
    try:
        session_row = await service_auth_sessions.get_active_session(
            conn,
            session_id,
            session_token,
        )
        if not session_row:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        expires_at = datetime.fromtimestamp(expires_at_raw, tz=timezone.utc)

        return SessionInfo(
            session_id=str(session_row["id"]),
            expires_at=expires_at,
        )
    finally:
        if postgres_pool and conn:
            await postgres_pool.release(conn)


async def get_optional_authenticated_user(
    request: Request,
) -> Optional[AuthenticatedUser]:
    """Retorna usuário autenticado quando sessão válida, ou None."""

    token = request.cookies.get("auth_token")
    if not token:
        return None

    try:
        payload = decode_token(token)
    except ValueError:
        return None

    conta_id = payload.get("sub")
    session_id = payload.get("sid")
    session_token = payload.get("stk")

    if not (conta_id and session_id and session_token):
        return None

    conn = await get_postgres_connection()
    try:
        session_row = await service_auth_sessions.get_active_session(
            conn,
            session_id,
            session_token,
        )
        if not session_row:
            return None

        account_row = await _fetch_account_summary(conn, conta_id)
        if not account_row:
            return None

        return AuthenticatedUser(
            conta_id=str(account_row["conta_id"]),
            username=account_row["username"],
            nome_completo=account_row["nome_completo"] or "Usuário",
            email=account_row["email"],
            primeiro_nome=account_row["primeiro_nome"],
            ultimo_nome=account_row["ultimo_nome"],
            ultimo_login=account_row["ultimo_login"],
        )
    finally:
        if postgres_pool and conn:
            await postgres_pool.release(conn)
