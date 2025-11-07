from neo4j import GraphDatabase

# Usar Neo4j local
URI = 'bolt://localhost:7687'
AUTH = ('neo4j', 'sigma123456')

try:
    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        driver.verify_connectivity()
        print('✅ Conexão Neo4j Local verificada com sucesso!')

        # Criar grafo de exemplo
        summary = driver.execute_query(
            "CREATE (a:Person {name: $name}) CREATE (b:Person {name: $friendName}) CREATE (a)-[:KNOWS]->(b)",
            name='Alice', friendName='David',
            database_='neo4j',
        ).summary

        print('✅ Grafo criado com sucesso!')
        print('Criados {nodes_created} nós em {time} ms.'.format(
            nodes_created=summary.counters.nodes_created,
            time=summary.result_available_after
        ))

        # Query o grafo
        records, summary, keys = driver.execute_query(
            "MATCH (p:Person)-[:KNOWS]->(:Person) RETURN p.name AS name",
            database_='neo4j',
        )

        print('\n📋 Pessoas que conhecem outras:')
        for record in records:
            print('-', record['name'])

        print('\nQuery retornou {records_count} registros em {time} ms.'.format(
            records_count=len(records),
            time=summary.result_available_after
        ))

except Exception as e:
    print('❌ Erro:', str(e))