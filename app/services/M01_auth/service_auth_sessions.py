"""Serviços para gerenciamento de sessões de autenticação."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Optional
from uuid import uuid4

import asyncpg


def _now_utc() -> datetime:
    # Retornar datetime UTC *sem* tzinfo para compatibilidade com colunas TIMESTAMP
    return datetime.utcnow()


def _expires_at(hours: int) -> datetime:
    return _now_utc() + timedelta(hours=hours)


async def create_session(
    conn: asyncpg.Connection,
    conta_id: Any,
    token: str,
    ip_address: Optional[str],
    user_agent: Optional[str],
    expiration_hours: int,
) -> asyncpg.Record:
    """Cria registro em `usuarios.sessao` e retorna linha criada."""

    expires_at = _expires_at(expiration_hours)
    sql = """
        INSERT INTO usuarios.sessao (
            id,
            conta_usuario_id,
            token,
            ip_address,
            user_agent,
            expires_at
        )
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, conta_usuario_id, token, expires_at, created_at
    """

    session_id = uuid4()
    return await conn.fetchrow(
        sql,
        session_id,
        conta_id,
        token,
        ip_address,
        user_agent,
        expires_at,
    )


async def revoke_session(conn: asyncpg.Connection, session_id: Any) -> None:
    """Marca sessão como revogada."""

    await conn.execute(
        """
        UPDATE usuarios.sessao
        SET revoked = TRUE,
            revoked_at = CURRENT_TIMESTAMP
        WHERE id = $1
        """,
        session_id,
    )


async def revoke_session_by_token(
    conn: asyncpg.Connection,
    token: str,
) -> None:
    """Revoga sessão a partir do token armazenado."""

    await conn.execute(
        """
        UPDATE usuarios.sessao
        SET revoked = TRUE,
            revoked_at = CURRENT_TIMESTAMP
        WHERE token = $1
        """,
        token,
    )


async def get_active_session(
    conn: asyncpg.Connection,
    session_id: Any,
    token: str,
) -> Optional[asyncpg.Record]:
    """Obtém sessão ativa e não expirada."""

    sql = """
        SELECT id, conta_usuario_id, token, expires_at, revoked
        FROM usuarios.sessao
        WHERE id = $1 AND token = $2 AND revoked = FALSE
          AND expires_at > CURRENT_TIMESTAMP
    """

    return await conn.fetchrow(sql, session_id, token)
