"""
Serviço de auditoria de tentativas de login
Registra todas as tentativas de login (sucesso e falha)
"""

from typing import Optional
from datetime import datetime
import uuid

from app.database import get_postgres_connection


class LoginAuditService:
    """Serviço para auditoria de tentativas de login"""

    @staticmethod
    async def log_login_attempt(
        username: Optional[str] = None,
        email: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        sucesso: bool = False,
        motivo_falha: Optional[str] = None,
        conta_usuario_id: Optional[uuid.UUID] = None,
    ):
        """
        Registrar tentativa de login

        Args:
            username: Nome de usuário utilizado
            email: Email utilizado
            ip_address: Endereço IP
            user_agent: User agent do navegador
            sucesso: Se o login foi bem-sucedido
            motivo_falha: Motivo da falha (se aplicável)
            conta_usuario_id: ID da conta (se identificada)
        """
        conn = await get_postgres_connection()
        try:
            query = """
                INSERT INTO usuarios.tentativa_login
                (username, email, ip_address, user_agent, sucesso, motivo_falha, conta_usuario_id)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
            """

            await conn.execute(
                query,
                username,
                email,
                ip_address,
                user_agent,
                sucesso,
                motivo_falha,
                conta_usuario_id,
            )
        finally:
            await conn.close()

    @staticmethod
    async def get_recent_attempts(
        conta_usuario_id: uuid.UUID, limit: int = 10
    ) -> list[dict]:
        """
        Buscar tentativas recentes de login de um usuário

        Args:
            conta_usuario_id: ID da conta do usuário
            limit: Número máximo de registros

        Returns:
            Lista de tentativas de login
        """
        conn = await get_postgres_connection()
        try:
            query = """
                SELECT
                    id,
                    username,
                    email,
                    ip_address,
                    user_agent,
                    sucesso,
                    motivo_falha,
                    created_at
                FROM usuarios.tentativa_login
                WHERE conta_usuario_id = $1
                ORDER BY created_at DESC
                LIMIT $2
            """

            rows = await conn.fetch(query, conta_usuario_id, limit)
            return [dict(row) for row in rows]
        finally:
            await conn.close()

    @staticmethod
    async def get_failed_attempts_count(
        identifier: str, ip_address: Optional[str] = None, minutes: int = 30
    ) -> int:
        """
        Contar tentativas falhadas recentes

        Args:
            identifier: Username ou email
            ip_address: IP para filtrar (opcional)
            minutes: Janela de tempo em minutos

        Returns:
            Número de tentativas falhadas
        """
        conn = await get_postgres_connection()
        try:
            from datetime import timedelta

            time_threshold = datetime.utcnow() - timedelta(minutes=minutes)

            if ip_address:
                query = """
                    SELECT COUNT(*)
                    FROM usuarios.tentativa_login
                    WHERE (username = $1 OR email = $1)
                      AND ip_address = $2
                      AND sucesso = FALSE
                      AND created_at > $3
                """
                count = await conn.fetchval(
                    query, identifier, ip_address, time_threshold
                )
            else:
                query = """
                    SELECT COUNT(*)
                    FROM usuarios.tentativa_login
                    WHERE (username = $1 OR email = $1)
                      AND sucesso = FALSE
                      AND created_at > $2
                """
                count = await conn.fetchval(query, identifier, time_threshold)

            return count or 0
        finally:
            await conn.close()
