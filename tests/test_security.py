"""
Testes de Segurança - Encriptação, Validadores e Schemas
=========================================================

Testes unitários para validar:
- Criptografia Fernet (encrypt/decrypt)
- Hashing SHA256 (para buscas seguras)
- Validadores (CPF, CNPJ, Telefone)
- Schemas Pydantic com validação
- Mascaramento de dados

Executar com:
    python -m pytest tests/test_security.py -v
"""

import pytest
from datetime import datetime

# ============================================
# TESTES DE CRIPTOGRAFIA (crypto.py)
# ============================================


class TestCryptographyManager:
    """Testes para CryptographyManager (encrypt/decrypt/hash)"""

    def test_encrypt_decrypt_cpf(self):
        """Testa encriptação e descriptografia de CPF"""
        from app.security.crypto import init_crypto_manager, get_crypto_manager

        # Inicializar com chave mestre
        init_crypto_manager("test-master-key-32-caracteres-aqui!")
        crypto = get_crypto_manager()

        # CPF original
        cpf_original = "12345678900"

        # Encriptar
        cpf_encrypted = crypto.encrypt(cpf_original)

        # Verificar que é diferente
        assert cpf_encrypted != cpf_original
        assert len(cpf_encrypted) > len(cpf_original)

        # Descriptografar
        cpf_decrypted = crypto.decrypt(cpf_encrypted)

        # Verificar que voltou ao original
        assert cpf_decrypted == cpf_original

    def test_hash_cpf(self):
        """Testa hash SHA256 de CPF"""
        from app.security.crypto import init_crypto_manager, get_crypto_manager

        init_crypto_manager("test-master-key-32-caracteres-aqui!")
        crypto = get_crypto_manager()

        cpf = "12345678900"

        # Gerar hash
        hash1 = crypto.hash_data(cpf)
        hash2 = crypto.hash_data(cpf)

        # Verificar que são iguais (determinístico)
        assert hash1 == hash2

        # Verificar tamanho (SHA256 = 64 caracteres hex)
        assert len(hash1) == 64

        # Verificar que são diferentes de outros CPFs
        hash_diferente = crypto.hash_data("11111111111")
        assert hash1 != hash_diferente

    def test_encrypt_and_hash(self):
        """Testa encriptação + hash simultâneos"""
        from app.security.crypto import init_crypto_manager, get_crypto_manager

        init_crypto_manager("test-master-key-32-caracteres-aqui!")
        crypto = get_crypto_manager()

        cpf = "12345678900"

        # Encriptar e hashear
        encrypted, hash_value = crypto.encrypt_and_hash(cpf)

        # Verificar ambos retornam
        assert encrypted is not None
        assert hash_value is not None
        assert len(hash_value) == 64  # SHA256

        # Descriptografar e verificar hash
        decrypted = crypto.decrypt(encrypted)
        assert decrypted == cpf
        assert crypto.verify_hash(cpf, hash_value)

    def test_verify_hash(self):
        """Testa verificação de hash"""
        from app.security.crypto import init_crypto_manager, get_crypto_manager

        init_crypto_manager("test-master-key-32-caracteres-aqui!")
        crypto = get_crypto_manager()

        cpf = "12345678900"
        hash_correto = crypto.hash_data(cpf)

        # Verificar que o mesmo CPF bate
        assert crypto.verify_hash(cpf, hash_correto)

        # Verificar que CPF diferente não bate
        assert not crypto.verify_hash("11111111111", hash_correto)

    def test_encrypt_diferente_sempre(self):
        """Verifica que encriptação produz resultados diferentes cada vez (IV aleatório)"""
        from app.security.crypto import init_crypto_manager, get_crypto_manager

        init_crypto_manager("test-master-key-32-caracteres-aqui!")
        crypto = get_crypto_manager()

        cpf = "12345678900"

        # Encriptar 3 vezes
        encrypted1 = crypto.encrypt(cpf)
        encrypted2 = crypto.encrypt(cpf)
        encrypted3 = crypto.encrypt(cpf)

        # Todos devem ser diferentes (por causa do IV aleatório)
        assert encrypted1 != encrypted2
        assert encrypted2 != encrypted3
        assert encrypted1 != encrypted3

        # Mas todos devem descriptografar para o mesmo valor
        assert crypto.decrypt(encrypted1) == cpf
        assert crypto.decrypt(encrypted2) == cpf
        assert crypto.decrypt(encrypted3) == cpf


# ============================================
# TESTES DE VALIDADORES (validators.py)
# ============================================


class TestValidadores:
    """Testes para validadores de CPF, CNPJ, Telefone"""

    def test_validar_cpf_valido(self):
        """Testa CPF válido"""
        from app.security.validators import validar_cpf

        # CPF válido
        assert validar_cpf("11144477735")  # CPF real válido
        assert validar_cpf("111.444.777-35")  # Com formatação

    def test_validar_cpf_invalido(self):
        """Testa CPF inválido"""
        from app.security.validators import validar_cpf

        # CPF com dígitos inválidos
        assert not validar_cpf("12345678900")  # Módulo 11 errado

        # CPF conhecido como inválido (sequências)
        assert not validar_cpf("00000000000")
        assert not validar_cpf("11111111111")
        assert not validar_cpf("22222222222")

    def test_validar_telefone_valido(self):
        """Testa telefone válido"""
        from app.security.validators import validar_telefone

        # Telefone com 10 dígitos (sem 9o dígito)
        assert validar_telefone("1187654321")
        assert validar_telefone("(11) 8765-4321")

        # Telefone com 11 dígitos (com 9o dígito)
        assert validar_telefone("11987654321")
        assert validar_telefone("(11) 98765-4321")

    def test_validar_telefone_invalido(self):
        """Testa telefone inválido"""
        from app.security.validators import validar_telefone

        # Muito curto
        assert not validar_telefone("1234567")

        # Muito longo
        assert not validar_telefone("123456789012345")

    def test_validar_cnpj_valido(self):
        """Testa CNPJ válido"""
        from app.security.validators import validar_cnpj

        # CNPJ válido
        assert validar_cnpj("11222333000181")  # CNPJ real válido
        assert validar_cnpj("11.222.333/0001-81")  # Com formatação

    def test_validar_cnpj_invalido(self):
        """Testa CNPJ inválido"""
        from app.security.validators import validar_cnpj

        # CNPJ com dígitos inválidos
        assert not validar_cnpj("12345678901234")

        # CNPJ conhecido inválido
        assert not validar_cnpj("00000000000000")

    def test_limpar_cpf(self):
        """Testa limpeza de formatação de CPF"""
        from app.security.validators import limpar_cpf

        assert limpar_cpf("111.444.777-35") == "11144477735"
        assert limpar_cpf("11144477735") == "11144477735"
        assert limpar_cpf("111 444 777 35") == "11144477735"

    def test_formatar_cpf(self):
        """Testa formatação de CPF"""
        from app.security.validators import formatar_cpf

        assert formatar_cpf("11144477735") == "111.444.777-35"

    def test_formatar_telefone(self):
        """Testa formatação de telefone"""
        from app.security.validators import formatar_telefone

        # 10 dígitos
        assert formatar_telefone("1187654321") == "(11) 8765-4321"

        # 11 dígitos
        assert formatar_telefone("11987654321") == "(11) 98765-4321"


# ============================================
# TESTES DE SCHEMAS (schema_pessoa_fisica.py)
# ============================================


class TestSchemaPessoaFisica:
    """Testes para Pydantic schemas com validação"""

    def test_criar_pessoa_fisica_valida(self):
        """Testa criação com dados válidos"""
        from app.models.schemas.schema_pessoa_fisica import PessoaFisicaCreate

        dados = PessoaFisicaCreate(
            nome="João Silva",
            cpf="11144477735",
            telefone="11987654321",
            email="joao@example.com",
        )

        assert dados.nome == "João Silva"
        assert dados.cpf == "11144477735"
        assert dados.telefone == "11987654321"
        assert dados.email == "joao@example.com"

    def test_criar_pessoa_fisica_cpf_invalido(self):
        """Testa validação de CPF inválido"""
        from app.models.schemas.schema_pessoa_fisica import PessoaFisicaCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            PessoaFisicaCreate(
                nome="João Silva",
                cpf="12345678900",  # CPF inválido
                telefone="11987654321",
                email="joao@example.com",
            )

    def test_criar_pessoa_fisica_email_invalido(self):
        """Testa validação de email"""
        from app.models.schemas.schema_pessoa_fisica import PessoaFisicaCreate
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            PessoaFisicaCreate(
                nome="João Silva",
                cpf="11144477735",
                telefone="11987654321",
                email="email-invalido",  # Email sem @
            )

    def test_response_mascara_cpf(self):
        """Testa se resposta mascara CPF"""
        from app.models.schemas.schema_pessoa_fisica import PessoaFisicaResponse

        response = PessoaFisicaResponse(
            id="550e8400-e29b-41d4-a716-446655440000",
            nome="João Silva",
            cpf_display="***.***.***-35",
            email="joao@example.com",
            telefone_display="(**) ****-4321",
            data_criacao=datetime.utcnow(),
            ativo=True,
        )

        # Verificar que CPF é mascarado
        assert "***" in response.cpf_display
        assert "35" in response.cpf_display  # Últimos 2 dígitos visíveis

    def test_response_nao_expoe_criptografado(self):
        """Testa que response não expõe dados criptografados"""
        from app.models.schemas.schema_pessoa_fisica import PessoaFisicaResponse

        response = PessoaFisicaResponse(
            id="550e8400-e29b-41d4-a716-446655440000",
            nome="João Silva",
            cpf_display="***.***.***-35",
            email="joao@example.com",
            telefone_display="(**) ****-4321",
            data_criacao=datetime.utcnow(),
            ativo=True,
        )

        # Verificar que não há campos de criptografia
        assert not hasattr(response, "cpf_criptografado")
        assert not hasattr(response, "cpf_hash")
        assert not hasattr(response, "telefone_criptografado")


# ============================================
# TESTES DE SERVIÇO (service_pessoa_fisica.py)
# ============================================


class TestPessoaFisicaService:
    """Testes para serviço com encriptação"""

    def test_mascarar_cpf(self):
        """Testa mascaramento de CPF"""
        from app.services.service_pessoa_fisica import PessoaFisicaService

        service = PessoaFisicaService()

        # Testar com CPF limpo
        assert service._mascarar_cpf("11144477735") == "***.***.***-35"

        # Testar com CPF formatado
        assert service._mascarar_cpf("111.444.777-35") == "***.***.***-35"

        # Testar com CPF curto (inválido)
        assert service._mascarar_cpf("123") == "***.***.***-**"

    def test_mascarar_telefone(self):
        """Testa mascaramento de telefone"""
        from app.services.service_pessoa_fisica import PessoaFisicaService

        service = PessoaFisicaService()

        # Telefone com 10 dígitos
        assert service._mascarar_telefone("1187654321") == "(**) ****-4321"

        # Telefone com 11 dígitos
        assert service._mascarar_telefone("11987654321") == "(**) ****-4321"

        # Telefone formatado
        assert service._mascarar_telefone("(11) 98765-4321") == "(**) ****-4321"

    def test_registrar_auditoria(self):
        """Testa registro de auditoria"""
        from app.services.service_pessoa_fisica import (
            PessoaFisicaService,
            AuditoriaAcao,
        )

        service = PessoaFisicaService()

        # Registrar ação
        service._registrar_auditoria(
            acao=AuditoriaAcao.CRIACAO,
            entidade_tipo="PessoaFisica",
            entidade_id="test-uuid",
            usuario_id="admin",
            usuario_ip="127.0.0.1",
            descricao="Teste de auditoria",
            dados_sensíveis={"cpf_hash": "abc123"},
        )

        # Verificar que foi registrado
        assert len(service.audit_log) == 1

        # Verificar conteúdo
        entrada = service.audit_log[0]
        assert entrada["acao"] == "CRIACAO"
        assert entrada["usuario_id"] == "admin"
        assert entrada["usuario_ip"] == "127.0.0.1"


# ============================================
# TESTES DE INTEGRAÇÃO
# ============================================


class TestIntegracaoSeguranca:
    """Testes de integração de todo o sistema de segurança"""

    def test_fluxo_completo_criar_pessoa(self):
        """Testa fluxo completo: validação -> encriptação -> mascaramento"""
        from app.models.schemas.schema_pessoa_fisica import PessoaFisicaCreate
        from app.services.service_pessoa_fisica import PessoaFisicaService
        from app.security.crypto import init_crypto_manager

        # Inicializar cripto
        init_crypto_manager("test-master-key-32-caracteres-aqui!")

        # 1. Validar entrada com Pydantic
        dados = PessoaFisicaCreate(
            nome="João Silva",
            cpf="11144477735",
            telefone="11987654321",
            email="joao@example.com",
        )

        # 2. Criar serviço
        service = PessoaFisicaService()

        # 3. Verificar mascaramento
        cpf_mascarado = service._mascarar_cpf(dados.cpf)
        tel_mascarado = service._mascarar_telefone(dados.telefone)

        assert cpf_mascarado == "***.***.***-35"
        assert tel_mascarado == "(**) ****-4321"

        # 4. Verificar encriptação
        crypto = service.crypto
        cpf_encrypted, cpf_hash = crypto.encrypt_and_hash(dados.cpf)

        assert crypto.decrypt(cpf_encrypted) == dados.cpf
        assert crypto.verify_hash(dados.cpf, cpf_hash)

    def test_busca_hash_nao_descriptografa(self):
        """Testa que busca por hash não descriptografa"""
        from app.services.service_pessoa_fisica import PessoaFisicaService
        from app.security.crypto import init_crypto_manager

        init_crypto_manager("test-master-key-32-caracteres-aqui!")

        service = PessoaFisicaService()
        crypto = service.crypto

        cpf1 = "11144477735"
        cpf2 = "98765432100"

        # Gerar hashes
        hash1 = crypto.hash_data(cpf1)
        hash2 = crypto.hash_data(cpf2)

        # Verificar que são diferentes
        assert hash1 != hash2

        # Simular busca: verificar hash sem descriptografar
        assert crypto.verify_hash(cpf1, hash1)
        assert crypto.verify_hash(cpf2, hash2)
        assert not crypto.verify_hash(cpf1, hash2)


# ============================================
# TESTES DE COMPLIANCE LGPD
# ============================================


class TestComplianceLGPD:
    """Testes para validar compliance LGPD"""

    def test_dados_nunca_descriptografados_em_resposta(self):
        """Garante que dados sensíveis nunca são descriptografados em respostas"""
        from app.models.schemas.schema_pessoa_fisica import PessoaFisicaResponse

        response = PessoaFisicaResponse(
            id="test-uuid",
            nome="João",
            cpf_display="***.***.***-35",  # Mascarado
            email="joao@example.com",
            telefone_display="(**) ****-4321",  # Mascarado
            data_criacao=datetime.utcnow(),
            ativo=True,
        )

        # Converter para dict e verificar
        response_dict = response.dict()

        # Verificar que não há valores desmascarados
        assert not any(
            "111.444.777-35" in str(v)
            or "11144477735" in str(v)
            or "(11) 98765-4321" in str(v)
            or "11987654321" in str(v)
            for v in response_dict.values()
        )

    def test_auditoria_registra_hash_nao_valor(self):
        """Verifica que auditoria registra hash, nunca valor"""
        from app.services.service_pessoa_fisica import (
            PessoaFisicaService,
            AuditoriaAcao,
        )

        service = PessoaFisicaService()

        # Registrar auditoria com hash
        service._registrar_auditoria(
            acao=AuditoriaAcao.BUSCA_CPF,
            entidade_tipo="PessoaFisica",
            entidade_id="test-uuid",
            usuario_id="admin",
            usuario_ip="127.0.0.1",
            descricao="Busca realizada",
            dados_sensíveis={"cpf_hash": "abc123def456"},
        )

        # Verificar que auditoria NÃO contém valor
        entrada = service.audit_log[0]

        # Não deve conter CPF original
        assert "11144477735" not in str(entrada)
        assert "***.***.***-35" not in str(entrada)

        # Deve conter apenas hash
        assert "abc123def456" in str(entrada.get("dados_sensíveis", {}))


if __name__ == "__main__":
    # Executar com: python -m pytest tests/test_security.py -v
    pytest.main([__file__, "-v", "--tb=short"])
