// Import relationships

// arquivo -> pasta
LOAD CSV WITH HEADERS FROM 'file:///neo4j_dicionario_de_dados/rels_arquivo_em_pasta.csv' AS row
MATCH (a:Arquivo {id: row.arquivo_id}), (p:Pasta {id: row.pasta_id})
MERGE (a)-[:EM_PASTA]->(p);

// arquivo -> dataset
LOAD CSV WITH HEADERS FROM 'file:///neo4j_dicionario_de_dados/rels_arquivo_refere_dataset.csv' AS row
MATCH (a:Arquivo {id: row.arquivo_id}), (d:Dataset {id: row.dataset_id})
MERGE (a)-[:REFERE_DATASET]->(d);

// dataset -> camada
LOAD CSV WITH HEADERS FROM 'file:///neo4j_dicionario_de_dados/rels_dataset_publicado_como_camada.csv' AS row
MATCH (d:Dataset {id: row.dataset_id}), (c:Camada {id: row.camada_id})
MERGE (d)-[:PUBLICADO_COMO]->(c);

// arquivo -> instituicao
LOAD CSV WITH_HEADERS FROM 'file:///neo4j_dicionario_de_dados/rels_arquivo_produzido_por_instituicao.csv' AS row
MATCH (a:Arquivo {id: row.arquivo_id}), (i:Instituicao {id: row.instituicao_id})
MERGE (a)-[:PRODUZIDO_POR]->(i);

// arquivo -> pessoa (autor)
LOAD CSV WITH_HEADERS FROM 'file:///neo4j_dicionario_de_dados/rels_arquivo_autor_pessoa.csv' AS row
MATCH (a:Arquivo {id: row.arquivo_id}), (ps:Pessoa {id: row.pessoa_id})
MERGE (a)-[:AUTOR]->(ps);

// arquivo -> tag
LOAD CSV WITH HEADERS FROM 'file:///neo4j_dicionario_de_dados/rels_arquivo_tem_tag.csv' AS row
MATCH (a:Arquivo {id: row.arquivo_id}), (t:Tag {id: row.tag_id})
MERGE (a)-[:TEM_TAG]->(t);

// dataset -> tag
LOAD CSV WITH HEADERS FROM 'file:///neo4j_dicionario_de_dados/rels_dataset_tem_tag.csv' AS row
MATCH (d:Dataset {id: row.dataset_id}), (t:Tag {id: row.tag_id})
MERGE (d)-[:TEM_TAG]->(t);

// camada -> tag
LOAD CSV WITH HEADERS FROM 'file:///neo4j_dicionario_de_dados/rels_camada_tem_tag.csv' AS row
MATCH (c:Camada {id: row.camada_id}), (t:Tag {id: row.tag_id})
MERGE (c)-[:TEM_TAG]->(t);

// dataset -> licenca
LOAD CSV WITH HEADERS FROM 'file:///neo4j_dicionario_de_dados/rels_dataset_licenciado_por.csv' AS row
MATCH (d:Dataset {id: row.dataset_id}), (l:Licenca {id: row.licenca_id})
MERGE (d)-[:LICENCIADO_POR]->(l);

// arquivo precede arquivo
LOAD CSV WITH HEADERS FROM 'file:///neo4j_dicionario_de_dados/rels_arquivo_precede_arquivo.csv' AS row
MATCH (a1:Arquivo {id: row.arquivo_id_atual}), (a2:Arquivo {id: row.arquivo_id_anterior})
MERGE (a1)-[:PRECEDE]->(a2);
