#!/usr/bin/env python3
"""
Teste específico para Neo4j Aura com diferentes configurações
"""

from neo4j import GraphDatabase
import sys

def test_connection_variants():
    """Testa diferentes variações de conexão"""
    
    # Configurações base
    uri = "neo4j+s://3f74966e.databases.neo4j.io"
    password = "77N9B2nQd_maiqyGxD5aE9LadT396gwj7NaKSilpBzU"
    
    # Variações para testar
    test_configs = [
        {"user": "3f74966e", "database": "neo4j", "desc": "Usuário específico + banco padrão"},
        {"user": "neo4j", "database": "neo4j", "desc": "Usuário padrão + banco padrão"},
        {"user": "3f74966e", "database": "3f74966e", "desc": "Usuário específico + banco específico"},
        {"user": "neo4j", "database": "3f74966e", "desc": "Usuário padrão + banco específico"},
    ]
    
    for i, config in enumerate(test_configs, 1):
        print(f"\n{i}️⃣ Testando: {config['desc']}")
        print(f"   Usuário: {config['user']}")
        print(f"   Database: {config['database']}")
        
        try:
            # Criar driver com configurações específicas
            driver = GraphDatabase.driver(
                uri,
                auth=(config['user'], password),
                connection_timeout=30,
                max_connection_lifetime=300
            )
            
            # Testar conexão
            with driver.session(database=config['database']) as session:
                result = session.run("RETURN 'Conexão OK!' as message, datetime() as timestamp")
                record = result.single()
                
                print(f"   ✅ SUCESSO!")
                print(f"   Mensagem: {record['message']}")
                print(f"   Timestamp: {record['timestamp']}")
                
                # Obter informações do servidor
                server_info = session.run("CALL dbms.components() YIELD name, versions, edition")
                for info in server_info:
                    print(f"   Neo4j: {info['name']} {info['versions'][0]} {info['edition']}")
                
            driver.close()
            return True, config
            
        except Exception as e:
            print(f"   ❌ Erro: {str(e)}")
            continue
    
    return False, None

def test_browser_connection():
    """Testa a conexão que funcionaria no Neo4j Browser"""
    print("\n🌐 Testando conexão estilo Browser...")
    
    try:
        driver = GraphDatabase.driver(
            "neo4j+s://3f74966e.databases.neo4j.io",
            auth=("3f74966e", "77N9B2nQd_maiqyGxD5aE9LadT396gwj7NaKSilpBzU")
        )
        
        # Não especificar database - deixar o padrão
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            print(f"   ✅ Conexão Browser OK: {record['test']}")
            
            # Verificar qual database estamos usando
            db_result = session.run("CALL db.info()")
            for db_info in db_result:
                print(f"   Database atual: {db_info.get('name', 'N/A')}")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Erro Browser: {str(e)}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 TESTE AVANÇADO NEO4J AURA - MÚLTIPLAS CONFIGURAÇÕES")
    print("=" * 60)
    
    # Testar diferentes variações
    success, working_config = test_connection_variants()
    
    if success:
        print(f"\n🎉 CONEXÃO ESTABELECIDA COM SUCESSO!")
        print(f"📋 Configuração que funcionou:")
        print(f"   Usuário: {working_config['user']}")
        print(f"   Database: {working_config['database']}")
    else:
        print(f"\n❌ Nenhuma configuração funcionou")
        
        # Testar conexão estilo browser como último recurso
        browser_success = test_browser_connection()
        
        if not browser_success:
            print(f"\n🔍 POSSÍVEIS CAUSAS:")
            print(f"   1. A instância ainda está inicializando completamente")
            print(f"   2. Firewall ou proxy bloqueando a conexão")
            print(f"   3. Problema temporário na rede")
            print(f"   4. Configuração específica do Neo4j Aura")
            
            print(f"\n🛠️ SOLUÇÕES:")
            print(f"   1. Aguarde mais 2-3 minutos e tente novamente")
            print(f"   2. Teste via Neo4j Browser: https://3f74966e.databases.neo4j.io/browser/")
            print(f"   3. Verifique o status no console: https://console.neo4j.io")
    
    print(f"\n" + "=" * 60)