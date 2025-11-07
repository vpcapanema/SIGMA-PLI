#!/usr/bin/env python3
"""
Teste de conexão com Neo4j LOCAL
"""

from neo4j import GraphDatabase
import time

# Configurações do Neo4j LOCAL
NEO4J_LOCAL_CONFIG = {
    "uri": "bolt://localhost:7687",
    "user": "neo4j",
    "password": "sigma123456",
    "database": "neo4j"
}

def test_local_connection():
    """Testa conexão com Neo4j local"""
    print("🔄 Testando conexão com Neo4j LOCAL...")
    print(f"   URI: {NEO4J_LOCAL_CONFIG['uri']}")
    print(f"   Usuário: {NEO4J_LOCAL_CONFIG['user']}")
    print(f"   Database: {NEO4J_LOCAL_CONFIG['database']}")
    
    try:
        # Criar driver
        driver = GraphDatabase.driver(
            NEO4J_LOCAL_CONFIG["uri"],
            auth=(NEO4J_LOCAL_CONFIG["user"], NEO4J_LOCAL_CONFIG["password"])
        )
        
        # Testar conexão
        with driver.session(database=NEO4J_LOCAL_CONFIG["database"]) as session:
            result = session.run("RETURN 'Hello Neo4j LOCAL!' as message, datetime() as timestamp")
            record = result.single()
            
            print(f"✅ Conexão estabelecida!")
            print(f"   Mensagem: {record['message']}")
            print(f"   Timestamp: {record['timestamp']}")
            
            # Verificar versão do Neo4j
            version_result = session.run("CALL dbms.components() YIELD name, versions, edition")
            for version_record in version_result:
                print(f"   Neo4j: {version_record['name']} {version_record['versions'][0]} {version_record['edition']}")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        return False

def create_sample_data():
    """Cria dados de exemplo para testar o grafo"""
    print("\n🔄 Criando dados de exemplo...")
    
    try:
        driver = GraphDatabase.driver(
            NEO4J_LOCAL_CONFIG["uri"],
            auth=(NEO4J_LOCAL_CONFIG["user"], NEO4J_LOCAL_CONFIG["password"])
        )
        
        with driver.session(database=NEO4J_LOCAL_CONFIG["database"]) as session:
            # Limpar dados existentes
            session.run("MATCH (n) DETACH DELETE n")
            
            # Criar nós de exemplo
            create_queries = [
                """
                CREATE (pessoa1:Pessoa {nome: 'João Silva', idade: 30, cpf: '123.456.789-00'})
                CREATE (pessoa2:Pessoa {nome: 'Maria Santos', idade: 25, cpf: '987.654.321-00'})
                CREATE (empresa:Empresa {nome: 'Tech Corp', cnpj: '12.345.678/0001-90'})
                CREATE (documento1:Documento {tipo: 'Contrato', numero: 'DOC001'})
                CREATE (documento2:Documento {tipo: 'Proposta', numero: 'DOC002'})
                """,
                """
                MATCH (p1:Pessoa {nome: 'João Silva'})
                MATCH (p2:Pessoa {nome: 'Maria Santos'})
                MATCH (e:Empresa {nome: 'Tech Corp'})
                MATCH (d1:Documento {numero: 'DOC001'})
                MATCH (d2:Documento {numero: 'DOC002'})
                CREATE (p1)-[:TRABALHA_EM]->(e)
                CREATE (p2)-[:TRABALHA_EM]->(e)
                CREATE (p1)-[:ASSINOU]->(d1)
                CREATE (p2)-[:CRIOU]->(d2)
                CREATE (e)-[:POSSUI]->(d1)
                CREATE (e)-[:POSSUI]->(d2)
                """
            ]
            
            for query in create_queries:
                session.run(query)
            
            # Verificar dados criados
            result = session.run("""
                MATCH (n) 
                RETURN labels(n) as labels, count(n) as count
            """)
            
            print("✅ Dados de exemplo criados:")
            for record in result:
                labels = record['labels']
                count = record['count']
                print(f"   {labels[0] if labels else 'No Label'}: {count} nós")
            
            # Verificar relacionamentos
            rel_result = session.run("""
                MATCH ()-[r]->() 
                RETURN type(r) as tipo, count(r) as count
            """)
            
            print("   Relacionamentos:")
            for record in rel_result:
                print(f"   {record['tipo']}: {record['count']}")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar dados: {str(e)}")
        return False

def get_database_info():
    """Obtém informações sobre o banco de dados"""
    print("\n📊 Informações do banco de dados:")
    
    try:
        driver = GraphDatabase.driver(
            NEO4J_LOCAL_CONFIG["uri"],
            auth=(NEO4J_LOCAL_CONFIG["user"], NEO4J_LOCAL_CONFIG["password"])
        )
        
        with driver.session(database=NEO4J_LOCAL_CONFIG["database"]) as session:
            # Contar nós
            result = session.run("MATCH (n) RETURN count(n) as node_count")
            node_count = result.single()["node_count"]
            print(f"   Total de nós: {node_count}")
            
            # Contar relacionamentos
            result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
            rel_count = result.single()["rel_count"]
            print(f"   Total de relacionamentos: {rel_count}")
            
            # Listar labels
            result = session.run("CALL db.labels()")
            labels = [record["label"] for record in result]
            print(f"   Labels disponíveis: {labels if labels else 'Nenhum'}")
            
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
    print("🚀 TESTE NEO4J LOCAL - SIGMA PLI")
    print("=" * 60)
    
    # Teste 1: Conexão básica
    if test_local_connection():
        print("\n🎉 Conexão LOCAL estabelecida com sucesso!")
        
        # Teste 2: Criar dados de exemplo
        if create_sample_data():
            print("\n✅ Dados de exemplo criados!")
            
            # Teste 3: Informações do banco
            get_database_info()
            
            print("\n" + "=" * 60)
            print("✅ CONFIGURAÇÃO COMPLETA!")
            print("=" * 60)
            print("🌐 Acesse Neo4j Browser: http://localhost:7474")
            print("🔑 Usuário: neo4j")
            print("🔒 Senha: sigma123456")
            print("\n💡 Comandos úteis:")
            print("   MATCH (n) RETURN n LIMIT 25  // Ver todos os nós")
            print("   MATCH p=()-[]->() RETURN p   // Ver relacionamentos")
            print("   CALL db.schema.visualization() // Visualizar schema")
            
        else:
            print("\n⚠️ Conexão OK, mas erro ao criar dados de exemplo")
    else:
        print("\n❌ Falha na conexão local")
        print("💡 Verifique se o container Docker está rodando:")
        print("   docker ps")
        print("   docker logs sigma_pli_neo4j")