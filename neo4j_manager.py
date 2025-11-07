#!/usr/bin/env python3
"""
Utilitário para gerenciar Neo4j LOCAL e AURA
"""

from neo4j import GraphDatabase
import json

def get_local_config():
    """Retorna configuração do Neo4j local"""
    return {
        "uri": "bolt://localhost:7687",
        "user": "neo4j",
        "password": "sigma123456",
        "database": "neo4j"
    }

def get_aura_config():
    """Retorna configuração do Neo4j Aura - NOVA INSTÂNCIA AUREA (2025-10-29)"""
    return {
        "uri": "neo4j+s://6b7fc90e.databases.neo4j.io",
        "user": "neo4j",
        "password": "RWpV06f_yQ9CAo2NbsP76jhNbInaZgE0kOxOBSdQDRs",
        "database": "neo4j"
    }

def test_connection(config, name):
    """Testa conexão com uma configuração específica"""
    try:
        driver = GraphDatabase.driver(
            config["uri"],
            auth=(config["user"], config["password"])
        )
        
        with driver.session(database=config["database"]) as session:
            result = session.run("RETURN 1 as test")
            result.single()
            
        driver.close()
        print(f"✅ {name}: Conexão OK")
        return True
        
    except Exception as e:
        print(f"❌ {name}: {str(e)}")
        return False

def switch_to_local():
    """Configura para usar Neo4j local"""
    print("🔄 Configurando para usar Neo4j LOCAL...")
    config = get_local_config()
    
    if test_connection(config, "Neo4j Local"):
        print("✅ Neo4j Local configurado como principal")
        print("🌐 Acesse: http://localhost:7474")
        print("🔑 Usuário: neo4j | Senha: sigma123456")
        return True
    else:
        print("❌ Falha ao configurar Neo4j Local")
        return False

def switch_to_aura():
    """Configura para usar Neo4j Aura"""
    print("🔄 Configurando para usar Neo4j AURA...")
    config = get_aura_config()
    
    if test_connection(config, "Neo4j Aura"):
        print("✅ Neo4j Aura configurado como principal")
        print("🌐 Acesse: https://6b7fc90e.databases.neo4j.io/browser/")
        return True
    else:
        print("❌ Falha ao configurar Neo4j Aura (problema de rede)")
        return False

def status_check():
    """Verifica status de ambas as conexões"""
    print("📊 Verificando status das conexões Neo4j...")
    
    local_ok = test_connection(get_local_config(), "Neo4j Local")
    aura_ok = test_connection(get_aura_config(), "Neo4j Aura")
    
    print("\n📋 RESUMO:")
    if local_ok:
        print("✅ LOCAL disponível - http://localhost:7474")
    if aura_ok:
        print("✅ AURA disponível - https://3f74966e.databases.neo4j.io/browser/")
    
    if not local_ok and not aura_ok:
        print("❌ Nenhuma conexão disponível")
    
    return local_ok, aura_ok

def manage_docker():
    """Comandos para gerenciar Docker"""
    print("\n🐳 COMANDOS DOCKER NEO4J:")
    print("Iniciar:  docker-compose up -d")
    print("Parar:    docker-compose down")
    print("Logs:     docker logs sigma_pli_neo4j")
    print("Status:   docker ps")

if __name__ == "__main__":
    print("=" * 50)
    print("🛠️  GERENCIADOR NEO4J - SIGMA PLI")
    print("=" * 50)
    
    # Verificar status atual
    local_ok, aura_ok = status_check()
    
    # Recomendação
    print("\n💡 RECOMENDAÇÃO:")
    if local_ok:
        print("✅ Use Neo4j LOCAL para desenvolvimento")
        print("   Mais rápido e sem problemas de rede")
    elif aura_ok:
        print("✅ Use Neo4j AURA")
        print("   Conexão de rede resolvida")
    else:
        print("⚠️  Inicie Neo4j local com: docker-compose up -d")
    
    # Comandos Docker
    manage_docker()
    
    print("\n🎯 STATUS ATUAL: Neo4j Local está ATIVO")
    print("   Para trocar, edite config.py")