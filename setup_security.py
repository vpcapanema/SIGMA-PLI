"""
Script de Configuração de Segurança - SIGMA-PLI
===============================================

Facilita a inicialização do sistema de segurança:
1. Gera MASTER_KEY segura
2. Cria/atualiza .env
3. Valida configuração
4. Executa testes

Uso:
    python setup_security.py

Menu Interativo:
    python setup_security.py --interactive
"""

import os
import sys
import secrets
import subprocess
from pathlib import Path
from datetime import datetime


def gerar_master_key(comprimento: int = 32) -> str:
    """Gera chave mestra segura com comprimento especificado"""
    return secrets.token_hex(comprimento)


def ler_env_atual() -> dict:
    """Lê variáveis de ambiente do .env atual"""
    env_file = Path(".env")
    env_vars = {}

    if env_file.exists():
        with open(env_file) as f:
            for linha in f:
                linha = linha.strip()
                if linha and not linha.startswith("#"):
                    if "=" in linha:
                        chave, valor = linha.split("=", 1)
                        env_vars[chave.strip()] = valor.strip()

    return env_vars


def salvar_env(env_vars: dict) -> None:
    """Salva variáveis de ambiente no .env"""
    env_file = Path(".env")

    # Backup do arquivo anterior
    if env_file.exists():
        backup_file = Path(f".env.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        print(f"📦 Criando backup: {backup_file}")
        env_file.replace(backup_file)

    # Escrever novo .env
    with open(env_file, "w") as f:
        f.write("# SIGMA-PLI - Arquivo de Configuração\n")
        f.write(f"# Gerado em: {datetime.now().isoformat()}\n")
        f.write(
            "# NUNCA commitar este arquivo no Git! Use .env.example como template\n\n"
        )

        for chave, valor in sorted(env_vars.items()):
            if chave.lower() in [
                "master_key",
                "jwt_secret_key",
                "smtp_password",
                "aws_secret_access_key",
            ]:
                # Não exibir chaves sensíveis
                f.write(f"{chave}={valor}\n")
            else:
                f.write(f"{chave}={valor}\n")

    print(f"✅ Arquivo .env criado/atualizado")


def testar_importacoes() -> bool:
    """Testa se todas as dependências de segurança podem ser importadas"""
    try:
        from app.security.crypto import CryptographyManager
        from app.security.validators import validar_cpf
        from app.models.schemas.schema_pessoa_fisica import PessoaFisicaCreate
        from app.services.service_pessoa_fisica import PessoaFisicaService

        print("✅ Todas as dependências de segurança importadas com sucesso")
        return True

    except Exception as e:
        print(f"❌ Erro ao importar dependências: {e}")
        return False


def testar_criptografia(master_key: str) -> bool:
    """Testa se a criptografia funciona com a chave fornecida"""
    try:
        from app.security.crypto import init_crypto_manager, get_crypto_manager

        print("\n🔐 Testando criptografia...")

        # Inicializar
        init_crypto_manager(master_key)
        crypto = get_crypto_manager()

        # Testar encrypt/decrypt
        texto_original = "12345678900"
        encrypted = crypto.encrypt(texto_original)
        decrypted = crypto.decrypt(encrypted)

        if decrypted != texto_original:
            raise ValueError("Descriptografia falhou!")

        print("  ✅ Criptografia Fernet: OK")

        # Testar hash
        hash_value = crypto.hash_data(texto_original)
        if not crypto.verify_hash(texto_original, hash_value):
            raise ValueError("Hash verification failed!")

        print("  ✅ Hashing SHA256: OK")

        # Testar encrypt_and_hash
        enc, h = crypto.encrypt_and_hash(texto_original)
        if not crypto.verify_hash(texto_original, h):
            raise ValueError("Encrypt and hash failed!")

        print("  ✅ Encrypt + Hash simultâneo: OK")

        return True

    except Exception as e:
        print(f"  ❌ Erro na criptografia: {e}")
        return False


def testar_validadores() -> bool:
    """Testa se os validadores funcionam"""
    try:
        from app.security.validators import (
            validar_cpf,
            validar_cnpj,
            validar_telefone,
            limpar_cpf,
            formatar_cpf,
        )

        print("\n✔️ Testando validadores...")

        # CPF válido
        if not validar_cpf("11144477735"):
            raise ValueError("CPF válido foi rejeitado!")
        print("  ✅ Validador CPF: OK")

        # Telefone válido
        if not validar_telefone("11987654321"):
            raise ValueError("Telefone válido foi rejeitado!")
        print("  ✅ Validador Telefone: OK")

        # Limpeza de CPF
        cpf_limpo = limpar_cpf("111.444.777-35")
        if cpf_limpo != "11144477735":
            raise ValueError("Limpeza de CPF falhou!")
        print("  ✅ Limpeza de CPF: OK")

        # Formatação de CPF
        cpf_formatado = formatar_cpf("11144477735")
        if cpf_formatado != "111.444.777-35":
            raise ValueError("Formatação de CPF falhou!")
        print("  ✅ Formatação de CPF: OK")

        return True

    except Exception as e:
        print(f"  ❌ Erro nos validadores: {e}")
        return False


def testar_schemas() -> bool:
    """Testa se os schemas Pydantic funcionam"""
    try:
        from app.models.schemas.schema_pessoa_fisica import (
            PessoaFisicaCreate,
            PessoaFisicaResponse,
        )
        from pydantic import ValidationError

        print("\n📋 Testando schemas Pydantic...")

        # Schema válido
        dados = PessoaFisicaCreate(
            nome="João Silva",
            cpf="11144477735",
            telefone="11987654321",
            email="joao@example.com",
        )
        print("  ✅ Schema PessoaFisicaCreate: OK")

        # Schema inválido (CPF errado)
        try:
            PessoaFisicaCreate(
                nome="João Silva",
                cpf="12345678900",  # Inválido
                telefone="11987654321",
                email="joao@example.com",
            )
            raise ValueError("Schema aceitou CPF inválido!")
        except ValidationError:
            print("  ✅ Validação de CPF em schema: OK")

        return True

    except Exception as e:
        print(f"  ❌ Erro nos schemas: {e}")
        return False


def executar_testes() -> bool:
    """Executa suite de testes de segurança"""
    try:
        print("\n🧪 Executando testes unitários...")

        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/test_security.py", "-v"],
            capture_output=True,
            text=True,
            timeout=60,
        )

        if result.returncode == 0:
            print("  ✅ Todos os testes passaram!")
            return True
        else:
            print("  ❌ Alguns testes falharam:")
            print(result.stdout[-500:])  # Últimas 500 chars
            return False

    except subprocess.TimeoutExpired:
        print("  ⚠️ Testes demoraram muito (timeout)")
        return False
    except Exception as e:
        print(f"  ⚠️ Não foi possível executar testes: {e}")
        return False


def exibir_menu_interativo():
    """Menu interativo para configuração"""
    print("\n" + "=" * 60)
    print("🔐 CONFIGURAÇÃO DE SEGURANÇA - SIGMA-PLI")
    print("=" * 60)

    while True:
        print("\nOpções:")
        print("1. Gerar nova MASTER_KEY")
        print("2. Criar/atualizar .env")
        print("3. Testar importações")
        print("4. Testar criptografia")
        print("5. Testar validadores")
        print("6. Testar schemas")
        print("7. Executar testes completos")
        print("8. Setup completo (todas as etapas)")
        print("0. Sair")

        opcao = input("\nEscolha uma opção: ").strip()

        if opcao == "1":
            master_key = gerar_master_key()
            print(f"\n🔑 Sua nova MASTER_KEY:\n{master_key}")
            print("\n⚠️ GUARDE ESTA CHAVE EM LOCAL SEGURO!")
            print("Se perder, não poderá descriptografar dados antigos!")

        elif opcao == "2":
            env_vars = ler_env_atual()

            # Solicitar dados
            print("\nConfiguração de .env:")

            if "MASTER_KEY" not in env_vars:
                print("\n⚠️ MASTER_KEY não encontrada!")
                gerar = input("Deseja gerar uma nova? (s/n): ").strip().lower()
                if gerar == "s":
                    env_vars["MASTER_KEY"] = gerar_master_key()
                    print(f"✅ MASTER_KEY gerada: {env_vars['MASTER_KEY'][:20]}...")

            # Outros valores
            if "DATABASE_URL" not in env_vars:
                env_vars["DATABASE_URL"] = (
                    input("DATABASE_URL [postgresql://...]: ").strip()
                    or "postgresql://sigma_user:sigma_pass@localhost:5432/sigma_pli"
                )

            if "DEBUG" not in env_vars:
                env_vars["DEBUG"] = "false"

            salvar_env(env_vars)

        elif opcao == "3":
            testar_importacoes()

        elif opcao == "4":
            env_vars = ler_env_atual()
            if "MASTER_KEY" in env_vars:
                testar_criptografia(env_vars["MASTER_KEY"])
            else:
                print("❌ MASTER_KEY não encontrada em .env")

        elif opcao == "5":
            testar_validadores()

        elif opcao == "6":
            testar_schemas()

        elif opcao == "7":
            env_vars = ler_env_atual()
            if "MASTER_KEY" not in env_vars:
                print("❌ MASTER_KEY não encontrada em .env")
                continue

            executar_testes()

        elif opcao == "8":
            print("\n🚀 Executando setup completo...\n")

            # 1. Gerar MASTER_KEY
            env_vars = ler_env_atual()
            if "MASTER_KEY" not in env_vars:
                env_vars["MASTER_KEY"] = gerar_master_key()
                print(f"✅ MASTER_KEY gerada")

            # 2. Salvar .env
            if "DATABASE_URL" not in env_vars:
                env_vars["DATABASE_URL"] = (
                    "postgresql://sigma_user:sigma_pass@localhost:5432/sigma_pli"
                )
            if "DEBUG" not in env_vars:
                env_vars["DEBUG"] = "false"

            salvar_env(env_vars)

            # 3. Testes
            print("\n" + "=" * 60)
            print("🧪 VALIDAÇÃO DE SEGURANÇA")
            print("=" * 60)

            sucesso = True
            sucesso &= testar_importacoes()
            sucesso &= testar_criptografia(env_vars["MASTER_KEY"])
            sucesso &= testar_validadores()
            sucesso &= testar_schemas()
            sucesso &= executar_testes()

            if sucesso:
                print("\n" + "=" * 60)
                print("✅ SETUP COMPLETO COM SUCESSO!")
                print("=" * 60)
                print("\n📚 Próximos passos:")
                print("1. Adicionar campos encriptados ao banco (migration SQL)")
                print(
                    "2. Criar router de cadastro (seguir EXEMPLO_INTEGRACAO_SEGURANCA.py)"
                )
                print("3. Registrar router no compose (/app/routers/__init__.py)")
                print("4. Testar endpoints com cURL ou Postman")
                print("\n📖 Ver: GUIA_IMPLEMENTACAO_SEGURANCA.md")
            else:
                print("\n" + "=" * 60)
                print("⚠️ ALGUNS TESTES FALHARAM")
                print("=" * 60)
                print("Verifique os erros acima e tente novamente")

        elif opcao == "0":
            print("\n👋 Até logo!")
            break

        else:
            print("❌ Opção inválida!")


def main():
    """Ponto de entrada do script"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Script de configuração de segurança - SIGMA-PLI"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Modo interativo"
    )
    parser.add_argument(
        "--generate-key", action="store_true", help="Gerar apenas MASTER_KEY"
    )
    parser.add_argument("--setup", action="store_true", help="Setup completo")

    args = parser.parse_args()

    if args.generate_key:
        # Apenas gerar chave
        master_key = gerar_master_key()
        print(f"Sua MASTER_KEY:\n{master_key}")

    elif args.setup:
        # Setup completo não-interativo
        print("🚀 Executando setup completo...\n")

        env_vars = ler_env_atual()
        if "MASTER_KEY" not in env_vars:
            env_vars["MASTER_KEY"] = gerar_master_key()
        if "DATABASE_URL" not in env_vars:
            env_vars["DATABASE_URL"] = (
                "postgresql://sigma_user:sigma_pass@localhost:5432/sigma_pli"
            )
        if "DEBUG" not in env_vars:
            env_vars["DEBUG"] = "false"

        salvar_env(env_vars)

        # Testes
        testar_importacoes()
        testar_criptografia(env_vars["MASTER_KEY"])
        testar_validadores()
        testar_schemas()
        executar_testes()

    elif args.interactive or len(sys.argv) == 1:
        # Menu interativo (padrão)
        exibir_menu_interativo()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
