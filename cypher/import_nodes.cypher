// Import nodes from CSV templates (execute from project root where `neo4j_dicionario_de_dados` is located)

// Projeto
LOAD CSV WITH HEADERS FROM 'file:///neo4j_dicionario_de_dados/nodes_projeto.csv' AS row
MERGE (p:Projeto {id: row.id})
SET p.nome = row.nome, p.sigla = row.sigla, p.descricao = row.descricao, p.status = row.status,
    p.data_inicio = row.data_inicio, p.data_fim = row.data_fim;

// Instituicao
LOAD CSV WITH HEADERS FROM 'file:///neo4j_dicionario_de_dados/nodes_instituicao.csv' AS row
MERGE (i:Instituicao {id: row.id})
SET i.nome = row.nome, i.sigla = row.sigla, i.cnpj = row.cnpj, i.tipo = row.tipo;

// Pessoa
LOAD CSV WITH HEADERS FROM 'file:///neo4j_dicionario_de_dados/nodes_pessoa.csv' AS row
MERGE (ps:Pessoa {id: row.id})
SET ps.nome = row.nome, ps.email = row.email, ps.funcao = row.funcao, ps.instituicao_id = row.instituicao_id;

// Licenca
LOAD CSV WITH HEADERS FROM 'file:///neo4j_dicionario_de_dados/nodes_licenca.csv' AS row
MERGE (l:Licenca {id: row.id})
SET l.nome = row.nome, l.url = row.url, l.codigo = row.codigo;

// Tag
LOAD CSV WITH HEADERS FROM 'file:///neo4j_dicionario_de_dados/nodes_palavra_chave.csv' AS row
MERGE (t:Tag {id: row.id})
SET t.tag = row.tag;

// Dataset
LOAD CSV WITH HEADERS FROM 'file:///neo4j_dicionario_de_dados/nodes_dataset.csv' AS row
MERGE (d:Dataset {id: row.id})
SET d.titulo = row.titulo, d.descricao = row.descricao, d.tema = row.tema, d.cobertura_espacial = row.cobertura_espacial,
    d.cobertura_temporal_inicio = row.cobertura_temporal_inicio, d.cobertura_temporal_fim = row.cobertura_temporal_fim,
    d.formato_principal = row.formato_principal, d.srid = row.srid, d.licenca_id = row.licenca_id, d.projeto_id = row.projeto_id;

// Camada
LOAD CSV WITH HEADERS FROM 'file:///neo4j_dicionario_de_dados/nodes_camada.csv' AS row
MERGE (c:Camada {id: row.id})
SET c.nome = row.nome, c.tipo = row.tipo, c.srid = row.srid, c.formato = row.formato, c.url_publicacao = row.url_publicacao,
    c.servico = row.servico, c.projeto_id = row.projeto_id, c.dataset_id = row.dataset_id, c.estilo = row.estilo;

// Pasta
LOAD CSV WITH HEADERS FROM 'file:///neo4j_dicionario_de_dados/nodes_pasta.csv' AS row
MERGE (pasta:Pasta {id: row.id})
SET pasta.caminho = row.caminho, pasta.nome = row.nome, pasta.nivel = row.nivel, pasta.pai_id = row.pai_id, pasta.projeto_id = row.projeto_id;

// Arquivo
LOAD CSV WITH HEADERS FROM 'file:///neo4j_dicionario_de_dados/nodes_arquivo.csv' AS row
MERGE (a:Arquivo {id: row.id})
SET a.nome = row.nome, a.extensao = row.extensao, a.mime_type = row.mime_type, a.tamanho_bytes = row.tamanho_bytes,
    a.hash_sha256 = row.hash_sha256, a.versao = row.versao, a.caminho = row.caminho, a.data_criacao = row.data_criacao,
    a.data_modificacao = row.data_modificacao, a.tipo_documento = row.tipo_documento, a.resumo = row.resumo,
    a.projeto_id = row.projeto_id, a.instituicao_id = row.instituicao_id, a.pessoa_autor_id = row.pessoa_autor_id;
