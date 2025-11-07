#!/usr/bin/env python3
"""
Script para testar as novas funções Neo4j
"""

import asyncio
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import execute_neo4j_query, create_neo4j_example_graph, query_neo4j_example

async def test_basic_connection():
    """Testa conexão básica"""
    print("🔄 Testando conexão básica...")
    records, summary, keys = await execute_neo4j_query("RETURN 'Hello Neo4j' as message, timestamp() as ts")

    if records and summary:
        record = records[0]
        print("✅ Conexão OK!")
        print(f"   Mensagem: {record['message']}")
        print(f"   Timestamp: {record['ts']}")
        print(f"   Tempo: {summary.result_available_after} ms")
        return True
    else:
        print("❌ Falha na conexão")
        return False

async def test_create_graph():
    """Testa criação de grafo"""
    print("\n🔄 Testando criação de grafo...")
    success = await create_neo4j_example_graph()
    if success:
        print("✅ Grafo criado!")
        return True
    else:
        print("❌ Falha ao criar grafo")
        return False

async def test_query_graph():
    """Testa query no grafo"""
    print("\n🔄 Testando query no grafo...")
    records = await query_neo4j_example()
    if records:
        print("✅ Query executada!")
        print(f"   Resultados: {len(records)}")
        for record in records:
            print(f"   - {record.data()}")
        return True
    else:
        print("❌ Falha na query ou nenhum resultado")
        return False

async def main():
    print("=" * 50)
    print("🧪 TESTE DAS FUNÇÕES NEO4J")
    print("=" * 50)

    # Teste 1: Conexão básica
    if not await test_basic_connection():
        print("\n❌ Teste básico falhou. Abortando.")
        return

    # Teste 2: Criar grafo
    if not await test_create_graph():
        print("\n❌ Teste de criação falhou. Abortando.")
        return

    # Teste 3: Query
    await test_query_graph()

    print("\n✅ Todos os testes concluídos!")

if __name__ == "__main__":
    asyncio.run(main())