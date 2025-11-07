from neo4j import GraphDatabase

URI = 'bolt://localhost:7687'
AUTH = ('neo4j', 'sigma123456')

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    with driver.session() as session:
        print('🎯 CONSULTAS SIGMA-PLI NO NEO4J LOCAL\n')

        # Query 1: Arquivos e seus produtores
        print('1️⃣ Arquivos e Instituições Produtoras:')
        result = session.run('''
            MATCH (a:Arquivo)-[:PRODUZIDO_POR]->(i:Instituicao)
            RETURN a.id AS arquivo, i.nome AS instituicao
        ''')
        for record in result:
            print(f'   📄 {record["arquivo"]} → 🏛️ {record["instituicao"]}')

        # Query 2: Datasets e suas camadas
        print('\n2️⃣ Datasets publicados como camadas:')
        result = session.run('''
            MATCH (d:Dataset)-[:PUBLICADO_COMO]->(c:Camada)
            RETURN d.id AS dataset, c.nome AS camada, c.servico AS servico
        ''')
        for record in result:
            print(f'   📊 {record["dataset"]} → 🗺️ {record["camada"]} ({record["servico"]})')

        # Query 3: Pessoas e seus projetos
        print('\n3️⃣ Participantes do projeto:')
        result = session.run('''
            MATCH (p:Pessoa)-[:PARTICIPA_DE]->(proj:Projeto)
            RETURN p.nome AS pessoa, proj.nome AS projeto
        ''')
        for record in result:
            print(f'   👤 {record["pessoa"]} → 📋 {record["projeto"]}')

        # Query 4: Tags em arquivos
        print('\n4️⃣ Tags associadas aos arquivos:')
        result = session.run('''
            MATCH (a:Arquivo)-[:TEM_TAG]->(t:Tag)
            RETURN a.id AS arquivo, t.tag AS tag
        ''')
        for record in result:
            print(f'   🏷️ {record["arquivo"]} → #{record["tag"]}')