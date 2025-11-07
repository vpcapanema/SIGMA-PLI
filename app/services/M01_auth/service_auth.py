"""
Serviço principal de autenticação
Orquestra login, logout e verificação de sessão
"""

import hashlib
import secrets
from typing import Optional

from app.services.M01_auth.service_auth_user import UserService
from app.services.M01_auth.service_auth_session import SessionService
from app.services.M01_auth.service_auth_audit import LoginAuditService
from app.services.M01_auth.service_email import EmailService
from app.services.M01_auth.service_pessoa import PessoaService
from app.schemas.M01_auth.schema_auth import AuthenticatedUser


class AuthService:
    """Serviço principal de autenticação"""

    @staticmethod
    def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
        """
        Hash de senha usando PBKDF2

        Args:
            password: Senha em texto plano
            salt: Salt (gerado se não fornecido)

        Returns:
            tuple (password_hash, salt)
        """
        if not salt:
            salt = secrets.token_hex(16)

        # PBKDF2 com SHA256
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100000,  # iterações
        ).hex()

        return password_hash, salt

    @staticmethod
    def verify_password(password: str, password_hash: str, salt: str) -> bool:
        """
        Verificar se senha está correta

        Args:
            password: Senha em texto plano
            password_hash: Hash armazenado
            salt: Salt usado no hash

        Returns:
            True se senha correta, False caso contrário
        """
        computed_hash, _ = AuthService.hash_password(password, salt)
        return computed_hash == password_hash

    @staticmethod
    async def authenticate(
        identifier: str,
        password: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Optional[tuple[AuthenticatedUser, str, str]]:
        """
        Autenticar usuário

        Args:
            identifier: Username ou email
            password: Senha
            ip_address: IP do cliente
            user_agent: User agent do navegador

        Returns:
            tuple (AuthenticatedUser, session_token, refresh_token) ou None se falhar
        """
        # Buscar usuário
        user_data = await UserService.get_user_by_identifier(identifier)

        if not user_data:
            # Registrar tentativa falhada
            await LoginAuditService.log_login_attempt(
                username=identifier,
                ip_address=ip_address,
                user_agent=user_agent,
                sucesso=False,
                motivo_falha="Usuário não encontrado",
            )
            return None

        conta_id = user_data["conta_id"]

        # Verificar se conta está ativa
        if not user_data.get("ativo", True):
            await LoginAuditService.log_login_attempt(
                username=identifier,
                ip_address=ip_address,
                user_agent=user_agent,
                sucesso=False,
                motivo_falha="Conta desativada",
                conta_usuario_id=conta_id,
            )
            return None

        # Verificar se conta está bloqueada
        if await UserService.is_account_locked(conta_id):
            await LoginAuditService.log_login_attempt(
                username=identifier,
                ip_address=ip_address,
                user_agent=user_agent,
                sucesso=False,
                motivo_falha="Conta temporariamente bloqueada",
                conta_usuario_id=conta_id,
            )
            return None

        # Verificar senha
        if not AuthService.verify_password(
            password, user_data["password_hash"], user_data["salt"]
        ):
            # Incrementar tentativas falhadas
            await UserService.increment_failed_attempts(conta_id)

            # Registrar tentativa falhada
            await LoginAuditService.log_login_attempt(
                username=identifier,
                ip_address=ip_address,
                user_agent=user_agent,
                sucesso=False,
                motivo_falha="Senha incorreta",
                conta_usuario_id=conta_id,
            )
            return None

        # Login bem-sucedido!

        # Atualizar último login
        await UserService.update_last_login(conta_id, ip_address)

        # Criar sessão
        session_token, refresh_token = await SessionService.create_session(
            conta_id, ip_address=ip_address, user_agent=user_agent, expires_in_hours=24
        )

        # Registrar tentativa bem-sucedida
        await LoginAuditService.log_login_attempt(
            username=identifier,
            ip_address=ip_address,
            user_agent=user_agent,
            sucesso=True,
            conta_usuario_id=conta_id,
        )

        # Criar objeto AuthenticatedUser
        authenticated_user = AuthenticatedUser(
            conta_id=str(conta_id),
            username=user_data["username"],
            nome_completo=user_data.get("nome_completo", ""),
            email=user_data.get("email"),
            primeiro_nome=user_data.get("primeiro_nome"),
            ultimo_nome=user_data.get("ultimo_nome"),
            ultimo_login=user_data.get("ultimo_login"),
        )

        return authenticated_user, session_token, refresh_token

    @staticmethod
    async def logout(session_token: str):
        """
        Fazer logout (revogar sessão)

        Args:
            session_token: Token da sessão
        """
        await SessionService.revoke_session(session_token)

    @staticmethod
    async def get_current_user(session_token: str) -> Optional[AuthenticatedUser]:
        """
        Obter usuário atual pela sessão

        Args:
            session_token: Token da sessão

        Returns:
            AuthenticatedUser ou None se sessão inválida
        """
        session = await SessionService.get_session_by_token(session_token)

        if not session:
            return None

        # Criar objeto AuthenticatedUser
        authenticated_user = AuthenticatedUser(
            conta_id=str(session["conta_usuario_id"]),
            username=session["username"],
            nome_completo=session.get("nome_completo", ""),
            email=session.get("email"),
            primeiro_nome=session.get("primeiro_nome"),
            ultimo_nome=session.get("ultimo_nome"),
            ultimo_login=None,  # Não temos essa info na query de sessão
        )

        return authenticated_user

    @staticmethod
    async def refresh_session(refresh_token: str) -> Optional[tuple[str, str]]:
        """
        Renovar sessão

        Args:
            refresh_token: Refresh token

        Returns:
            tuple (new_session_token, new_refresh_token) ou None se inválido
        """
        return await SessionService.refresh_session(refresh_token)

    @staticmethod
    async def register_user(
        username: str,
        senha: str,
        pessoa_id: str,
        instituicao_id: str,
        tipo_usuario: str,
        email_institucional: str,
        telefone_institucional: Optional[str] = None,
    ) -> tuple[bool, str]:
        """
        Registrar novo usuário

        Args:
            username: Nome de usuário
            senha: Senha
            pessoa_fisica_id: ID da pessoa física
            instituicao_id: ID da instituição
            tipo_usuario: Tipo do usuário (ex: GESTOR_MUNICIPAL, ANALISTA_SEMA, etc.)
            email_institucional: Email institucional
            telefone_institucional: Telefone institucional (opcional)

        Returns:
            tuple (sucesso: bool, mensagem: str)
        """
        # Verificar se username já existe
        existing_user = await UserService.get_user_by_username(username)
        if existing_user:
            return False, "Nome de usuário já existe"

        # Verificar se email já existe
        existing_email = await UserService.get_user_by_email(email_institucional)
        if existing_email:
            return False, "Email já cadastrado"

        # Hash da senha
        password_hash, salt = AuthService.hash_password(senha)

        # Criar usuário
        try:
            import uuid

            pessoa_uuid = uuid.UUID(pessoa_id)
            instituicao_uuid = uuid.UUID(instituicao_id)

            # Buscar dados da pessoa física e instituição para o email
            pessoa = await PessoaService.get_pessoa_by_cpf("")  # TODO: buscar por ID
            instituicao = await PessoaService.get_pessoa_by_cnpj(
                ""
            )  # TODO: buscar por ID

            user_id = await UserService.create_user(
                username=username,
                email=email_institucional,
                password_hash=password_hash,
                salt=salt,
                pessoa_id=pessoa_uuid,
                instituicao_id=instituicao_uuid,
                email_institucional=email_institucional,
                telefone_institucional=telefone_institucional,
                email_verificado=False,
            )

            # Preparar dados do usuário para email
            usuario_email = {
                "id": str(user_id),
                "nome_completo": pessoa.get("nome_completo", "") if pessoa else "",
                "email": pessoa.get("email", "") if pessoa else "",
                "telefone": pessoa.get("telefone", "") if pessoa else "",
                "cpf": pessoa.get("cpf", "") if pessoa else "",
                "instituicao": (
                    instituicao.get("razao_social", "") if instituicao else ""
                ),
                "email_institucional": email_institucional,
                "telefone_institucional": telefone_institucional or "",
                "tipo_usuario": tipo_usuario,
                "username": username,
            }

            # Enviar emails (não bloqueia se falhar)
            try:
                await EmailService.enviar_confirmacao_solicitacao(usuario_email)
                await EmailService.notificar_administradores(usuario_email)
            except Exception as email_error:
                print(f"[AuthService] Aviso: Erro ao enviar emails: {email_error}")

            return True, f"Usuário criado com sucesso. ID: {user_id}"
        except Exception as e:
            return False, f"Erro ao criar usuário: {str(e)}"
