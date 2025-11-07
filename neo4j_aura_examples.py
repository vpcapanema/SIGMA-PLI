#!/usr/bin/env python3
"""
Neo4j Aura - Exemplos usando melhores práticas
Baseado na documentação oficial Neo4j 5.28.0
"""

from neo4j import GraphDatabase
from src.backend.config import NEO4J_CONFIG

# 1. Configuração usando as credenciais do Aura
URI = NEO4J_CONFIG["uri"]  # "neo4j+s://3f74966e.databases.neo4j.io"
AUTH = (NEO4J_CONFIG["user"], NEO4J_CONFIG["password"])
DATABASE_NAME = NEO4J_CONFIG["database"]  # "3f74966e"

def test_connectivity():
    """1. Teste de conectividade"""
    print("🔄 Testando conectividade com Neo4j Aura...")
    
    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            driver.verify_connectivity()
            print("✅ Conectividade verificada com sucesso!")
            return True
    except Exception as e:
        print(f"❌ Erro de conectividade: {e}")
        return False

def create_example_graph():
    """2. Criar grafo de exemplo"""
    print("\n🔄 Criando grafo de exemplo...")
    
    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            # Usar execute_query com parâmetros - NÃO hardcode!
            summary = driver.execute_query("""
                CREATE (a:Person {name: $name})
                CREATE (b:Person {name: $friendName})
                CREATE (a)-[:KNOWS]->(b)
                """,
                name="Alice", 
                friendName="David",
                database_=DATABASE_NAME,
            ).summary
            
            print("✅ Grafo criado com sucesso!")
            print("Created {nodes_created} nodes in {time} ms.".format(
                nodes_created=summary.counters.nodes_created,
                time=summary.result_available_after
            ))
            return True
            
    except Exception as e:
        print(f"❌ Erro ao criar grafo: {e}")
        return False

def query_graph():
    """3. Consultar grafo"""
    print("\n🔄 Consultando grafo...")
    
    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            # Recuperar todas as pessoas que conhecem outras pessoas
            records, summary, keys = driver.execute_query("""
                MATCH (p:Person)-[:KNOWS]->(:Person)
                RETURN p.name AS name
                """,
                database_=DATABASE_NAME,
            )
            
            print("✅ Consulta executada com sucesso!")
            
            # Loop pelos resultados
            print("📋 Resultados:")
            for record in records:
                print(f"   - {record.data()}")  # obter record como dict
            
            # Informações do resumo
            print("The query `{query}` returned {records_count} records in {time} ms.".format(
                query=summary.query, 
                records_count=len(records),
                time=summary.result_available_after
            ))
            
            return True
            
    except Exception as e:
        print(f"❌ Erro na consulta: {e}")
        return False

def create_sigma_pli_data():
    """4. Criar dados específicos do SIGMA PLI"""
    print("\n🔄 Criando dados do SIGMA PLI...")
    
    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            # Limpar dados existentes primeiro
            driver.execute_query("""
                MATCH (n) DETACH DELETE n
                """,
                database_=DATABASE_NAME,
            )
            
            # Criar estrutura do SIGMA PLI
            summary = driver.execute_query("""
                // Criar pessoas
                CREATE (p1:Pessoa {nome: $pessoa1_nome, cpf: $pessoa1_cpf, cargo: $pessoa1_cargo})
                CREATE (p2:Pessoa {nome: $pessoa2_nome, cpf: $pessoa2_cpf, cargo: $pessoa2_cargo})
                
                // Criar empresa
                CREATE (emp:Empresa {nome: $empresa_nome, cnpj: $empresa_cnpj, setor: $empresa_setor})
                
                // Criar documentos
                CREATE (doc1:Documento {tipo: $doc1_tipo, numero: $doc1_numero, status: $doc1_status})
                CREATE (doc2:Documento {tipo: $doc2_tipo, numero: $doc2_numero, status: $doc2_status})
                
                // Criar relacionamentos
                CREATE (p1)-[:TRABALHA_EM {desde: $p1_desde}]->(emp)
                CREATE (p2)-[:TRABALHA_EM {desde: $p2_desde}]->(emp)
                CREATE (p1)-[:ASSINOU {data: $doc1_data}]->(doc1)
                CREATE (p2)-[:CRIOU {data: $doc2_data}]->(doc2)
                CREATE (emp)-[:POSSUI]->(doc1)
                CREATE (emp)-[:POSSUI]->(doc2)
                """,
                # Parâmetros - NÃO hardcode!
                pessoa1_nome="João Silva",
                pessoa1_cpf="123.456.789-00",
                pessoa1_cargo="Gerente",
                pessoa2_nome="Maria Santos",
                pessoa2_cpf="987.654.321-00", 
                pessoa2_cargo="Analista",
                empresa_nome="SIGMA Tecnologia",
                empresa_cnpj="12.345.678/0001-90",
                empresa_setor="Tecnologia",
                doc1_tipo="Contrato",
                doc1_numero="CONT-001",
                doc1_status="Ativo",
                doc2_tipo="Relatório",
                doc2_numero="REL-001",
                doc2_status="Finalizado",
                p1_desde="2023-01-15",
                p2_desde="2023-03-10",
                doc1_data="2024-01-10",
                doc2_data="2024-02-15",
                database_=DATABASE_NAME,
            ).summary
            
            print("✅ Dados SIGMA PLI criados!")
            print("Created {nodes_created} nodes and {relationships_created} relationships in {time} ms.".format(
                nodes_created=summary.counters.nodes_created,
                relationships_created=summary.counters.relationships_created,
                time=summary.result_available_after
            ))
            return True
            
    except Exception as e:
        print(f"❌ Erro ao criar dados SIGMA PLI: {e}")
        return False

def query_sigma_pli_data():
    """5. Consultas específicas do SIGMA PLI"""
    print("\n🔄 Executando consultas SIGMA PLI...")
    
    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            
            # Consulta 1: Pessoas e suas empresas
            print("\n📋 1. Pessoas e suas empresas:")
            records1, _, _ = driver.execute_query("""
                MATCH (p:Pessoa)-[t:TRABALHA_EM]->(e:Empresa)
                RETURN p.nome AS pessoa, p.cargo AS cargo, e.nome AS empresa, t.desde AS desde
                ORDER BY p.nome
                """,
                database_=DATABASE_NAME,
            )
            
            for record in records1:
                data = record.data()
                print(f"   {data['pessoa']} ({data['cargo']}) -> {data['empresa']} (desde {data['desde']})")
            
            # Consulta 2: Documentos por empresa
            print("\n📋 2. Documentos por empresa:")
            records2, _, _ = driver.execute_query("""
                MATCH (e:Empresa)-[:POSSUI]->(d:Documento)
                RETURN e.nome AS empresa, collect(d.tipo + ' ' + d.numero) AS documentos
                """,
                database_=DATABASE_NAME,
            )
            
            for record in records2:
                data = record.data()
                print(f"   {data['empresa']}: {', '.join(data['documentos'])}")
            
            # Consulta 3: Rede de relacionamentos
            print("\n📋 3. Rede de relacionamentos:")
            records3, summary3, _ = driver.execute_query("""
                MATCH path = (p:Pessoa)-[r]-(target)
                RETURN p.nome AS pessoa, type(r) AS relacao, 
                       CASE 
                           WHEN 'Empresa' IN labels(target) THEN target.nome 
                           WHEN 'Documento' IN labels(target) THEN target.tipo + ' ' + target.numero
                           ELSE 'Outro'
                       END AS destino
                ORDER BY p.nome, relacao
                """,
                database_=DATABASE_NAME,
            )
            
            for record in records3:
                data = record.data()
                print(f"   {data['pessoa']} --[{data['relacao']}]--> {data['destino']}")
            
            print(f"\n✅ Consultas executadas em {summary3.result_available_after} ms")
            return True
            
    except Exception as e:
        print(f"❌ Erro nas consultas: {e}")
        return False

def get_database_summary():
    """6. Resumo do banco de dados"""
    print("\n🔄 Obtendo resumo do banco...")
    
    try:
        with GraphDatabase.driver(URI, auth=AUTH) as driver:
            
            # Contar nós por label
            records1, _, _ = driver.execute_query("""
                MATCH (n)
                RETURN labels(n) AS labels, count(n) AS count
                ORDER BY count DESC
                """,
                database_=DATABASE_NAME,
            )
            
            print("📊 Nós por tipo:")
            total_nodes = 0
            for record in records1:
                data = record.data()
                label = data['labels'][0] if data['labels'] else 'No Label'
                count = data['count']
                total_nodes += count
                print(f"   {label}: {count}")
            
            # Contar relacionamentos por tipo
            records2, _, _ = driver.execute_query("""
                MATCH ()-[r]->()
                RETURN type(r) AS tipo, count(r) AS count
                ORDER BY count DESC
                """,
                database_=DATABASE_NAME,
            )
            
            print("\n📊 Relacionamentos por tipo:")
            total_rels = 0
            for record in records2:
                data = record.data()
                total_rels += data['count']
                print(f"   {data['tipo']}: {data['count']}")
            
            print(f"\n📈 Total: {total_nodes} nós, {total_rels} relacionamentos")
            return True
            
    except Exception as e:
        print(f"❌ Erro ao obter resumo: {e}")
        return False

def main():
    """Função principal que executa todos os exemplos"""
    print("=" * 60)
    print("🚀 NEO4J AURA - SIGMA PLI - MELHORES PRÁTICAS")
    print("=" * 60)
    print(f"🔗 URI: {URI}")
    print(f"👤 User: {AUTH[0]}")
    print(f"🗄️  Database: {DATABASE_NAME}")
    print("=" * 60)
    
    # 1. Teste de conectividade
    if not test_connectivity():
        print("❌ Falha na conectividade. Verifique:")
        print("   - Conexão com internet")
        print("   - Credenciais Neo4j Aura")
        print("   - Status da instância no console")
        return False
    
    # 2. Criar grafo de exemplo
    create_example_graph()
    
    # 3. Consultar grafo de exemplo
    query_graph()
    
    # 4. Criar dados SIGMA PLI
    create_sigma_pli_data()
    
    # 5. Consultar dados SIGMA PLI
    query_sigma_pli_data()
    
    # 6. Resumo do banco
    get_database_summary()
    
    print("\n" + "=" * 60)
    print("✅ TODOS OS EXEMPLOS EXECUTADOS!")
    print("=" * 60)
    print("🌐 Acesse o Neo4j Browser:")
    print(f"   {NEO4J_CONFIG['aura_url']}")
    print("🔑 Credenciais:")
    print(f"   Usuário: {NEO4J_CONFIG['user']}")
    print(f"   Senha: {NEO4J_CONFIG['password']}")
    print("\n💡 Comandos úteis no Browser:")
    print("   MATCH (n) RETURN n LIMIT 25")
    print("   MATCH p=()-[]->() RETURN p")
    print("   CALL db.schema.visualization()")
    
    return True

if __name__ == "__main__":
    main()