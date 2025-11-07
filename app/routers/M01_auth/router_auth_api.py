"""
Router de autenticação - Endpoints de login, logout, registro
"""

import secrets
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Header
from pydantic import BaseModel, EmailStr, Field, AliasChoices
from app.utils.normalizers import normalize_usuario_payload

from app.services.M01_auth.service_auth import AuthService
from app.services.M01_auth.service_auth_user import UserService
from app.services.M01_auth import service_auth_tokens
from app.schemas.M01_auth.schema_auth import AuthenticatedUser
from app.database import get_postgres_connection


router = APIRouter(prefix="/api/v1/auth", tags=["Autenticação"])


# Schemas de request/response
class LoginRequest(BaseModel):
    """Request de login"""

    identifier: str  # username ou email
    password: str


class LoginResponse(BaseModel):
    """Response de login bem-sucedido"""

    success: bool
    message: str
    user: AuthenticatedUser
    session_token: str
    refresh_token: str


class RegisterRequest(BaseModel):
    """Request de registro de novo usuário"""

    # IDs de vinculação
    # Aceita aliases: pessoa_id -> pessoa_fisica_id
    pessoa_fisica_id: str = Field(
        validation_alias=AliasChoices("pessoa_fisica_id", "pessoa_id")
    )
    instituicao_id: str

    # Dados profissionais
    # Aceita alias: email -> email_institucional
    email_institucional: EmailStr = Field(
        validation_alias=AliasChoices("email_institucional", "email")
    )
    telefone_institucional: Optional[str] = None

    # Dados de acesso
    tipo_usuario: str  # ADMIN, GESTOR, ANALISTA, OPERADOR, VISUALIZADOR
    username: str
    # Aceita alias: password -> senha
    senha: str = Field(validation_alias=AliasChoices("senha", "password"))

    # Termos
    termo_privacidade: bool
    termo_uso: bool


class RegisterResponse(BaseModel):
    """Response de registro"""

    success: bool
    message: str


class RefreshRequest(BaseModel):
    """Request de refresh de sessão"""

    refresh_token: str


class RefreshResponse(BaseModel):
    """Response de refresh"""

    success: bool
    session_token: str
    refresh_token: str


class PasswordResetRequest(BaseModel):
    """Request de solicitação de reset de senha"""

    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Request de confirmação de reset de senha"""

    token: str
    new_password: str


class MessageResponse(BaseModel):
    """Response genérica com mensagem"""

    success: bool
    message: str


# Endpoints
@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    x_forwarded_for: Optional[str] = Header(None),
    user_agent: Optional[str] = Header(None),
):
    """
    Endpoint de login

    Args:
        request: Dados de login (username/email + senha)
        x_forwarded_for: IP do cliente (para auditoria)
        user_agent: User agent do navegador

    Returns:
        LoginResponse com token de sessão e dados do usuário
    """
    # Tentar autenticar
    result = await AuthService.authenticate(
        identifier=request.identifier,
        password=request.password,
        ip_address=x_forwarded_for,
        user_agent=user_agent,
    )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas ou conta bloqueada",
        )

    user, session_token, refresh_token = result

    return LoginResponse(
        success=True,
        message="Login realizado com sucesso",
        user=user,
        session_token=session_token,
        refresh_token=refresh_token,
    )


@router.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """
    Endpoint de logout

    Args:
        authorization: Header com token de sessão (formato: "Bearer <token>")

    Returns:
        Confirmação de logout
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de sessão não fornecido",
        )

    session_token = authorization.replace("Bearer ", "")

    await AuthService.logout(session_token)

    return {"success": True, "message": "Logout realizado com sucesso"}


@router.get("/me", response_model=AuthenticatedUser)
async def get_current_user(authorization: Optional[str] = Header(None)):
    """
    Obter dados do usuário autenticado

    Args:
        authorization: Header com token de sessão (formato: "Bearer <token>")

    Returns:
        Dados do usuário autenticado
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de sessão não fornecido",
        )

    session_token = authorization.replace("Bearer ", "")

    user = await AuthService.get_current_user(session_token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida ou expirada",
        )

    return user


@router.post("/register", response_model=RegisterResponse)
async def register(request: RegisterRequest):
    """
    Endpoint de registro de novo usuário completo

    Args:
        request: Dados completos de registro incluindo:
            - pessoa_fisica_id: ID da pessoa física
            - pessoa_juridica_id: ID da instituição
            - dados profissionais (cargo, email institucional, etc)
            - dados de acesso (tipo_usuario, username, senha)
            - aceite de termos

    Returns:
        Confirmação de registro
    """
    # Normalizar payload recebido (aceita aliases)
    raw = request.model_dump(exclude_none=True)
    norm = normalize_usuario_payload(raw)

    # Validar presença explícita dos IDs obrigatórios
    if not norm.get("pessoa_id") or not norm.get("instituicao_id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Campos obrigatórios ausentes: pessoa_fisica_id e instituicao_id "
                "devem ser informados."
            ),
        )

    # Validar termos
    if not request.termo_privacidade or not request.termo_uso:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="É necessário aceitar os termos de uso e política de privacidade",
        )

    # Validar tipo de usuário
    tipos_validos = ["ADMIN", "GESTOR", "ANALISTA", "OPERADOR", "VISUALIZADOR"]
    if norm.get("tipo_usuario") not in tipos_validos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Tipo de usuário inválido. Valores aceitos: {', '.join(tipos_validos)}",
        )

    try:
        success, message = await AuthService.register_user(
            username=norm["username"],
            senha=norm["senha"],
            pessoa_id=norm["pessoa_id"],
            instituicao_id=norm["instituicao_id"],
            tipo_usuario=norm["tipo_usuario"],
            email_institucional=norm["email_institucional"],
            telefone_institucional=norm.get("telefone_institucional"),
        )

        if not success:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

        return RegisterResponse(success=True, message=message)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro ao registrar usuário: {str(e)}",
        )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_session(request: RefreshRequest):
    """
    Renovar sessão usando refresh token

    Args:
        request: Refresh token

    Returns:
        Novos tokens de sessão
    """
    result = await AuthService.refresh_session(request.refresh_token)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido ou expirado",
        )

    new_session_token, new_refresh_token = result

    return RefreshResponse(
        success=True, session_token=new_session_token, refresh_token=new_refresh_token
    )


@router.post("/request-password-reset", response_model=MessageResponse)
async def request_password_reset(request: PasswordResetRequest):
    """
    Solicitar reset de senha

    Args:
        request: Email do usuário

    Returns:
        Confirmação de envio (sempre retorna sucesso para não vazar informação)
    """
    # Buscar usuário por email
    user_data = await UserService.get_user_by_email(request.email)

    if user_data:
        conta_id = user_data["conta_id"]

        # Gerar token seguro
        token = secrets.token_urlsafe(32)

        # Salvar token no banco
        conn = await get_postgres_connection()
        try:
            # Invalidar tokens anteriores
            await service_auth_tokens.invalidate_previous_tokens(
                conn, conta_id, "password_reset"
            )

            # Criar novo token (expira em 2 horas)
            await service_auth_tokens.create_recovery_token(
                conn, conta_id, token, expires_hours=2
            )
        finally:
            await conn.close()

        # TODO: Enviar email com link de reset
        # O link seria: https://seu-dominio.com/auth/reset-password?token={token}
        print(f"🔑 Token de recuperação: {token}")
        print(f"📧 Email: {request.email}")

    # SEMPRE retorna sucesso para não vazar se email existe
    return MessageResponse(
        success=True,
        message="Se o email estiver cadastrado, você receberá as instruções de recuperação",
    )


# Alias para compatibilidade com rota antiga
@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password_alias(request: PasswordResetRequest):
    """Compat: encaminha para /request-password-reset."""
    return await request_password_reset(request)


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(request: PasswordResetConfirm):
    """
    Confirmar reset de senha

    Args:
        request: Token e nova senha

    Returns:
        Confirmação de reset
    """
    conn = await get_postgres_connection()
    try:
        # Validar token
        token_data = await service_auth_tokens.fetch_valid_recovery_token(
            conn, request.token
        )

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token inválido, expirado ou já utilizado",
            )

        conta_id = token_data["conta_usuario_id"]

        # Hash da nova senha
        password_hash, salt = AuthService.hash_password(request.new_password)

        # Atualizar senha
        await UserService.update_password(conta_id, password_hash, salt)

        # Marcar token como usado
        await service_auth_tokens.mark_token_used(conn, token_data["id"])

        return MessageResponse(success=True, message="Senha alterada com sucesso")
    finally:
        await conn.close()


@router.get("/verify-email", response_model=MessageResponse)
async def verify_email(token: str):
    """
    Verificar email do usuário

    Args:
        token: Token de verificação

    Returns:
        Confirmação de verificação
    """
    conn = await get_postgres_connection()
    try:
        # Validar token
        token_data = await service_auth_tokens.fetch_valid_verification_token(
            conn, token
        )

        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Token de verificação inválido, expirado ou já utilizado",
            )

        conta_id = token_data["conta_usuario_id"]

        # Marcar email como verificado
        await UserService.verify_email(conta_id)

        # Marcar token como usado
        await service_auth_tokens.mark_token_used(conn, token_data["id"])

        return MessageResponse(
            success=True,
            message="Email verificado com sucesso! Você já pode fazer login.",
        )
    finally:
        await conn.close()
