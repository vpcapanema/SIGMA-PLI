// =============================================================================
// EXEMPLO PRÁTICO - TESTANDO A EXTENSÃO NEO4J NO VS CODE
// =============================================================================

// 🔥 PASSO 1: TESTE DE CONECTIVIDADE
// Execute esta query primeiro para confirmar que a extensão está conectada
RETURN "Extensão Neo4j funcionando!" AS status, 
       datetime() AS timestamp,
       "SIGMA PLI" AS projeto;

// 🔥 PASSO 2: VERIFICAR STATUS DO BANCO
// Veja quantos dados você já tem
MATCH (n) 
RETURN count(n) AS total_nos,
       [label IN labels(n) | label][0] AS primeiro_label
LIMIT 1;

// 🔥 PASSO 3: CRIAR DADOS DE TESTE SIMPLES
// Execute esta query para criar dados básicos
CREATE (p1:Pessoa {nome: "Ana Silva", cargo: "Designer"})
CREATE (p2:Pessoa {nome: "Bruno Costa", cargo: "Developer"})
CREATE (emp:Empresa {nome: "SIGMA Design", setor: "Criativo"})
CREATE (p1)-[:TRABALHA_EM]->(emp)
CREATE (p2)-[:TRABALHA_EM]->(emp)
RETURN "Dados criados!" AS resultado;

// 🔥 PASSO 4: VISUALIZAR OS DADOS
// Esta query vai mostrar um grafo visual na extensão
MATCH (p:Pessoa)-[r:TRABALHA_EM]->(e:Empresa)
RETURN p, r, e;

// 🔥 PASSO 5: CONSULTA COM PARÂMETROS
// Para usar parâmetros na extensão:
// 1. Execute a query abaixo
// 2. No painel da extensão, adicione parâmetros: {"cargo": "Designer"}
MATCH (p:Pessoa {cargo: $cargo})
RETURN p.nome AS nome, 
       p.cargo AS cargo;

// 🔥 PASSO 6: ANÁLISE DE DADOS
// Conte tipos de nós
MATCH (n)
RETURN labels(n) AS tipos, count(n) AS quantidade
ORDER BY quantidade DESC;

// 🔥 PASSO 7: LIMPEZA (OPCIONAL)
// Execute apenas se quiser limpar os dados de teste
// MATCH (n) DETACH DELETE n;

// =============================================================================
// DICAS PARA USAR A EXTENSÃO:
// =============================================================================

/*
1. 🎯 EXECUTAR QUERIES:
   - Selecione a query que quer executar
   - Use Ctrl+Enter ou clique no botão "Run" na extensão

2. 📊 VISUALIZAR RESULTADOS:
   - Aba "Table": Dados em tabela
   - Aba "Graph": Visualização do grafo (mais interessante!)
   - Aba "JSON": Dados brutos

3. 🔍 EXPLORAR SCHEMA:
   - Use o painel lateral da extensão
   - Veja labels, propriedades e relacionamentos
   - Clique para gerar queries automaticamente

4. ⚡ AUTOCOMPLETAR:
   - Digite "MATCH (" e veja as sugestões de labels
   - Digite "p." e veja as propriedades disponíveis
   - A extensão sugere funções Cypher automaticamente

5. 🎨 VISUALIZAÇÕES:
   - Queries que retornam nós e relacionamentos mostram gráficos
   - Use RETURN n, r, m para visualizações de grafo
   - Queries com apenas propriedades mostram tabelas

6. 📝 PARÂMETROS:
   - Use $parametro nas queries
   - Defina valores no painel da extensão
   - Formato JSON: {"parametro": "valor"}
*/

// =============================================================================
// QUERIES PRONTAS PARA TESTAR RECURSOS DA EXTENSÃO:
// =============================================================================

// 🎯 Teste 1: Autocompletar (digite e veja as sugestões)
MATCH (p:) // <- Complete aqui com Ctrl+Space

// 🎯 Teste 2: Visualização de grafo
MATCH (n)-[r]-(m) 
RETURN n, r, m 
LIMIT 10;

// 🎯 Teste 3: Tabela de resultados
MATCH (p:Pessoa)
RETURN p.nome AS nome, p.cargo AS cargo
ORDER BY nome;

// 🎯 Teste 4: Estatísticas (JSON)
CALL db.stats.retrieve('GRAPH COUNTS');

// 🎯 Teste 5: Schema do banco
CALL db.schema.visualization();

// =============================================================================
// PRÓXIMOS PASSOS:
// =============================================================================

/*
✅ 1. Execute as queries acima uma por uma
✅ 2. Experimente a visualização de grafo
✅ 3. Use o autocompletar ao escrever novas queries  
✅ 4. Explore o painel lateral da extensão
✅ 5. Teste queries com parâmetros
✅ 6. Abra o arquivo queries_neo4j_extension.cypher para mais exemplos
*/