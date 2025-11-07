"""
Dependencies para autenticação
Dependency injection para validar sessões e proteger rotas
"""

from typing import Optional
from fastapi import Header, HTTPException, status

from app.services.M01_auth.service_auth import AuthService
from app.schemas.M01_auth.schema_auth import AuthenticatedUser


async def get_current_user_optional(
    authorization: Optional[str] = Header(None),
) -> Optional[AuthenticatedUser]:
    """
    Dependency para obter usuário atual (opcional)

    Args:
        authorization: Header Authorization com Bearer token

    Returns:
        AuthenticatedUser se autenticado, None caso contrário
    """
    if not authorization or not authorization.startswith("Bearer "):
        return None

    session_token = authorization.replace("Bearer ", "")

    try:
        user = await AuthService.get_current_user(session_token)
        return user
    except Exception:
        return None


async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> AuthenticatedUser:
    """
    Dependency para obter usuário atual (obrigatório)

    Args:
        authorization: Header Authorization com Bearer token

    Returns:
        AuthenticatedUser

    Raises:
        HTTPException 401 se não autenticado
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    session_token = authorization.replace("Bearer ", "")

    user = await AuthService.get_current_user(session_token)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida ou expirada",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_authenticated_user(
    current_user: AuthenticatedUser = None,
) -> AuthenticatedUser:
    """
    Dependency para exigir usuário autenticado

    Args:
        current_user: Usuário injetado

    Returns:
        AuthenticatedUser

    Raises:
        HTTPException 401 se não autenticado
    """
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Autenticação necessária",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return current_user
