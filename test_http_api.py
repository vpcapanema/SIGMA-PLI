#!/usr/bin/env python3
"""
Teste de conexão Neo4j usando HTTP API como alternativa
"""

import requests
import json
import base64

class Neo4jHTTPClient:
    def __init__(self, url, username, password):
        self.url = url.rstrip('/')
        self.username = username
        self.password = password
        self.headers = self._create_headers()
    
    def _create_headers(self):
        """Cria headers com autenticação básica"""
        credentials = f"{self.username}:{self.password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {encoded_credentials}',
            'Accept': 'application/json'
        }
    
    def test_connection(self):
        """Testa a conexão básica"""
        try:
            # Endpoint para informações do servidor
            response = requests.get(
                f"{self.url}/db/data/",
                headers=self.headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, data
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, str(e)
    
    def run_cypher(self, query, database="neo4j"):
        """Executa uma query Cypher via HTTP"""
        try:
            # Endpoint para queries transacionais
            url = f"{self.url}/db/{database}/tx/commit"
            
            payload = {
                "statements": [{
                    "statement": query
                }]
            }
            
            response = requests.post(
                url,
                headers=self.headers,
                data=json.dumps(payload),
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return True, data
            else:
                return False, f"HTTP {response.status_code}: {response.text}"
                
        except Exception as e:
            return False, str(e)

def test_http_api():
    """Testa conexão via HTTP API"""
    print("🌐 Testando conexão via HTTP API...")
    
    # URLs para testar
    urls_to_test = [
        "https://3f74966e.databases.neo4j.io",
        "https://3f74966e.databases.neo4j.io/db/3f74966e/query/v2"
    ]
    
    username = "3f74966e"
    password = "77N9B2nQd_maiqyGxD5aE9LadT396gwj7NaKSilpBzU"
    
    for url in urls_to_test:
        print(f"\n🔄 Testando URL: {url}")
        
        client = Neo4jHTTPClient(url, username, password)
        
        # Teste 1: Conexão básica
        success, result = client.test_connection()
        if success:
            print(f"✅ Conexão básica OK")
            print(f"   Neo4j Version: {result.get('neo4j_version', 'N/A')}")
            
            # Teste 2: Query simples
            success2, result2 = client.run_cypher("RETURN 'Hello Neo4j!' as message")
            if success2:
                print(f"✅ Query executada com sucesso!")
                if 'results' in result2 and result2['results']:
                    data = result2['results'][0]['data']
                    if data:
                        print(f"   Resultado: {data[0]['row'][0]}")
                return True
            else:
                print(f"❌ Erro na query: {result2}")
        else:
            print(f"❌ Erro na conexão: {result}")
    
    return False

def test_network_connectivity():
    """Testa conectividade de rede básica"""
    print("\n🔌 Testando conectividade de rede...")
    
    test_urls = [
        "https://httpbin.org/get",  # Teste geral de HTTP
        "https://neo4j.com",        # Site principal Neo4j
        "https://console.neo4j.io", # Console Neo4j
    ]
    
    for url in test_urls:
        try:
            response = requests.get(url, timeout=10)
            print(f"✅ {url} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {url} - Erro: {e}")

def check_proxy_settings():
    """Verifica configurações de proxy"""
    print("\n🔍 Verificando configurações de proxy...")
    
    try:
        # Tentar detectar proxy do sistema
        import urllib.request
        proxies = urllib.request.getproxies()
        
        if proxies:
            print("⚠️ Proxies detectados:")
            for key, value in proxies.items():
                print(f"   {key}: {value}")
            print("   Isso pode estar causando problemas de conexão com Neo4j Aura")
        else:
            print("✅ Nenhum proxy detectado")
            
    except Exception as e:
        print(f"❌ Erro ao verificar proxy: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 DIAGNÓSTICO AVANÇADO DE CONECTIVIDADE NEO4J")
    print("=" * 60)
    
    # Teste 1: Conectividade geral
    test_network_connectivity()
    
    # Teste 2: Configurações de proxy
    check_proxy_settings()
    
    # Teste 3: HTTP API
    http_success = test_http_api()
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    if http_success:
        print("🎉 SUCESSO! Conexão estabelecida via HTTP API")
        print("💡 Recomendação: Use HTTP API para queries até resolver problema do driver")
    else:
        print("❌ Todos os testes falharam")
        print("\n🛠️ PRÓXIMOS PASSOS:")
        print("   1. Verificar configurações de firewall/proxy")
        print("   2. Tentar de uma rede diferente")
        print("   3. Contatar suporte Neo4j se problema persistir")
        print("   4. Aguardar mais tempo (até 15-20 minutos) para estabilização")
    
    print(f"\n💻 Para acessar via navegador, tente:")
    print(f"   - Modo privado/incógnito")
    print(f"   - Navegador diferente")
    print(f"   - Desabilitar extensões temporariamente")