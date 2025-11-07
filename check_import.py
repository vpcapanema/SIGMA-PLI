from neo4j import GraphDatabase

URI = 'bolt://localhost:7687'
AUTH = ('neo4j', 'sigma123456')

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    with driver.session() as session:
        # Contar nós por tipo
        result = session.run('MATCH (n) RETURN labels(n) AS tipo, count(n) AS quantidade ORDER BY quantidade DESC')
        print('📊 Nós no grafo:')
        for record in result:
            print(f'  {record["tipo"]}: {record["quantidade"]}')

        # Contar relacionamentos por tipo
        result2 = session.run('MATCH ()-[r]->() RETURN type(r) AS tipo_rel, count(r) AS quantidade ORDER BY quantidade DESC')
        print('\n🔗 Relacionamentos no grafo:')
        for record in result2:
            print(f'  {record["tipo_rel"]}: {record["quantidade"]}')

        # Verificar alguns nós específicos
        result3 = session.run('MATCH (p:Projeto) RETURN p.nome, p.id LIMIT 3')
        print('\n🏗️ Projetos encontrados:')
        for record in result3:
            print(f'  {record["p.id"]}: {record["p.nome"]}')