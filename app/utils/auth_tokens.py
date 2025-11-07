"""Utilitários para geração e validação de tokens JWT."""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict

from jose import JWTError, jwt

from app.config import settings


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def build_token(payload: Dict[str, Any], expires_hours: int) -> str:
    """Gera JWT utilizando configuração padrão do sistema."""

    expire = _now_utc() + timedelta(hours=expires_hours)
    to_encode = {**payload, "exp": expire, "iat": _now_utc()}
    return jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )


def decode_token(token: str) -> Dict[str, Any]:
    """Decodifica JWT e retorna seu payload."""

    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
    except JWTError as exc:
        raise ValueError("Token inválido ou expirado") from exc
