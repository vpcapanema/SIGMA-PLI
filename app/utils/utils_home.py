"""
SIGMA-PLI - M00: Home - Utils
Utilitários e helpers para o módulo Home
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from email_validator import validate_email, EmailNotValidError
import hashlib
import secrets
import string

class ValidationUtils:
    """Utilitários de validação"""

    @staticmethod
    def validate_email_format(email: str) -> Tuple[bool, str]:
        """Valida formato de email"""
        try:
            validate_email(email, check_deliverability=False)
            return True, "Email válido"
        except EmailNotValidError as e:
            return False, str(e)

    @staticmethod
    def validate_name(name: str) -> Tuple[bool, str]:
        """Valida nome"""
        if not name or not name.strip():
            return False, "Nome é obrigatório"

        if len(name.strip()) < 2:
            return False, "Nome deve ter pelo menos 2 caracteres"

        if not re.match(r"^[a-zA-ZÀ-ÿ\s]+$", name.strip()):
            return False, "Nome deve conter apenas letras e espaços"

        return True, "Nome válido"

    @staticmethod
    def validate_message(message: str) -> Tuple[bool, str]:
        """Valida mensagem"""
        if not message or not message.strip():
            return False, "Mensagem é obrigatória"

        if len(message.strip()) < 10:
            return False, "Mensagem deve ter pelo menos 10 caracteres"

        if len(message.strip()) > 1000:
            return False, "Mensagem deve ter no máximo 1000 caracteres"

        return True, "Mensagem válida"

    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitiza entrada de texto"""
        if not text:
            return ""

        # Remove tags HTML
        text = re.sub(r'<[^>]+>', '', text)

        # Remove caracteres de controle
        text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)

        # Limita comprimento
        return text.strip()[:1000]

class FormatUtils:
    """Utilitários de formatação"""

    @staticmethod
    def format_uptime(seconds: float) -> str:
        """Formata uptime em formato legível"""
        days, remainder = divmod(int(seconds), 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)

        parts = []
        if days > 0:
            parts.append(f"{days}d")
        if hours > 0:
            parts.append(f"{hours}h")
        if minutes > 0:
            parts.append(f"{minutes}m")
        if seconds > 0 and not parts:
            parts.append(f"{seconds}s")

        return " ".join(parts) if parts else "0s"

    @staticmethod
    def format_file_size(bytes_size: int) -> str:
        """Formata tamanho de arquivo"""
        if bytes_size == 0:
            return "0 B"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"

    @staticmethod
    def format_timestamp(dt: datetime) -> str:
        """Formata timestamp para exibição"""
        now = datetime.now()
        diff = now - dt

        if diff.days == 0:
            if diff.seconds < 60:
                return "agora mesmo"
            elif diff.seconds < 3600:
                minutes = diff.seconds // 60
                return f"{minutes} min atrás"
            else:
                hours = diff.seconds // 3600
                return f"{hours} h atrás"
        elif diff.days == 1:
            return "ontem"
        elif diff.days < 7:
            return f"{diff.days} dias atrás"
        else:
            return dt.strftime("%d/%m/%Y")

class SecurityUtils:
    """Utilitários de segurança"""

    @staticmethod
    def generate_csrf_token() -> str:
        """Gera token CSRF"""
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_string(text: str) -> str:
        """Gera hash SHA-256 de uma string"""
        return hashlib.sha256(text.encode()).hexdigest()

    @staticmethod
    def generate_random_string(length: int = 32) -> str:
        """Gera string aleatória"""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitiza nome de arquivo"""
        # Remove caracteres perigosos
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)

        # Remove caracteres de controle
        filename = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', filename)

        # Remove palavras perigosas (case insensitive)
        dangerous_words = ['script', 'javascript', 'vbscript', 'onload', 'onerror', 'eval', 'exec']
        for word in dangerous_words:
            filename = re.sub(re.escape(word), '', filename, flags=re.IGNORECASE)

        # Remove sequências de pontos (path traversal)
        filename = re.sub(r'\.\.+', '', filename)

        # Limita comprimento
        return filename[:255].strip()

class DataUtils:
    """Utilitários de manipulação de dados"""

    @staticmethod
    def deep_merge(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
        """Faz merge profundo de dicionários"""
        result = dict1.copy()

        for key, value in dict2.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = DataUtils.deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    @staticmethod
    def flatten_dict(d: Dict[str, Any], prefix: str = '') -> Dict[str, Any]:
        """Achata dicionário aninhado"""
        items = []

        for k, v in d.items():
            new_key = f"{prefix}.{k}" if prefix else k

            if isinstance(v, dict):
                items.extend(DataUtils.flatten_dict(v, new_key).items())
            else:
                items.append((new_key, v))

        return dict(items)

    @staticmethod
    def group_by_key(data: List[Dict[str, Any]], key: str) -> Dict[str, List[Dict[str, Any]]]:
        """Agrupa lista de dicionários por chave"""
        grouped = {}

        for item in data:
            group_key = item.get(key)
            if group_key not in grouped:
                grouped[group_key] = []
            grouped[group_key].append(item)

        return grouped

class UIUtils:
    """Utilitários para interface"""

    @staticmethod
    def get_status_color(status: str) -> str:
        """Retorna cor CSS baseada no status"""
        colors = {
            "operational": "#28a745",
            "healthy": "#28a745",
            "degraded": "#ffc107",
            "unhealthy": "#dc3545",
            "error": "#dc3545",
            "warning": "#ffc107",
            "info": "#17a2b8",
            "maintenance": "#6c757d"
        }
        return colors.get(status.lower(), "#6c757d")

    @staticmethod
    def get_status_icon(status: str) -> str:
        """Retorna ícone baseado no status"""
        icons = {
            "operational": "✅",
            "healthy": "✅",
            "degraded": "⚠️",
            "unhealthy": "❌",
            "error": "❌",
            "warning": "⚠️",
            "info": "ℹ️",
            "maintenance": "🔧"
        }
        return icons.get(status.lower(), "❓")

    @staticmethod
    def truncate_text(text: str, max_length: int = 100) -> str:
        """Trunca texto com reticências"""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."

class CacheUtils:
    """Utilitários de cache"""

    _cache = {}

    @staticmethod
    def set_cache(key: str, value: Any, ttl: int = 300) -> None:
        """Define valor no cache com TTL"""
        CacheUtils._cache[key] = {
            "value": value,
            "expires": datetime.now() + timedelta(seconds=ttl)
        }

    @staticmethod
    def get_cache(key: str) -> Optional[Any]:
        """Obtém valor do cache se ainda válido"""
        if key not in CacheUtils._cache:
            return None

        item = CacheUtils._cache[key]
        if datetime.now() > item["expires"]:
            del CacheUtils._cache[key]
            return None

        return item["value"]

    @staticmethod
    def clear_cache(key: Optional[str] = None) -> None:
        """Limpa cache (chave específica ou todo)"""
        if key:
            CacheUtils._cache.pop(key, None)
        else:
            CacheUtils._cache.clear()

class LogUtils:
    """Utilitários de logging"""

    @staticmethod
    def format_log_message(level: str, message: str, module: str = "M00_home") -> str:
        """Formata mensagem de log"""
        timestamp = datetime.now().isoformat()
        return f"[{timestamp}] {level.upper()} [{module}] {message}"

    @staticmethod
    def log_error(message: str, error: Exception = None, module: str = "M00_home") -> None:
        """Log de erro"""
        error_msg = LogUtils.format_log_message("ERROR", message, module)
        print(error_msg)
        if error:
            print(f"Exception: {str(error)}")

    @staticmethod
    def log_warning(message: str, module: str = "M00_home") -> None:
        """Log de aviso"""
        warning_msg = LogUtils.format_log_message("WARNING", message, module)
        print(warning_msg)

    @staticmethod
    def log_info(message: str, module: str = "M00_home") -> None:
        """Log informativo"""
        info_msg = LogUtils.format_log_message("INFO", message, module)
        print(info_msg)