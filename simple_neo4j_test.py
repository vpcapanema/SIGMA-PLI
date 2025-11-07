#!/usr/bin/env python3
"""
Teste simples de conexão Neo4j com timeout mais longo
"""

from neo4j import GraphDatabase
import time

def simple_test():
    """Teste mais simples possível"""
    print("🔄 Iniciando teste simples...")
    
    try:
        print("1. Criando driver...")
        driver = GraphDatabase.driver(
            "neo4j+s://3f74966e.databases.neo4j.io",
            auth=("3f74966e", "77N9B2nQd_maiqyGxD5aE9LadT396gwj7NaKSilpBzU"),
            connection_timeout=60,  # 60 segundos
            max_connection_lifetime=600  # 10 minutos
        )
        
        print("2. Driver criado com sucesso")
        
        print("3. Aguardando 5 segundos...")
        time.sleep(5)
        
        print("4. Verificando conectividade...")
        driver.verify_connectivity()
        
        print("✅ SUCESSO! Conexão estabelecida")
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro: {e}")
        return False

def test_with_cypher():
    """Teste executando uma query Cypher simples"""
    print("\n🔄 Testando com query Cypher...")
    
    try:
        driver = GraphDatabase.driver(
            "neo4j+s://3f74966e.databases.neo4j.io",
            auth=("3f74966e", "77N9B2nQd_maiqyGxD5aE9LadT396gwj7NaKSilpBzU"),
            connection_timeout=60,
            encrypted=True
        )
        
        with driver.session() as session:
            # Query mais simples possível
            result = session.run("RETURN 42 as answer")
            record = result.single()
            answer = record["answer"]
            
            print(f"✅ Query executada! Resposta: {answer}")
            
            # Verificar informações do banco
            info_result = session.run("CALL dbms.components() YIELD name, versions RETURN name, versions[0] as version LIMIT 1")
            info_record = info_result.single()
            if info_record:
                print(f"✅ Neo4j {info_record['name']} versão {info_record['version']}")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na query: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("🧪 TESTE SIMPLES NEO4J AURA")
    print("=" * 50)
    
    # Teste 1: Conectividade básica
    success1 = simple_test()
    
    if success1:
        # Teste 2: Query Cypher
        success2 = test_with_cypher()
        
        if success2:
            print("\n🎉 AMBOS OS TESTES PASSARAM!")
            print("✅ Sua conexão Neo4j Aura está funcionando perfeitamente!")
        else:
            print("\n⚠️ Conectividade OK, mas há problemas com queries")
    else:
        print("\n❌ Problemas de conectividade básica")
        print("💡 Possíveis soluções:")
        print("   1. Aguardar mais alguns minutos")
        print("   2. Verificar se a instância está Running no console")
        print("   3. Tentar acessar via Neo4j Browser primeiro")
    
    print("\n" + "=" * 50)