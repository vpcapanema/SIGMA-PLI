#!/usr/bin/env python3
"""
Teste direto do Neo4j usando execute_query
"""

import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from neo4j import GraphDatabase


# Configurações do Neo4j Local
URI = "neo4j://localhost:7687"
AUTH = ("neo4j", "sigma123456")


def test_direct():
    """Teste direto usando execute_query"""
    print("🔄 Teste direto com execute_query...")

    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            driver.verify_connectivity()
            print("✅ Conectividade verificada!")

            # Teste execute_query
            records, summary, keys = driver.execute_query(
                "RETURN 'Hello Direct' as message, timestamp() as ts"
            )

            print("✅ execute_query funcionou!")
            print(f"   Records: {len(records)}")
            if records:
                record = records[0]
                print(f"   Mensagem: {record['message']}")
                print(f"   Timestamp: {record['ts']}")
                print(f"   Tempo: {summary.result_available_after} ms")

            return True

    except Exception as e:
        print(f"❌ Erro: {e}")
        return False


if __name__ == "__main__":
    print("=" * 40)
    print("🔧 TESTE DIRETO NEO4J")
    print("=" * 40)

    success = test_direct()
    if success:
        print("\n✅ Teste direto OK!")
    else:
        print("\n❌ Teste direto falhou!")
