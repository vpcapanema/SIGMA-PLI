"""Utilitários de segurança para o módulo de autenticação (M01)."""

from passlib.context import CryptContext


_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Valida senha em texto plano contra o hash armazenado."""
    if not plain_password or not hashed_password:
        return False
    try:
        return _pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Retorna falso para qualquer erro na verificação (hash inválido etc.)
        return False


def hash_password(plain_password: str) -> str:
    """Gera hash bcrypt para novas senhas."""
    return _pwd_context.hash(plain_password)
