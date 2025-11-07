#!/usr/bin/env python3
"""
Diagnóstico detalhado da conexão Neo4j Aura
"""

import socket
import ssl
import time
from neo4j import GraphDatabase

def test_network_connectivity(host, port):
    """Testa conectividade básica de rede"""
    print(f"🔍 Testando conectividade de rede: {host}:{port}")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)
        result = sock.connect_ex((host, port))
        sock.close()

        if result == 0:
            print(f"✅ Porta {port} está aberta em {host}")
            return True
        else:
            print(f"❌ Porta {port} está fechada em {host}")
            return False
    except Exception as e:
        print(f"❌ Erro de rede: {e}")
        return False

def test_ssl_connection(host, port):
    """Testa conexão SSL"""
    print(f"🔒 Testando conexão SSL: {host}:{port}")
    try:
        context = ssl.create_default_context()
        with socket.create_connection((host, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=host) as ssock:
                print(f"✅ Conexão SSL estabelecida com {host}:{port}")
                print(f"   Certificado: {ssock.getpeercert()['subject']}")
                return True
    except Exception as e:
        print(f"❌ Erro SSL: {e}")
        return False

def test_neo4j_connection(uri, user, password, database):
    """Testa conexão Neo4j completa"""
    print(f"🚀 Testando conexão Neo4j completa...")
    print(f"   URI: {uri}")
    print(f"   User: {user}")
    print(f"   Database: {database}")

    try:
        driver = GraphDatabase.driver(
            uri,
            auth=(user, password),
            connection_timeout=30,
            max_connection_lifetime=30
        )

        with driver.session(database=database) as session:
            # Teste simples
            result = session.run("RETURN 'Neo4j Aura OK' as status")
            record = result.single()
            status = record["status"]

            print(f"✅ Conexão Neo4j bem-sucedida: {status}")

            # Informações do banco
            info_result = session.run("CALL dbms.components() YIELD name, versions, edition")
            for record in info_result:
                print(f"   {record['name']} {record['versions'][0]} {record['edition']}")

            driver.close()
            return True

    except Exception as e:
        print(f"❌ Erro na conexão Neo4j: {e}")
        print(f"   Tipo do erro: {type(e).__name__}")

        # Tentar diagnóstico adicional
        if "routing" in str(e).lower():
            print("💡 Este erro geralmente indica que a instância ainda está sendo provisionada.")
            print("   Tente novamente em alguns minutos.")
        elif "authentication" in str(e).lower():
            print("💡 Erro de autenticação - verifique usuário/senha.")
        elif "timeout" in str(e).lower():
            print("💡 Timeout - a instância pode estar sobrecarregada.")

        return False

def main():
    print("=" * 60)
    print("🔬 DIAGNÓSTICO DETALHADO - NEO4J AURA SIGMA-PLI")
    print("=" * 60)

    # Configurações da nova instância
    host = "6b7fc90e.databases.neo4j.io"
    port = 7687
    uri = f"neo4j+s://{host}"
    user = "neo4j"
    password = "RWpV06f_yQ9CAo2NbsP76jhNbInaZgE0kOxOBSdQDRs"
    database = "neo4j"

    print(f"🎯 Testando instância: {host}")
    print(f"📅 Data/Hora: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Teste 1: Conectividade básica
    network_ok = test_network_connectivity(host, port)
    print()

    # Teste 2: Conexão SSL (porta 7687 usa SSL)
    ssl_ok = test_ssl_connection(host, port)
    print()

    # Teste 3: Conexão Neo4j completa
    if network_ok and ssl_ok:
        neo4j_ok = test_neo4j_connection(uri, user, password, database)
    else:
        print("⏭️  Pulando teste Neo4j devido a falhas anteriores")
        neo4j_ok = False

    print()
    print("=" * 60)
    print("📋 RESUMO DO DIAGNÓSTICO:")

    status = []
    if network_ok:
        status.append("✅ Rede")
    else:
        status.append("❌ Rede")

    if ssl_ok:
        status.append("✅ SSL")
    else:
        status.append("❌ SSL")

    if neo4j_ok:
        status.append("✅ Neo4j")
    else:
        status.append("❌ Neo4j")

    print(f"   Status: {' | '.join(status)}")

    if neo4j_ok:
        print("🎉 Instância Neo4j totalmente operacional!")
        print("   ✅ Pronto para importar dados e usar na aplicação")
    elif network_ok and ssl_ok:
        print("⚠️  Rede e SSL OK, mas Neo4j ainda não responde")
        print("   💡 Instância provavelmente ainda inicializando")
        print("   🔄 Tente novamente em 5-10 minutos")
    else:
        print("❌ Problemas de conectividade básica")
        print("   🔍 Verifique conexão com internet")

    print()
    print("🌐 Neo4j Browser: https://6b7fc90e.databases.neo4j.io/browser/")
    print("=" * 60)

if __name__ == "__main__":
    main()