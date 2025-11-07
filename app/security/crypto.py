"""
SIGMA-PLI - Gerenciador de Criptografia
Envelope Encryption para dados sensíveis (CPF, Telefone, CNPJ)
"""

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import hashlib
import base64
import os
from typing import Tuple


class CryptographyManager:
    """
    Gerencia criptografia de dados sensíveis com envelope encryption.

    Padrão: Fernet (AES 128 em modo CBC)
    Hash: SHA256 para buscas sem descriptografar
    """

    def __init__(self, master_key: str = None):
        """
        Inicializa com chave mestra.

        Args:
            master_key: Chave mestra (sensível). Se None, tenta carregar de env.
        """
        if master_key is None:
            master_key = os.getenv("MASTER_KEY", "")
            if not master_key:
                raise ValueError(
                    "MASTER_KEY não configurada. "
                    "Configure em .env ou passe como argumento."
                )

        self.master_key = master_key

    def _derive_key(self) -> bytes:
        """Deriva chave criptográfica da chave mestra usando PBKDF2"""
        salt = b"sigma-pli-2025"  # Salt fixo (em produção, considerar rotação)
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        return key

    def encrypt(self, data: str) -> str:
        """
        Criptografa dados sensíveis.

        Args:
            data: Dados a criptografar (ex: "12345678900")

        Returns:
            Dados criptografados em base64
        """
        try:
            key = self._derive_key()
            cipher = Fernet(key)
            encrypted = cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            raise ValueError(f"Erro ao criptografar: {e}")

    def decrypt(self, encrypted_data: str) -> str:
        """
        Descriptografa dados sensíveis.

        ⚠️ USE COM CAUTELA - Apenas quando necessário (auditoria, exclusão, etc)

        Args:
            encrypted_data: Dados criptografados

        Returns:
            Dados descriptografados
        """
        try:
            key = self._derive_key()
            cipher = Fernet(key)
            decrypted = cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            raise ValueError(f"Erro ao descriptografar: {e}")

    def hash_data(self, data: str) -> str:
        """
        Gera hash SHA256 para buscas rápidas sem descriptografar.

        Args:
            data: Dados a fazer hash (ex: CPF)

        Returns:
            Hash SHA256 em hexadecimal
        """
        return hashlib.sha256(data.encode()).hexdigest()

    def encrypt_and_hash(self, data: str) -> Tuple[str, str]:
        """
        Criptografa dados e gera hash simultaneamente.

        Args:
            data: Dados sensíveis

        Returns:
            Tupla (dados_criptografados, hash)
        """
        encrypted = self.encrypt(data)
        hash_value = self.hash_data(data)
        return encrypted, hash_value

    def verify_hash(self, data: str, hash_value: str) -> bool:
        """
        Verifica se dados correspondem ao hash sem descriptografar.

        Args:
            data: Dados a verificar
            hash_value: Hash para comparação

        Returns:
            True se dados correspondem ao hash
        """
        return self.hash_data(data) == hash_value


# Instância global (será inicializada na startup da app)
_crypto_manager = None


def get_crypto_manager() -> CryptographyManager:
    """Obter instância do gerenciador de criptografia"""
    global _crypto_manager
    if _crypto_manager is None:
        _crypto_manager = CryptographyManager()
    return _crypto_manager


def init_crypto_manager(master_key: str = None):
    """Inicializar gerenciador de criptografia na startup"""
    global _crypto_manager
    _crypto_manager = CryptographyManager(master_key)
