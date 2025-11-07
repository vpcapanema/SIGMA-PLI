"""
Serviço de gerenciamento de usuários para autenticação
Interage com PostgreSQL para CRUD de usuários
"""

from typing import Optional
from datetime import datetime
import uuid

from app.database import get_postgres_connection


class UserService:
    """Serviço para operações de usuário no banco de dados"""

    @staticmethod
    async def get_user_by_username(username: str) -> Optional[dict]:
        """
        Buscar usuário por username

        Args:
            username: Nome de usuário

        Returns:
            dict com dados do usuário ou None se não encontrado
        """
        conn = await get_postgres_connection()
        try:
            query = """
                SELECT
                    u.id as conta_id,
                    u.username,
                    u.email,
                    u.password_hash,
                    u.salt,
                    u.email_verificado,
                    u.dois_fatores_habilitado,
                    u.ativo,
                    u.bloqueado_ate,
                    u.tentativas_falha,
                    u.ultimo_login,
                    p.nome_completo,
                    COALESCE(p.nome_completo, '') as primeiro_nome,
                    COALESCE(p.nome_completo, '') as ultimo_nome,
                    p.telefone,
                    p.cpf
                FROM usuarios.usuario u
                LEFT JOIN cadastro.pessoa p ON u.pessoa_id = p.id
                WHERE u.username = $1
            """
            row = await conn.fetchrow(query, username)

            if row:
                return dict(row)
            return None
        finally:
            await conn.close()

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[dict]:
        """
        Buscar usuário por email

        Args:
            email: Email do usuário

        Returns:
            dict com dados do usuário ou None se não encontrado
        """
        conn = await get_postgres_connection()
        try:
            query = """
                SELECT
                    u.id as conta_id,
                    u.username,
                    u.email,
                    u.password_hash,
                    u.salt,
                    u.email_verificado,
                    u.dois_fatores_habilitado,
                    u.ativo,
                    u.bloqueado_ate,
                    u.tentativas_falha,
                    u.ultimo_login,
                    p.nome_completo,
                    COALESCE(p.nome_completo, '') as primeiro_nome,
                    COALESCE(p.nome_completo, '') as ultimo_nome,
                    p.telefone,
                    p.cpf
                FROM usuarios.usuario u
                LEFT JOIN cadastro.pessoa p ON u.pessoa_id = p.id
                WHERE u.email = $1
            """
            row = await conn.fetchrow(query, email)

            if row:
                return dict(row)
            return None
        finally:
            await conn.close()

    @staticmethod
    async def get_user_by_identifier(identifier: str) -> Optional[dict]:
        """
        Buscar usuário por username OU email

        Args:
            identifier: Username ou email

        Returns:
            dict com dados do usuário ou None se não encontrado
        """
        conn = await get_postgres_connection()
        try:
            query = """
                SELECT
                    u.id as conta_id,
                    u.username,
                    u.email,
                    u.password_hash,
                    u.salt,
                    u.email_verificado,
                    u.dois_fatores_habilitado,
                    u.ativo,
                    u.bloqueado_ate,
                    u.tentativas_falha,
                    u.ultimo_login,
                    p.nome_completo,
                    COALESCE(p.nome_completo, '') as primeiro_nome,
                    COALESCE(p.nome_completo, '') as ultimo_nome,
                    p.telefone,
                    p.cpf
                FROM usuarios.usuario u
                LEFT JOIN cadastro.pessoa p ON u.pessoa_id = p.id
                WHERE u.username = $1 OR u.email = $1
            """
            row = await conn.fetchrow(query, identifier)

            if row:
                return dict(row)
            return None
        finally:
            await conn.close()

    @staticmethod
    async def create_user(
        username: str,
        email: str,
        password_hash: str,
        salt: str,
        pessoa_id: Optional[uuid.UUID] = None,
        instituicao_id: Optional[uuid.UUID] = None,
        email_institucional: Optional[str] = None,
        telefone_institucional: Optional[str] = None,
        email_verificado: bool = False,
    ) -> uuid.UUID:
        """
        Criar novo usuário

        Args:
            username: Nome de usuário
            email: Email do usuário (para login)
            password_hash: Hash da senha
            salt: Salt usado no hash
            pessoa_id: ID da pessoa física associada
            instituicao_id: ID da instituição
            email_institucional: Email institucional
            telefone_institucional: Telefone institucional
            email_verificado: Se email já está verificado

        Returns:
            UUID do usuário criado
        """
        conn = await get_postgres_connection()
        try:
            query = """
                INSERT INTO usuarios.usuario
                (pessoa_id, instituicao_id, username, email,
                 password_hash, salt, email_institucional,
                 telefone_institucional, email_verificado)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                RETURNING id
            """
            user_id = await conn.fetchval(
                query,
                pessoa_id,
                instituicao_id,
                username,
                email,
                password_hash,
                salt,
                email_institucional,
                telefone_institucional,
                email_verificado,
            )
            return user_id
        finally:
            await conn.close()

    @staticmethod
    async def update_last_login(conta_id: uuid.UUID, ip_address: Optional[str] = None):
        """
        Atualizar último login e IP

        Args:
            conta_id: ID da conta do usuário
            ip_address: Endereço IP (opcional)
        """
        conn = await get_postgres_connection()
        try:
            query = """
                UPDATE usuarios.usuario
                SET ultimo_login = $1,
                    ultimo_ip = $2,
                    tentativas_falha = 0
                WHERE id = $3
            """
            await conn.execute(query, datetime.utcnow(), ip_address, conta_id)
        finally:
            await conn.close()

    @staticmethod
    async def increment_failed_attempts(conta_id: uuid.UUID):
        """
        Incrementar tentativas de login falhadas

        Args:
            conta_id: ID da conta do usuário
        """
        conn = await get_postgres_connection()
        try:
            query = """
                UPDATE usuarios.usuario
                SET tentativas_falha = tentativas_falha + 1,
                    atualizado_em = $1
                WHERE id = $2
                RETURNING tentativas_falha
            """
            attempts = await conn.fetchval(query, datetime.utcnow(), conta_id)

            # Bloquear conta após 5 tentativas
            if attempts >= 5:
                await UserService.lock_account(conta_id, minutes=30)

            return attempts
        finally:
            await conn.close()

    @staticmethod
    async def lock_account(conta_id: uuid.UUID, minutes: int = 30):
        """
        Bloquear conta temporariamente

        Args:
            conta_id: ID da conta do usuário
            minutes: Minutos de bloqueio
        """
        conn = await get_postgres_connection()
        try:
            query = """
                UPDATE usuarios.usuario
                SET bloqueado_ate = $1,
                    atualizado_em = $2
                WHERE id = $3
            """
            from datetime import timedelta

            bloqueado_ate = datetime.utcnow() + timedelta(minutes=minutes)

            await conn.execute(query, bloqueado_ate, datetime.utcnow(), conta_id)
        finally:
            await conn.close()

    @staticmethod
    async def is_account_locked(conta_id: uuid.UUID) -> bool:
        """
        Verificar se conta está bloqueada

        Args:
            conta_id: ID da conta do usuário

        Returns:
            True se conta está bloqueada, False caso contrário
        """
        conn = await get_postgres_connection()
        try:
            query = """
                SELECT bloqueado_ate
                FROM usuarios.usuario
                WHERE id = $1
            """
            bloqueado_ate = await conn.fetchval(query, conta_id)

            if bloqueado_ate and bloqueado_ate > datetime.utcnow():
                return True
            return False
        finally:
            await conn.close()

    @staticmethod
    async def verify_email(conta_id: uuid.UUID):
        """
        Marcar email como verificado

        Args:
            conta_id: ID da conta do usuário
        """
        conn = await get_postgres_connection()
        try:
            query = """
                UPDATE usuarios.usuario
                SET email_verificado = TRUE,
                    atualizado_em = $1
                WHERE id = $2
            """
            await conn.execute(query, datetime.utcnow(), conta_id)
        finally:
            await conn.close()

    @staticmethod
    async def update_password(conta_id: uuid.UUID, password_hash: str, salt: str):
        """
        Atualizar senha do usuário

        Args:
            conta_id: ID da conta do usuário
            password_hash: Novo hash da senha
            salt: Novo salt
        """
        conn = await get_postgres_connection()
        try:
            query = """
                UPDATE usuarios.usuario
                SET password_hash = $1,
                    salt = $2,
                    atualizado_em = $3,
                    tentativas_falha = 0,
                    bloqueado_ate = NULL
                WHERE id = $4
            """
            await conn.execute(query, password_hash, salt, datetime.utcnow(), conta_id)
        finally:
            await conn.close()
