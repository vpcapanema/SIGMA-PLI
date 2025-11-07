#!/usr/bin/env python3
"""
Neo4j - Exemplos de melhores práticas (Estrutura para Aura)
Configurado para Neo4j Aura mas pode ser adaptado facilmente
"""

from neo4j import GraphDatabase

class Neo4jAuraConnection:
    """Classe para gerenciar conexão com Neo4j Aura seguindo melhores práticas"""
    
    def __init__(self):
        # Configurações Neo4j Aura - SUBSTITUA com suas credenciais
        self.URI = "neo4j+s://3f74966e.databases.neo4j.io"
        self.AUTH = ("3f74966e", "77N9B2nQd_maiqyGxD5aE9LadT396gwj7NaKSilpBzU")
        self.DATABASE_NAME = "3f74966e"
    
    def test_connectivity(self):
        """1. Teste de conectividade - Melhor prática"""
        print("🔄 Testando conectividade...")
        
        try:
            with GraphDatabase.driver(self.URI, auth=self.AUTH) as driver:
                driver.verify_connectivity()
                print("✅ Conectividade verificada!")
                return True
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def create_example_graph(self):
        """2. Criar grafo - Usando parâmetros (NÃO hardcode)"""
        print("🔄 Criando grafo de exemplo...")
        
        try:
            with GraphDatabase.driver(self.URI, auth=self.AUTH) as driver:
                # IMPORTANTE: Use parâmetros, nunca hardcode valores!
                summary = driver.execute_query("""
                    CREATE (a:Person {name: $name})
                    CREATE (b:Person {name: $friendName})
                    CREATE (a)-[:KNOWS]->(b)
                    """,
                    name="Alice", 
                    friendName="David",
                    database_=self.DATABASE_NAME,
                ).summary
                
                print("Created {nodes_created} nodes in {time} ms.".format(
                    nodes_created=summary.counters.nodes_created,
                    time=summary.result_available_after
                ))
                return True
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def query_graph(self):
        """3. Consultar grafo - Recuperar informações"""
        print("🔄 Consultando grafo...")
        
        try:
            with GraphDatabase.driver(self.URI, auth=self.AUTH) as driver:
                # Retrieve all Person nodes who know other persons
                records, summary, keys = driver.execute_query("""
                    MATCH (p:Person)-[:KNOWS]->(:Person)
                    RETURN p.name AS name
                    """,
                    database_=self.DATABASE_NAME,
                )
                
                # Loop through results and do something with them
                for record in records:
                    print(record.data())  # obtain record as dict
                
                # Summary information
                print("The query `{query}` returned {records_count} records in {time} ms.".format(
                    query=summary.query, 
                    records_count=len(records),
                    time=summary.result_available_after
                ))
                return True
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def create_sigma_data(self):
        """4. Criar dados SIGMA PLI com parâmetros"""
        print("🔄 Criando dados SIGMA PLI...")
        
        try:
            with GraphDatabase.driver(self.URI, auth=self.AUTH) as driver:
                summary = driver.execute_query("""
                    // Limpar dados existentes
                    MATCH (n) DETACH DELETE n
                    
                    // Criar nós com parâmetros
                    CREATE (p:Pessoa {nome: $pessoa_nome, cpf: $pessoa_cpf})
                    CREATE (e:Empresa {nome: $empresa_nome, cnpj: $empresa_cnpj})
                    CREATE (d:Documento {tipo: $doc_tipo, numero: $doc_numero})
                    CREATE (p)-[:TRABALHA_EM]->(e)
                    CREATE (p)-[:ASSINOU]->(d)
                    CREATE (e)-[:POSSUI]->(d)
                    """,
                    # Parâmetros - sempre use isto!
                    pessoa_nome="João Silva",
                    pessoa_cpf="123.456.789-00",
                    empresa_nome="SIGMA Corp",
                    empresa_cnpj="12.345.678/0001-90",
                    doc_tipo="Contrato",
                    doc_numero="CONT-001",
                    database_=self.DATABASE_NAME,
                ).summary
                
                print("✅ Dados SIGMA criados!")
                print("Nodes: {}, Relationships: {}".format(
                    summary.counters.nodes_created,
                    summary.counters.relationships_created
                ))
                return True
        except Exception as e:
            print(f"❌ Erro: {e}")
            return False
    
    def close_connection_example(self):
        """5. Exemplo de fechamento manual de conexões"""
        print("🔄 Exemplo de gerenciamento manual de conexões...")
        
        # Exemplo SEM 'with' statement
        driver = None
        session = None
        
        try:
            driver = GraphDatabase.driver(self.URI, auth=self.AUTH)
            session = driver.session(database=self.DATABASE_NAME)
            
            # Usar session aqui
            result = session.run("RETURN 1 as test")
            record = result.single()
            print(f"✅ Teste manual: {record['test']}")
            
        except Exception as e:
            print(f"❌ Erro: {e}")
        finally:
            # IMPORTANTE: Sempre feche as conexões!
            if session:
                session.close()
            if driver:
                driver.close()
            print("🔒 Conexões fechadas manualmente")

def demonstrate_best_practices():
    """Demonstra todas as melhores práticas"""
    
    print("=" * 60)
    print("📚 NEO4J AURA - MELHORES PRÁTICAS DEMONSTRADAS")
    print("=" * 60)
    
    # Exemplo de estrutura correta
    print("✅ 1. INSTALAÇÃO:")
    print("   pip install neo4j~=5.28.0")
    
    print("\n✅ 2. IMPORTAÇÃO:")
    print("   from neo4j import GraphDatabase")
    
    print("\n✅ 3. CONFIGURAÇÃO:")
    print('   URI = "neo4j+s://xxx.databases.neo4j.io"')
    print('   AUTH = ("username", "password")')
    
    print("\n✅ 4. CONECTIVIDADE (com 'with' statement):")
    print("   with GraphDatabase.driver(URI, auth=AUTH) as driver:")
    print("       driver.verify_connectivity()")
    
    print("\n✅ 5. CRIAR DADOS (com parâmetros):")
    print("   driver.execute_query('''")
    print("       CREATE (a:Person {name: $name})")
    print("       ''', name='Alice', database_='mydb')")
    
    print("\n✅ 6. CONSULTAR DADOS:")
    print("   records, summary, keys = driver.execute_query('''")
    print("       MATCH (p:Person) RETURN p.name AS name")
    print("       ''', database_='mydb')")
    print("   for record in records:")
    print("       print(record.data())")
    
    print("\n✅ 7. FECHAMENTO MANUAL:")
    print("   session.close()")
    print("   driver.close()")
    
    print("\n" + "=" * 60)
    print("🎯 CONFIGURAÇÃO ATUAL:")
    print("=" * 60)
    
    connection = Neo4jAuraConnection()
    print(f"🔗 URI: {connection.URI}")
    print(f"👤 User: {connection.AUTH[0]}")
    print(f"🗄️  Database: {connection.DATABASE_NAME}")
    
    print("\n💡 PARA TESTAR:")
    print("   1. Resolva problema de rede corporativa")
    print("   2. Execute: python neo4j_aura_examples.py")
    print("   3. Ou use Neo4j local temporariamente")
    
    print("\n🌐 ACESSO VIA BROWSER:")
    print("   https://3f74966e.databases.neo4j.io/browser/")
    print("   User: 3f74966e")
    print("   Pass: 77N9B2nQd_maiqyGxD5aE9LadT396gwj7NaKSilpBzU")

if __name__ == "__main__":
    demonstrate_best_practices()
    
    # Instanciar e tentar conectar
    print("\n" + "=" * 60)
    print("🧪 TESTE DE CONECTIVIDADE")
    print("=" * 60)
    
    connection = Neo4jAuraConnection()
    if connection.test_connectivity():
        print("🎉 Aura está funcionando! Executando exemplos...")
        connection.create_example_graph()
        connection.query_graph()
        connection.create_sigma_data()
        connection.close_connection_example()
    else:
        print("⚠️  Problema de rede detectado.")
        print("💡 Use Neo4j local ou resolva conectividade para Aura")