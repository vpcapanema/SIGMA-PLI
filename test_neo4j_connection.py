#!/usr/bin/env python3
"""
Script para testar conexão com Neo4j Aura
"""

from neo4j import GraphDatabase
import sys

# Configurações do Neo4j Aura - NOVA INSTÂNCIA AUREA (2025-10-29)
NEO4J_CONFIG = {
    "uri": "neo4j+s://6b7fc90e.databases.neo4j.io",
    "user": "neo4j",  # Username específico da instância
    "password": "RWpV06f_yQ9CAo2NbsP76jhNbInaZgE0kOxOBSdQDRs",
    "database": "neo4j",  # Nome do banco específico da instância
    "instance_id": "6b7fc90e",
    "instance_name": "SIGMA-PLI-NEO4J",
    "aura_url": "https://6b7fc90e.databases.neo4j.io/db/neo4j/query/v2"
}

def test_connection():
    """Testa a conexão com o Neo4j Aura"""
    
    # Verifica se a senha foi configurada
    if not NEO4J_CONFIG["password"]:
        print("❌ ERRO: Você precisa configurar a senha do Neo4j!")
        print("   Edite este arquivo e substitua a senha vazia pela sua senha do Neo4j Aura.")
        return False
    
    try:
        print("🔄 Testando conexão com Neo4j Aura...")
        print(f"   URI: {NEO4J_CONFIG['uri']}")
        print(f"   Usuário: {NEO4J_CONFIG['user']}")
        print(f"   Database: {NEO4J_CONFIG['database']}")
        
        # Criar driver
        driver = GraphDatabase.driver(
            NEO4J_CONFIG["uri"],
            auth=(NEO4J_CONFIG["user"], NEO4J_CONFIG["password"])
        )
        
        # Testar conexão executando uma query simples
        with driver.session(database=NEO4J_CONFIG["database"]) as session:
            result = session.run("RETURN 'Hello Neo4j Aura!' as message")
            record = result.single()
            message = record["message"]
            
            print(f"✅ Conexão bem-sucedida!")
            print(f"   Resposta do servidor: {message}")
            
            # Verificar versão do Neo4j
            version_result = session.run("CALL dbms.components() YIELD name, versions, edition")
            for record in version_result:
                print(f"   Neo4j {record['name']} {record['versions'][0]} {record['edition']}")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        print("\n💡 Dicas para resolver:")
        print("   1. Verifique se a senha está correta")
        print("   2. Confirme se a instância Neo4j Aura está ativa")
        print("   3. Verifique sua conexão com a internet")
        return False

def get_database_info():
    """Obtém informações sobre o banco de dados"""
    
    if not NEO4J_CONFIG["password"]:
        print("❌ Configure a senha primeiro!")
        return False
    
    try:
        driver = GraphDatabase.driver(
            NEO4J_CONFIG["uri"],
            auth=(NEO4J_CONFIG["user"], NEO4J_CONFIG["password"])
        )
        
        with driver.session(database=NEO4J_CONFIG["database"]) as session:
            print("\n📊 Informações do banco de dados:")
            
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
            print(f"   Tipos de relacionamentos: {rel_types if rel_types else 'Nenhum'}")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao obter informações: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 TESTE DE CONEXÃO NEO4J AURA - SIGMA PLI")
    print("=" * 60)
    
    # Testar conexão
    if test_connection():
        # Se conexão ok, mostrar informações do banco
        get_database_info()
        print("\n✅ Teste concluído com sucesso!")
    else:
        print("\n❌ Teste falhou. Verifique as configurações.")
        sys.exit(1)
    
    print("\n💡 Próximos passos:")
    print("   1. Configure sua senha no arquivo de configuração")
    print("   2. Execute o script de importação dos dados")
    print("   3. Explore os dados usando o Neo4j Browser")
    print(f"   4. Acesse: {NEO4J_CONFIG['aura_url']}")