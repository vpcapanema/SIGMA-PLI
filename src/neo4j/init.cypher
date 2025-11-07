// Criar constraints para garantir unicidade
CREATE CONSTRAINT arquivo_id IF NOT EXISTS FOR (a:Arquivo) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT produtor_id IF NOT EXISTS FOR (p:Produtor) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT perfil_id IF NOT EXISTS FOR (p:Perfil) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT extensao_id IF NOT EXISTS FOR (e:Extensao) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT estrutura_id IF NOT EXISTS FOR (e:Estrutura) REQUIRE e.id IS UNIQUE;
CREATE CONSTRAINT conteudo_id IF NOT EXISTS FOR (c:Conteudo) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT instituicao_id IF NOT EXISTS FOR (i:Instituicao) REQUIRE i.id IS UNIQUE;
CREATE CONSTRAINT pessoa_id IF NOT EXISTS FOR (p:Pessoa) REQUIRE p.id IS UNIQUE;
CREATE CONSTRAINT camada_id IF NOT EXISTS FOR (c:Camada) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT tabela_id IF NOT EXISTS FOR (t:Tabela) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT tema_id IF NOT EXISTS FOR (t:Tema) REQUIRE t.id IS UNIQUE;

// Criar índices para melhorar performance de busca
CREATE INDEX arquivo_nome IF NOT EXISTS FOR (a:Arquivo) ON (a.nome);
CREATE INDEX produtor_nome IF NOT EXISTS FOR (p:Produtor) ON (p.nome);
CREATE INDEX perfil_nome IF NOT EXISTS FOR (p:Perfil) ON (p.nome);
CREATE INDEX extensao_nome IF NOT EXISTS FOR (e:Extensao) ON (e.nome);
CREATE INDEX instituicao_nome IF NOT EXISTS FOR (i:Instituicao) ON (i.nome);
CREATE INDEX pessoa_nome IF NOT EXISTS FOR (p:Pessoa) ON (p.nome);
CREATE INDEX tema_nome IF NOT EXISTS FOR (t:Tema) ON (t.nome);

// Criar alguns nós de exemplo para Perfil e Extensao (conforme documentação)
MERGE (p1:Perfil {id: "tabular", nome: "Tabular"})
MERGE (p2:Perfil {id: "geoespacial_vetor", nome: "Geoespacial Vetor"})
MERGE (p3:Perfil {id: "geoespacial_raster", nome: "Geoespacial Raster"})
MERGE (p4:Perfil {id: "documentos_texto", nome: "Documentos Texto"})
MERGE (p5:Perfil {id: "midia", nome: "Mídia"})
MERGE (p6:Perfil {id: "nuvem_pontos", nome: "Nuvem de Pontos"})
MERGE (p7:Perfil {id: "desenho_2d3d", nome: "Desenho 2D/3D"})
MERGE (p8:Perfil {id: "database", nome: "Database"})
MERGE (p9:Perfil {id: "geodatabase", nome: "Geodatabase"})
MERGE (p10:Perfil {id: "pacote", nome: "Pacote"})

// Criar algumas extensões e relacioná-las aos perfis
MERGE (e1:Extensao {id: "csv", nome: ".csv"})
MERGE (e2:Extensao {id: "shp", nome: ".shp"})
MERGE (e3:Extensao {id: "geotiff", nome: ".tiff"})
MERGE (e4:Extensao {id: "pdf", nome: ".pdf"})
MERGE (e5:Extensao {id: "mp4", nome: ".mp4"})
MERGE (e6:Extensao {id: "las", nome: ".las"})
MERGE (e7:Extensao {id: "dwg", nome: ".dwg"})
MERGE (e8:Extensao {id: "sql", nome: ".sql"})
MERGE (e9:Extensao {id: "gdb", nome: ".gdb"})
MERGE (e10:Extensao {id: "zip", nome: ".zip"})

// Criar relacionamentos entre Perfis e Extensões
MERGE (p1)-[:ACEITA_EXTENSAO]->(e1)
MERGE (p2)-[:ACEITA_EXTENSAO]->(e2)
MERGE (p3)-[:ACEITA_EXTENSAO]->(e3)
MERGE (p4)-[:ACEITA_EXTENSAO]->(e4)
MERGE (p5)-[:ACEITA_EXTENSAO]->(e5)
MERGE (p6)-[:ACEITA_EXTENSAO]->(e6)
MERGE (p7)-[:ACEITA_EXTENSAO]->(e7)
MERGE (p8)-[:ACEITA_EXTENSAO]->(e8)
MERGE (p9)-[:ACEITA_EXTENSAO]->(e9)
MERGE (p10)-[:ACEITA_EXTENSAO]->(e10);
