#!/usr/bin/env python3
"""
Script de diagnóstico avançado para Neo4j Aura
"""

from neo4j import GraphDatabase
import requests
import time
import socket

# Configurações do Neo4j Aura
NEO4J_CONFIG = {
    "uri": "neo4j+s://3f74966e.databases.neo4j.io",
    "user": "3f74966e",
    "password": "77N9B2nQd_maiqyGxD5aE9LadT396gwj7NaKSilpBzU",
    "database": "3f74966e",
    "instance_id": "3f74966e",
    "instance_name": "Instance01",
    "aura_url": "https://3f74966e.databases.neo4j.io/db/3f74966e/query/v2"
}

def test_dns_resolution():
    """Testa resolução DNS"""
    try:
        hostname = "3f74966e.databases.neo4j.io"
        ip = socket.gethostbyname(hostname)
        print(f"✅ DNS OK - {hostname} → {ip}")
        return True
    except Exception as e:
        print(f"❌ Erro DNS: {e}")
        return False

def test_web_access():
    """Testa acesso via HTTPS"""
    try:
        url = NEO4J_CONFIG["aura_url"]
        response = requests.get(url, timeout=10)
        print(f"✅ Web OK - Status: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Erro Web: {e}")
        return False

def test_simple_connection():
    """Teste de conexão mais simples"""
    try:
        print("🔄 Testando conexão básica...")
        driver = GraphDatabase.driver(
            NEO4J_CONFIG["uri"],
            auth=(NEO4J_CONFIG["user"], NEO4J_CONFIG["password"]),
            max_connection_lifetime=30,
            max_connection_pool_size=50,
            connection_timeout=20,
            resolver=None
        )
        
        # Verificar se o driver foi criado
        print("✅ Driver criado com sucesso")
        
        # Testar verificação do driver
        driver.verify_connectivity()
        print("✅ Conectividade verificada")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão básica: {e}")
        return False

def test_with_default_database():
    """Testa com database padrão"""
    try:
        print("🔄 Testando com database 'neo4j'...")
        driver = GraphDatabase.driver(
            NEO4J_CONFIG["uri"],
            auth=(NEO4J_CONFIG["user"], NEO4J_CONFIG["password"])
        )
        
        with driver.session(database="neo4j") as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            print(f"✅ Conexão com 'neo4j' OK: {record['test']}")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro com database 'neo4j': {e}")
        return False

def test_with_original_credentials():
    """Testa com credenciais padrão"""
    try:
        print("🔄 Testando com usuário 'neo4j'...")
        driver = GraphDatabase.driver(
            NEO4J_CONFIG["uri"],
            auth=("neo4j", NEO4J_CONFIG["password"])
        )
        
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            print(f"✅ Conexão com 'neo4j' OK: {record['test']}")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"❌ Erro com usuário 'neo4j': {e}")
        return False

def diagnose_all():
    """Executa todos os testes de diagnóstico"""
    print("=" * 60)
    print("🔍 DIAGNÓSTICO COMPLETO NEO4J AURA")
    print("=" * 60)
    
    print("\n1️⃣ Testando resolução DNS...")
    dns_ok = test_dns_resolution()
    
    print("\n2️⃣ Testando acesso web...")
    web_ok = test_web_access()
    
    print("\n3️⃣ Testando conexão básica...")
    basic_ok = test_simple_connection()
    
    print("\n4️⃣ Testando com database padrão...")
    default_db_ok = test_with_default_database()
    
    print("\n5️⃣ Testando com usuário padrão...")
    default_user_ok = test_with_original_credentials()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    print(f"DNS Resolution:     {'✅' if dns_ok else '❌'}")
    print(f"Web Access:         {'✅' if web_ok else '❌'}")
    print(f"Basic Connection:   {'✅' if basic_ok else '❌'}")
    print(f"Default Database:   {'✅' if default_db_ok else '❌'}")
    print(f"Default User:       {'✅' if default_user_ok else '❌'}")
    
    # Recomendações
    print("\n💡 RECOMENDAÇÕES:")
    if not dns_ok:
        print("   - Verifique sua conexão com a internet")
    if not web_ok:
        print("   - A instância pode ainda estar inicializando")
        print("   - Aguarde alguns minutos e tente novamente")
    if not any([basic_ok, default_db_ok, default_user_ok]):
        print("   - Verifique se a instância está ativa no console Neo4j")
        print("   - Confirme se as credenciais estão corretas")
        print("   - A instância pode levar alguns minutos para ficar disponível")
    
    return any([basic_ok, default_db_ok, default_user_ok])

if __name__ == "__main__":
    success = diagnose_all()
    
    print(f"\n🎯 Status final: {'✅ SUCESSO' if success else '❌ FALHA'}")
    
    if not success:
        print("\n⏳ AGUARDE: Instâncias Neo4j Aura podem levar de 2-5 minutos para ficarem disponíveis")
        print("   Tente novamente em alguns minutos!")