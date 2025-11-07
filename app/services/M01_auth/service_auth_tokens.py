"""Serviços para criação e validação de tokens de recuperação/verificação."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import uuid4

import asyncpg


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _expires_at(hours: int) -> datetime:
    return _now_utc() + timedelta(hours=hours)


async def create_recovery_token(
    conn: asyncpg.Connection,
    conta_id: Any,
    token: str,
    expires_hours: int = 2,
) -> asyncpg.Record:
    """Insere um token de recuperação na tabela `usuarios.token_recuperacao`."""

    expires = _expires_at(expires_hours)
    sql = """
        INSERT INTO usuarios.token_recuperacao (
            id, conta_usuario_id, token, tipo, expires_at
        ) VALUES ($1, $2, $3, 'password_reset', $4)
        RETURNING id, conta_usuario_id, token, tipo, expires_at, usado
    """

    token_id = uuid4()
    return await conn.fetchrow(sql, token_id, conta_id, token, expires)


async def fetch_valid_recovery_token(
    conn: asyncpg.Connection,
    token: str,
) -> Optional[asyncpg.Record]:
    """Retorna token válido (não usado e não expirado) ou None."""

    sql = """
        SELECT id, conta_usuario_id, token, tipo, expires_at, usado
        FROM usuarios.token_recuperacao
        WHERE token = $1 AND usado = FALSE AND expires_at > CURRENT_TIMESTAMP
    """

    return await conn.fetchrow(sql, token)


async def mark_token_used(conn: asyncpg.Connection, token_id: Any) -> None:
    await conn.execute(
        """
        UPDATE usuarios.token_recuperacao
        SET usado = TRUE, usado_em = CURRENT_TIMESTAMP
        WHERE id = $1
        """,
        token_id,
    )


async def create_email_verification_token(
    conn: asyncpg.Connection,
    conta_id: Any,
    token: str,
    expires_hours: int = 24,
) -> asyncpg.Record:
    """Insere um token de verificação de email."""

    expires = _expires_at(expires_hours)
    sql = """
        INSERT INTO usuarios.token_recuperacao (
            id, conta_usuario_id, token, tipo, expires_at
        ) VALUES ($1, $2, $3, 'email_verification', $4)
        RETURNING id, conta_usuario_id, token, tipo, expires_at, usado
    """

    token_id = uuid4()
    return await conn.fetchrow(sql, token_id, conta_id, token, expires)


async def fetch_valid_verification_token(
    conn: asyncpg.Connection,
    token: str,
) -> Optional[asyncpg.Record]:
    """Retorna token de verificação válido ou None."""

    sql = """
        SELECT id, conta_usuario_id, token, tipo, expires_at, usado
        FROM usuarios.token_recuperacao
        WHERE token = $1
          AND tipo = 'email_verification'
          AND usado = FALSE
          AND expires_at > CURRENT_TIMESTAMP
    """

    return await conn.fetchrow(sql, token)


async def invalidate_previous_tokens(
    conn: asyncpg.Connection, conta_id: Any, tipo: str
) -> None:
    """Invalida tokens anteriores do mesmo tipo para uma conta."""

    await conn.execute(
        """
        UPDATE usuarios.token_recuperacao
        SET usado = TRUE, usado_em = CURRENT_TIMESTAMP
        WHERE conta_usuario_id = $1
          AND tipo = $2
          AND usado = FALSE
          AND expires_at > CURRENT_TIMESTAMP
        """,
        conta_id,
        tipo,
    )
