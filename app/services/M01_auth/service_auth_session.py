"""
Serviço de gerenciamento de sessões
Interage com PostgreSQL para CRUD de sessões de usuário
"""

from typing import Optional
from datetime import datetime, timedelta
import uuid
import secrets

from app.database import get_postgres_connection


class SessionService:
    """Serviço para operações de sessão no banco de dados"""

    @staticmethod
    async def create_session(
        conta_usuario_id: uuid.UUID,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        expires_in_hours: int = 24,
    ) -> tuple[str, str]:
        """
        Criar nova sessão para usuário

        Args:
            conta_usuario_id: ID da conta do usuário
            ip_address: Endereço IP (opcional)
            user_agent: User agent do navegador (opcional)
            expires_in_hours: Horas até expiração (padrão 24h)

        Returns:
            tuple (session_token, refresh_token)
        """
        conn = await get_postgres_connection()
        try:
            # Gerar tokens seguros
            session_token = secrets.token_urlsafe(32)
            refresh_token = secrets.token_urlsafe(32)

            # Calcular expiração
            expires_at = datetime.utcnow() + timedelta(hours=expires_in_hours)

            query = """
                INSERT INTO usuarios.sessao 
                (conta_usuario_id, token, refresh_token, ip_address, user_agent, expires_at)
                VALUES ($1, $2, $3, $4, $5, $6)
                RETURNING id
            """

            await conn.execute(
                query,
                conta_usuario_id,
                session_token,
                refresh_token,
                ip_address,
                user_agent,
                expires_at,
            )

            return session_token, refresh_token
        finally:
            await conn.close()

    @staticmethod
    async def get_session_by_token(token: str) -> Optional[dict]:
        """
        Buscar sessão por token

        Args:
            token: Token da sessão

        Returns:
            dict com dados da sessão ou None se não encontrada/expirada
        """
        conn = await get_postgres_connection()
        try:
            query = """
                SELECT 
                    s.id as session_id,
                    s.conta_usuario_id,
                    s.token,
                    s.refresh_token,
                    s.ip_address,
                    s.user_agent,
                    s.expires_at,
                    s.created_at,
                    s.revoked,
                    cu.username,
                    cu.email,
                    p.nome_completo,
                    COALESCE(p.nome_completo, '') AS primeiro_nome,
                    COALESCE(p.nome_completo, '') AS ultimo_nome
                FROM usuarios.sessao s
                JOIN usuarios.usuario cu ON s.conta_usuario_id = cu.id
                LEFT JOIN cadastro.pessoa p ON cu.pessoa_id = p.id
                WHERE s.token = $1 
                  AND s.revoked = FALSE
                  AND s.expires_at > $2
            """

            row = await conn.fetchrow(query, token, datetime.utcnow())

            if row:
                return dict(row)
            return None
        finally:
            await conn.close()

    @staticmethod
    async def get_session_by_refresh_token(refresh_token: str) -> Optional[dict]:
        """
        Buscar sessão por refresh token

        Args:
            refresh_token: Refresh token da sessão

        Returns:
            dict com dados da sessão ou None se não encontrada
        """
        conn = await get_postgres_connection()
        try:
            query = """
                SELECT 
                    s.id as session_id,
                    s.conta_usuario_id,
                    s.token,
                    s.refresh_token,
                    s.expires_at,
                    s.revoked
                FROM usuarios.sessao s
                WHERE s.refresh_token = $1
                  AND s.revoked = FALSE
            """

            row = await conn.fetchrow(query, refresh_token)

            if row:
                return dict(row)
            return None
        finally:
            await conn.close()

    @staticmethod
    async def revoke_session(token: str):
        """
        Revogar sessão (logout)

        Args:
            token: Token da sessão a ser revogada
        """
        conn = await get_postgres_connection()
        try:
            query = """
                UPDATE usuarios.sessao
                SET revoked = TRUE,
                    revoked_at = $1
                WHERE token = $2
            """
            await conn.execute(query, datetime.utcnow(), token)
        finally:
            await conn.close()

    @staticmethod
    async def revoke_all_user_sessions(conta_usuario_id: uuid.UUID):
        """
        Revogar todas as sessões de um usuário

        Args:
            conta_usuario_id: ID da conta do usuário
        """
        conn = await get_postgres_connection()
        try:
            query = """
                UPDATE usuarios.sessao
                SET revoked = TRUE,
                    revoked_at = $1
                WHERE conta_usuario_id = $2
                  AND revoked = FALSE
            """
            await conn.execute(query, datetime.utcnow(), conta_usuario_id)
        finally:
            await conn.close()

    @staticmethod
    async def refresh_session(
        refresh_token: str, expires_in_hours: int = 24
    ) -> Optional[tuple[str, str]]:
        """
        Renovar sessão usando refresh token

        Args:
            refresh_token: Refresh token da sessão atual
            expires_in_hours: Horas até expiração da nova sessão

        Returns:
            tuple (new_session_token, new_refresh_token) ou None se refresh token inválido
        """
        # Verificar refresh token
        session = await SessionService.get_session_by_refresh_token(refresh_token)

        if not session:
            return None

        # Revogar sessão antiga
        await SessionService.revoke_session(session["token"])

        # Criar nova sessão
        new_token, new_refresh = await SessionService.create_session(
            session["conta_usuario_id"], expires_in_hours=expires_in_hours
        )

        return new_token, new_refresh

    @staticmethod
    async def get_active_sessions(conta_usuario_id: uuid.UUID) -> list[dict]:
        """
        Listar sessões ativas de um usuário

        Args:
            conta_usuario_id: ID da conta do usuário

        Returns:
            Lista de dicts com dados das sessões ativas
        """
        conn = await get_postgres_connection()
        try:
            query = """
                SELECT 
                    id as session_id,
                    ip_address,
                    user_agent,
                    created_at,
                    expires_at
                FROM usuarios.sessao
                WHERE conta_usuario_id = $1
                  AND revoked = FALSE
                  AND expires_at > $2
                ORDER BY created_at DESC
            """

            rows = await conn.fetch(query, conta_usuario_id, datetime.utcnow())
            return [dict(row) for row in rows]
        finally:
            await conn.close()

    @staticmethod
    async def cleanup_expired_sessions():
        """
        Limpar sessões expiradas (tarefa de manutenção)

        Returns:
            Número de sessões limpas
        """
        conn = await get_postgres_connection()
        try:
            query = """
                UPDATE usuarios.sessao
                SET revoked = TRUE,
                    revoked_at = $1
                WHERE expires_at < $1
                  AND revoked = FALSE
                RETURNING id
            """

            result = await conn.fetch(query, datetime.utcnow())
            return len(result)
        finally:
            await conn.close()
