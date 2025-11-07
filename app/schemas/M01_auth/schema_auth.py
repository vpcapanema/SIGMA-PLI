"""Esquemas Pydantic do módulo M01 Auth."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Payload para tentativa de login."""

    identifier: str = Field(..., description="Usuário ou e-mail institucional")
    password: str = Field(..., min_length=6, description="Senha do usuário")


class LoginResponse(BaseModel):
    """Resposta padrão para login bem-sucedido."""

    message: str
    redirect_url: str


class AuthenticatedUser(BaseModel):
    """Representação de usuário autenticado exposta ao front."""

    conta_id: str
    username: str
    nome_completo: str
    email: Optional[EmailStr] = None
    primeiro_nome: Optional[str] = None
    ultimo_nome: Optional[str] = None
    ultimo_login: Optional[datetime] = None


class SessionInfo(BaseModel):
    """Informações da sessão ativa."""

    session_id: str
    expires_at: datetime
