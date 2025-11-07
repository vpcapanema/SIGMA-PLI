"""
Teste do Serviço de Email
Testa a conexão SMTP e envio de email
"""

import asyncio
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path ANTES de qualquer import do app
root_dir = Path(__file__).parent.resolve()
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

# Verificar se o diretório app existe
app_dir = root_dir / "app"
if not app_dir.exists():
    print(f"❌ ERRO: Diretório 'app' não encontrado em {root_dir}")
    print(f"   Estrutura esperada: {root_dir}/app/config.py")
    sys.exit(1)

# Imports precisam estar após modificação do sys.path
# noqa: E402 (module level import not at top of file)
from app.services.M01_auth.service_email import EmailService  # noqa: E402
from app.config import settings  # noqa: E402


async def testar_servico_email():
    """Testa o serviço de email"""
    print("=" * 80)
    print("TESTE DO SERVIÇO DE EMAIL - SIGMA-PLI")
    print("=" * 80)

    email_service = EmailService()

    # 1. Testar configuração
    print("\n📋 CONFIGURAÇÕES:")
    print(f"   SMTP Host: {settings.smtp_host}")
    print(f"   SMTP Port: {settings.smtp_port}")
    print(f"   SMTP User: {settings.smtp_user}")
    print(f"   Email From: {settings.email_from}")
    print(f"   Email Admin: {settings.email_admin}")

    # 2. Testar conexão SMTP
    print("\n🔌 TESTANDO CONEXÃO SMTP...")
    conexao_ok = await email_service.testar_conexao()

    if conexao_ok:
        print("   ✅ Conexão SMTP estabelecida com sucesso!")
    else:
        print("   ❌ Falha na conexão SMTP")
        print("   ⚠️  Verifique as credenciais no arquivo .env")
        return False

    # 3. Testar envio de email simples
    print("\n📧 TESTANDO ENVIO DE EMAIL SIMPLES...")
    dados_usuario = {
        "nome": "Teste Usuario",
        "email": "teste@example.com",
        "cpf": "123.456.789-00",
        "nome_pessoa": "João da Silva",
        "cpf_pessoa": "987.654.321-00",
    }

    sucesso = await email_service.enviar_confirmacao_solicitacao(dados_usuario)

    if sucesso:
        print("   ✅ Email de confirmação enviado com sucesso!")
    else:
        print("   ❌ Falha no envio do email")
        print("   ⚠️  Verifique os logs para mais detalhes")
        return False

    # 4. Testar notificação de administradores
    print("\n👨‍💼 TESTANDO NOTIFICAÇÃO DE ADMINISTRADORES...")
    sucesso_admin = await email_service.notificar_administradores(dados_usuario)

    if sucesso_admin:
        print("   ✅ Notificação de administradores enviada!")
    else:
        print("   ❌ Falha na notificação de administradores")
        return False

    print("\n" + "=" * 80)
    print("✅ TODOS OS TESTES PASSARAM COM SUCESSO!")
    print("=" * 80)
    return True


if __name__ == "__main__":
    print("\n🚀 Iniciando testes do serviço de email...\n")

    try:
        resultado = asyncio.run(testar_servico_email())
        sys.exit(0 if resultado else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Testes interrompidos pelo usuário")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ ERRO DURANTE OS TESTES: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
