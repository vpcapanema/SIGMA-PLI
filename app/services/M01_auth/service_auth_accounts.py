"""Serviços para acessar `usuarios.conta_usuario` e entidades relacionadas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

import asyncpg

from app.services.M01_auth.service_auth_security import verify_password


FAILED_ATTEMPTS_LIMIT = 5
LOCK_DURATION_MINUTES = 15


async def fetch_account_by_identifier(
    conn: asyncpg.Connection,
    identifier: str,
) -> Optional[asyncpg.Record]:
    """Obtém conta por username ou email (ignorando caixa)."""

    sql = """
        SELECT
            cu.id AS conta_id,
            cu.username,
            cu.email,
            cu.password_hash,
            cu.salt,
            cu.email_verificado,
            cu.telefone_verificado,
            cu.dois_fatores_habilitado,
            cu.secreto_2fa,
            cu.ultimo_login,
            cu.ultimo_ip,
            cu.tentativas_falha,
            cu.bloqueado_ate,
            cu.ativo,
            cu.pessoa_id,
            p.nome_completo,
            COALESCE(p.nome_completo, '') AS primeiro_nome,
            COALESCE(p.nome_completo, '') AS ultimo_nome,
            p.email AS pessoa_email,
            p.telefone AS pessoa_telefone,
            p.cargo,
            p.instituicao_id,
            p.departamento_id
        FROM usuarios.usuario cu
        LEFT JOIN cadastro.pessoa p ON p.id = cu.pessoa_id
        WHERE LOWER(cu.username) = LOWER($1) OR LOWER(cu.email) = LOWER($1)
    """

    return await conn.fetchrow(sql, identifier)


def validate_account_status(account: asyncpg.Record) -> Optional[str]:
    """Executa checagens de status e retorna mensagem de erro, se houver."""

    if not account["ativo"]:
        return "Conta de usuário inativa."

    bloqueado_ate: Optional[datetime] = account["bloqueado_ate"]
    if bloqueado_ate and bloqueado_ate > datetime.utcnow():
        return "Conta bloqueada temporariamente. Tente novamente mais tarde."

    return None


async def register_failed_attempt(
    conn: asyncpg.Connection,
    conta_id: Any,
) -> None:
    """Incrementa tentativas de falha e aplica bloqueio quando necessário."""

    row = await conn.fetchrow(
        """
        UPDATE usuarios.conta_usuario
        SET tentativas_falha = tentativas_falha + 1,
            bloqueado_ate = CASE
                WHEN tentativas_falha + 1 >= $2
                    THEN CURRENT_TIMESTAMP + ($3 * INTERVAL '1 minute')
                ELSE bloqueado_ate
            END,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE id = $1
        RETURNING tentativas_falha
        """,
        conta_id,
        FAILED_ATTEMPTS_LIMIT,
        LOCK_DURATION_MINUTES,
    )

    if row and row["tentativas_falha"] >= FAILED_ATTEMPTS_LIMIT:
        await conn.execute(
            """
            UPDATE usuarios.conta_usuario
            SET bloqueado_ate = CURRENT_TIMESTAMP + ($1 * INTERVAL '1 minute')
            WHERE id = $2
            """,
            LOCK_DURATION_MINUTES,
            conta_id,
        )


async def reset_failed_attempts(
    conn: asyncpg.Connection,
    conta_id: Any,
) -> None:
    """Zera contador de tentativas e remove bloqueio."""

    await conn.execute(
        """
        UPDATE usuarios.conta_usuario
        SET tentativas_falha = 0,
            bloqueado_ate = NULL,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE id = $1
        """,
        conta_id,
    )


async def register_successful_login(
    conn: asyncpg.Connection,
    conta_id: Any,
    ip_address: Optional[str],
) -> None:
    """Atualiza metadados após login bem-sucedido."""

    await conn.execute(
        """
        UPDATE usuarios.conta_usuario
        SET ultimo_login = CURRENT_TIMESTAMP,
            ultimo_ip = $2,
            atualizado_em = CURRENT_TIMESTAMP
        WHERE id = $1
        """,
        conta_id,
        ip_address,
    )


def authenticate_user(password: str, stored_hash: str) -> bool:
    """Valida credenciais utilizando hash armazenado."""

    return verify_password(password, stored_hash)
