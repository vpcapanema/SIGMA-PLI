#!/usr/bin/env python3
"""
Script para testar conexão com Neo4j Local
"""

from neo4j import GraphDatabase
import sys

# Configurações do Neo4j Local
NEO4J_LOCAL_CONFIG = {
    "uri": "bolt://localhost:7687",
    "user": "neo4j",
    "password": "sigma123456",  # Senha definida no docker-compose
    "database": "neo4j",
}


def test_local_connection():
    """Testa a conexão com o Neo4j Local"""

    try:
        print("🔄 Testando conexão com Neo4j Local...")
        print(f"   URI: {NEO4J_LOCAL_CONFIG['uri']}")
        print(f"   Usuário: {NEO4J_LOCAL_CONFIG['user']}")
        print(f"   Database: {NEO4J_LOCAL_CONFIG['database']}")

        # Criar driver
        driver = GraphDatabase.driver(
            NEO4J_LOCAL_CONFIG["uri"],
            auth=(NEO4J_LOCAL_CONFIG["user"], NEO4J_LOCAL_CONFIG["password"]),
        )

        # Testar conexão executando uma query simples
        with driver.session(database=NEO4J_LOCAL_CONFIG["database"]) as session:
            result = session.run("RETURN 'Hello Neo4j Local!' as message")
            record = result.single()
            message = record["message"]

            print("✅ Conexão bem-sucedida!")
            print(f"   Resposta do servidor: {message}")

            # Verificar versão do Neo4j
            version_result = session.run(
                "CALL dbms.components() YIELD name, versions, edition"
            )
            for record in version_result:
                print(
                    f"   Neo4j {record['name']} {record['versions'][0]} {record['edition']}"
                )

        driver.close()
        return True

    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        print("\n💡 Dicas para resolver:")
        print("   1. Verifique se o Docker está rodando")
        print("   2. Confirme se o container Neo4j está ativo (docker ps)")
        print("   3. Aguarde alguns minutos para o Neo4j inicializar completamente")
        return False


def get_local_database_info():
    """Obtém informações sobre o banco de dados local"""

    try:
        driver = GraphDatabase.driver(
            NEO4J_LOCAL_CONFIG["uri"],
            auth=(NEO4J_LOCAL_CONFIG["user"], NEO4J_LOCAL_CONFIG["password"]),
        )

        with driver.session(database=NEO4J_LOCAL_CONFIG["database"]) as session:
            print("\n📊 Informações do banco de dados local:")

            # Contar nós
            result = session.run("MATCH (n) RETURN count(n) as node_count")
            node_count = result.single()["node_count"]
            print(f"   Nós: {node_count}")

            # Contar relacionamentos
            result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
            rel_count = result.single()["rel_count"]
            print(f"   Relacionamentos: {rel_count}")

            # Listar labels
            result = session.run("CALL db.labels()")
            labels = [record["label"] for record in result]
            print(f"   Labels: {labels if labels else 'Nenhum'}")

            # Listar tipos de relacionamentos
            result = session.run("CALL db.relationshipTypes()")
            rel_types = [record["relationshipType"] for record in result]
            print(
                f"   Tipos de relacionamentos: {rel_types if rel_types else 'Nenhum'}"
            )

        driver.close()
        return True

    except Exception as e:
        print(f"❌ Erro ao obter informações: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 TESTE DE CONEXÃO NEO4J LOCAL - SIGMA PLI")
    print("=" * 60)

    # Testar conexão
    if test_local_connection():
        # Se conexão ok, mostrar informações do banco
        get_local_database_info()
        print("\n✅ Teste concluído com sucesso!")
    else:
        print("\n❌ Teste falhou. Verifique se o Neo4j local está rodando.")
        sys.exit(1)

    print("\n💡 Próximos passos:")
    print("   1. Execute o script de importação dos dados do dicionário")
    print("   2. Explore os dados usando o Neo4j Browser (http://localhost:7474)")
    print("   3. Teste a conexão com o Neo4j Aura quando estiver provisionado")
