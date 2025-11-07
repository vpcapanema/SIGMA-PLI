"""
SIGMA-PLI - M00: Home - Tests
Testes unitários e de integração para o módulo Home
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
import asyncio

# Importações dos módulos a serem testados
from app.services.service_home import HomeService, ContactService, SystemMonitorService
from app.utils.utils_home import ValidationUtils, FormatUtils, SecurityUtils, DataUtils, UIUtils

class TestValidationUtils:
    """Testes para ValidationUtils"""

    def test_validate_email_format_valid(self):
        """Testa validação de email válido"""
        valid, message = ValidationUtils.validate_email_format("test@example.com")
        assert valid is True
        assert message == "Email válido"

    def test_validate_email_format_invalid(self):
        """Testa validação de email inválido"""
        valid, message = ValidationUtils.validate_email_format("invalid-email")
        assert valid is False
        assert "must have an @-sign" in message or "Email inválido" in message

    def test_validate_name_valid(self):
        """Testa validação de nome válido"""
        valid, message = ValidationUtils.validate_name("João Silva")
        assert valid is True
        assert message == "Nome válido"

    def test_validate_name_invalid(self):
        """Testa validação de nome inválido"""
        valid, message = ValidationUtils.validate_name("J")
        assert valid is False
        assert "pelo menos 2 caracteres" in message

    def test_validate_message_valid(self):
        """Testa validação de mensagem válida"""
        valid, message = ValidationUtils.validate_message("Esta é uma mensagem de teste com mais de 10 caracteres")
        assert valid is True
        assert message == "Mensagem válida"

    def test_validate_message_too_short(self):
        """Testa validação de mensagem muito curta"""
        valid, message = ValidationUtils.validate_message("Oi")
        assert valid is False
        assert "pelo menos 10 caracteres" in message

    def test_sanitize_input(self):
        """Testa sanitização de entrada"""
        dirty_input = "<script>alert('xss')</script>Hello World\x00"
        clean_input = ValidationUtils.sanitize_input(dirty_input)
        assert "<script>" not in clean_input
        assert "\x00" not in clean_input
        assert "alert('xss')Hello World" == clean_input  # Tags são removidas, conteúdo permanece

class TestFormatUtils:
    """Testes para FormatUtils"""

    def test_format_uptime_seconds(self):
        """Testa formatação de uptime em segundos"""
        result = FormatUtils.format_uptime(65)
        assert result == "1m"  # Só mostra a unidade maior quando não há segundos restantes

    def test_format_uptime_hours(self):
        """Testa formatação de uptime em horas"""
        result = FormatUtils.format_uptime(7265)  # 2h 1m 5s
        assert "2h" in result
        assert "1m" in result

    def test_format_file_size_kb(self):
        """Testa formatação de tamanho de arquivo em KB"""
        result = FormatUtils.format_file_size(1536)
        assert "1.5" in result and "KB" in result

    def test_format_file_size_mb(self):
        """Testa formatação de tamanho de arquivo em MB"""
        result = FormatUtils.format_file_size(1048576)
        assert "1.0" in result and "MB" in result

    def test_format_timestamp_recent(self):
        """Testa formatação de timestamp recente"""
        recent_time = datetime.now() - timedelta(minutes=30)
        result = FormatUtils.format_timestamp(recent_time)
        assert "30 min atrás" in result

    def test_format_timestamp_old(self):
        """Testa formatação de timestamp antigo"""
        old_time = datetime.now() - timedelta(days=10)
        result = FormatUtils.format_timestamp(old_time)
        assert "/" in result  # Formato de data

class TestSecurityUtils:
    """Testes para SecurityUtils"""

    def test_generate_csrf_token(self):
        """Testa geração de token CSRF"""
        token1 = SecurityUtils.generate_csrf_token()
        token2 = SecurityUtils.generate_csrf_token()

        assert len(token1) > 32  # Tokens URL-safe são maiores
        assert token1 != token2  # Tokens devem ser únicos

    def test_hash_string_consistent(self):
        """Testa que hash da mesma string é consistente"""
        text = "test string"
        hash1 = SecurityUtils.hash_string(text)
        hash2 = SecurityUtils.hash_string(text)

        assert hash1 == hash2
        assert len(hash1) == 64  # SHA-256 produz 64 caracteres hex

    def test_generate_random_string(self):
        """Testa geração de string aleatória"""
        str1 = SecurityUtils.generate_random_string(16)
        str2 = SecurityUtils.generate_random_string(16)

        assert len(str1) == 16
        assert str1 != str2
        assert str1.isalnum()  # Deve conter apenas letras e números

    def test_sanitize_filename(self):
        """Testa sanitização de nome de arquivo"""
        dangerous_name = "../../../etc/passwd<script>.txt"
        safe_name = SecurityUtils.sanitize_filename(dangerous_name)

        assert "<" not in safe_name
        assert "script" not in safe_name
        assert ".." not in safe_name
        assert safe_name.endswith(".txt")

class TestDataUtils:
    """Testes para DataUtils"""

    def test_deep_merge(self):
        """Testa merge profundo de dicionários"""
        dict1 = {"a": 1, "b": {"c": 2}}
        dict2 = {"b": {"d": 3}, "e": 4}

        result = DataUtils.deep_merge(dict1, dict2)

        assert result["a"] == 1
        assert result["b"]["c"] == 2
        assert result["b"]["d"] == 3
        assert result["e"] == 4

    def test_flatten_dict(self):
        """Testa achatamento de dicionário"""
        nested = {"a": {"b": {"c": 1}}, "d": 2}

        result = DataUtils.flatten_dict(nested)

        assert result["a.b.c"] == 1
        assert result["d"] == 2

    def test_group_by_key(self):
        """Testa agrupamento por chave"""
        data = [
            {"type": "error", "message": "Error 1"},
            {"type": "info", "message": "Info 1"},
            {"type": "error", "message": "Error 2"}
        ]

        result = DataUtils.group_by_key(data, "type")

        assert len(result["error"]) == 2
        assert len(result["info"]) == 1
        assert result["error"][0]["message"] == "Error 1"

class TestUIUtils:
    """Testes para UIUtils"""

    def test_get_status_color(self):
        """Testa obtenção de cor por status"""
        assert UIUtils.get_status_color("healthy") == "#28a745"
        assert UIUtils.get_status_color("error") == "#dc3545"
        assert UIUtils.get_status_color("unknown") == "#6c757d"

    def test_get_status_icon(self):
        """Testa obtenção de ícone por status"""
        assert UIUtils.get_status_icon("healthy") == "✅"
        assert UIUtils.get_status_icon("error") == "❌"
        assert UIUtils.get_status_icon("unknown") == "❓"

    def test_truncate_text(self):
        """Testa truncamento de texto"""
        long_text = "A" * 150
        truncated = UIUtils.truncate_text(long_text, 100)

        assert len(truncated) == 100  # Texto truncado com "..."
        assert truncated.endswith("...")

class TestHomeService:
    """Testes para HomeService"""

    @pytest.mark.asyncio
    async def test_get_system_overview(self):
        """Testa obtenção de visão geral do sistema"""
        result = await HomeService.get_system_overview()

        assert "version" in result
        assert "total_modules" in result
        assert result["total_modules"] == 9

    @pytest.mark.asyncio
    async def test_process_contact_submission_valid(self):
        """Testa processamento de contato válido"""
        contact_data = {
            "name": "João Silva",
            "email": "joao@example.com",
            "message": "Esta é uma mensagem de teste com mais de 10 caracteres"
        }

        result = await HomeService.process_contact_submission(contact_data)

        assert result["success"] is True
        assert "contact_id" in result

    @pytest.mark.asyncio
    async def test_process_contact_submission_invalid(self):
        """Testa processamento de contato inválido"""
        contact_data = {
            "name": "J",
            "email": "invalid-email",
            "message": "Oi"
        }

        result = await HomeService.process_contact_submission(contact_data)

        assert result["success"] is False
        assert "error" in result

class TestContactService:
    """Testes para ContactService"""

    @pytest.mark.asyncio
    async def test_save_contact(self):
        """Testa salvamento de contato"""
        contact_data = {
            "name": "Test User",
            "email": "test@example.com",
            "message": "Test message"
        }

        contact_id = await ContactService.save_contact(contact_data)

        assert contact_id.startswith("contact_")
        assert len(contact_id) > 8

class TestSystemMonitorService:
    """Testes para SystemMonitorService"""

    @pytest.mark.asyncio
    async def test_check_database_connectivity(self):
        """Testa verificação de conectividade de bancos"""
        result = await SystemMonitorService.check_database_connectivity()

        assert "postgresql" in result
        assert "neo4j" in result
        assert isinstance(result["postgresql"], bool)

    @pytest.mark.asyncio
    async def test_get_performance_metrics(self):
        """Testa obtenção de métricas de performance"""
        result = await SystemMonitorService.get_performance_metrics()

        assert "response_time_avg" in result
        assert "cpu_usage" in result
        assert "memory_usage" in result

# Testes de integração
class TestIntegration:
    """Testes de integração"""

    @pytest.mark.asyncio
    async def test_full_contact_flow(self):
        """Testa fluxo completo de contato"""
        # Dados de teste
        contact_data = {
            "name": "Maria Santos",
            "email": "maria.santos@example.com",
            "message": "Gostaria de mais informações sobre o sistema SIGMA-PLI e suas funcionalidades."
        }

        # 1. Validar dados
        name_valid, _ = ValidationUtils.validate_name(contact_data["name"])
        email_valid, _ = ValidationUtils.validate_email_format(contact_data["email"])
        message_valid, _ = ValidationUtils.validate_message(contact_data["message"])

        assert name_valid and email_valid and message_valid

        # 2. Processar contato
        result = await HomeService.process_contact_submission(contact_data)
        assert result["success"] is True

        # 3. Verificar que ID foi gerado
        assert "contact_id" in result
        contact_id = result["contact_id"]

        # 4. Simular salvamento (IDs podem ser diferentes por timestamp)
        saved_id = await ContactService.save_contact(contact_data)
        assert saved_id.startswith("contact_")
        assert contact_id.startswith("contact_")
        assert len(saved_id) > 8
        assert len(contact_id) > 8

    @pytest.mark.asyncio
    async def test_system_health_check(self):
        """Testa verificação de saúde do sistema"""
        # Verificar conectividade
        db_status = await SystemMonitorService.check_database_connectivity()
        assert all(db_status.values())  # Todos os bancos devem estar conectados

        # Obter métricas
        metrics = await SystemMonitorService.get_performance_metrics()
        assert all(key in metrics for key in ["cpu_usage", "memory_usage", "response_time_avg"])

        # Verificar visão geral
        overview = await HomeService.get_system_overview()
        assert overview["system_health"] == "healthy"

# Configuração de fixtures para pytest
@pytest.fixture
def sample_contact_data():
    """Fixture com dados de contato de exemplo"""
    return {
        "name": "João Silva",
        "email": "joao.silva@example.com",
        "message": "Mensagem de teste para validação do sistema"
    }

@pytest.fixture
def sample_system_metrics():
    """Fixture com métricas de sistema de exemplo"""
    return {
        "cpu_usage": 45.5,
        "memory_usage": 67.8,
        "response_time_avg": 120,
        "active_connections": 8,
        "requests_per_minute": 150
    }

# Testes de performance
class TestPerformance:
    """Testes de performance"""

    @pytest.mark.asyncio
    async def test_service_response_time(self):
        """Testa tempo de resposta dos serviços"""
        import time

        start_time = time.time()
        result = await HomeService.get_system_overview()
        end_time = time.time()

        response_time = end_time - start_time
        assert response_time < 1.0  # Deve responder em menos de 1 segundo
        assert result is not None

    @pytest.mark.asyncio
    async def test_multiple_concurrent_requests(self):
        """Testa múltiplas requisições concorrentes"""
        import asyncio

        async def make_request():
            return await HomeService.get_system_overview()

        # Fazer 10 requisições concorrentes
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)

        assert len(results) == 10
        assert all(result is not None for result in results)

# Testes de carga (desabilitados por padrão)
class TestLoad:
    """Testes de carga - executar apenas quando necessário"""

    @pytest.mark.skip(reason="Teste de carga - executar manualmente")
    @pytest.mark.asyncio
    async def test_high_load_contact_submission(self):
        """Testa submissão de muitos contatos"""
        contact_data = {
            "name": "Load Test User",
            "email": "load.test@example.com",
            "message": "Mensagem de teste de carga " * 10
        }

        # Submeter 100 contatos
        tasks = [HomeService.process_contact_submission(contact_data) for _ in range(100)]
        results = await asyncio.gather(*tasks)

        successful = sum(1 for result in results if result["success"])
        assert successful >= 95  # Pelo menos 95% devem ser bem-sucedidos

if __name__ == "__main__":
    # Executar testes básicos se rodado diretamente
    pytest.main([__file__, "-v"])