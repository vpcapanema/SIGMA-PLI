#!/usr/bin/env python3
"""
Script para detectar e testar Neo4j Desktop
"""

from neo4j import GraphDatabase
import sys

# Configurações comuns do Neo4j Desktop
POSSIBLE_CONFIGS = [
    {
        "name": "Neo4j Desktop - Default",
        "uri": "bolt://localhost:7687",
        "user": "neo4j",
        "password": "neo4j",  # senha padrão inicial
    },
    {
        "name": "Neo4j Desktop - Porta alternativa",
        "uri": "bolt://localhost:7688",
        "user": "neo4j",
        "password": "neo4j",
    },
    {
        "name": "Neo4j Desktop - Com senha personalizada",
        "uri": "bolt://localhost:7687",
        "user": "neo4j",
        "password": "sigma123456",
    },
]


def test_connection(config):
    """Testa uma configuração específica"""
    try:
        print(f"\n🔄 Testando: {config['name']}")
        print(f"   URI: {config['uri']}")
        print(f"   Usuário: {config['user']}")

        driver = GraphDatabase.driver(
            config["uri"], auth=(config["user"], config["password"])
        )

        # Testar com uma query simples
        with driver.session() as session:
            result = session.run(
                "RETURN 'Hello Neo4j Desktop!' as message, timestamp() as ts"
            )
            record = result.single()
            message = record["message"]
            ts = record["ts"]

        driver.close()

        print(f"✅ CONEXÃO FUNCIONOU!")
        print(f"   Mensagem: {message}")
        print(f"   Timestamp: {ts}")
        print(f"\n🎉 Use estas configurações:")
        print(f"   URI: {config['uri']}")
        print(f"   Usuário: {config['user']}")
        print(f"   Senha: {config['password']}")

        return True

    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
            print(f"❌ Senha incorreta")
        elif (
            "couldn't connect" in error_msg.lower()
            or "connection refused" in error_msg.lower()
        ):
            print(f"❌ Não conseguiu conectar (verifique se o DBMS está rodando)")
        else:
            print(f"❌ Erro: {error_msg[:80]}...")
        return False


def main():
    print("=" * 60)
    print("🔍 DETECTOR DE NEO4J DESKTOP")
    print("=" * 60)

    print("\n💡 INSTRUÇÕES:")
    print("   1. Abra o Neo4j Desktop")
    print("   2. Inicie seu DBMS (clique em 'Start')")
    print("   3. Aguarde até o status ficar 'Running'")
    print("   4. Então execute este script")

    print("\n" + "=" * 60)
    print("Tentando detectar automaticamente...")
    print("=" * 60)

    found = False
    for config in POSSIBLE_CONFIGS:
        if test_connection(config):
            found = True
            break

    if not found:
        print("\n❌ Nenhuma configuração funcionou.")
        print("\n💡 PRÓXIMOS PASSOS:")
        print("   1. Verifique no Neo4j Desktop:")
        print("      - Clique nos 3 pontinhos do DBMS → 'Settings'")
        print("      - Procure por 'dbms.connector.bolt.listen_address'")
        print("      - Anote a porta (geralmente 7687)")
        print("\n   2. Anote sua senha do Neo4j Desktop")
        print("\n   3. Execute este script com a senha:")

        print("\n   Digite a senha do Neo4j Desktop (ou Enter para pular):")
        custom_password = input("   Senha: ").strip()

        if custom_password:
            custom_config = {
                "name": "Senha personalizada",
                "uri": "bolt://localhost:7687",
                "user": "neo4j",
                "password": custom_password,
            }
            test_connection(custom_config)
    else:
        print("\n✅ SUCESSO! Atualize o arquivo app/config.py com essas configurações.")


if __name__ == "__main__":
    main()
