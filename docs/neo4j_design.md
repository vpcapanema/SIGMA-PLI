# Modelo Neo4j — SIGMA PLI

Resumo do modelo de grafo gerado a partir dos templates CSV fornecidos em `csv_templates_SIGMA_PLI.zip`.

Nodes (Labels) e propriedades (tipos inferidos)
- **Projeto** (`Projeto`)
  - `id` (string, PK), `nome` (string), `sigla` (string), `descricao` (string), `status` (string -> enum {em_andamento, concluido, planejado}), `data_inicio` (date), `data_fim` (date)
- **Instituicao** (`Instituicao`)
  - `id` (string, PK), `nome` (string), `sigla` (string), `cnpj` (string | nullable), `tipo` (string)
- **Pessoa** (`Pessoa`)
  - `id` (string, PK), `nome` (string), `email` (string | nullable), `funcao` (string | nullable), `instituicao_id` (string | FK -> Instituicao.id)
- **Dataset** (`Dataset`)
  - `id` (string), `titulo` (string), `descricao` (string | nullable), `tema` (string | nullable), `cobertura_espacial` (string | e.g. 'SP' ou 'Brasil'), `cobertura_temporal_inicio` (date), `cobertura_temporal_fim` (date), `formato_principal` (string), `srid` (string | ex: 'EPSG:4674'), `licenca_id` (string | FK -> Licenca.id), `projeto_id` (string | FK -> Projeto.id)
Cardinalidade observada (inferida dos templates)
- `Projeto 1..1` — cada projeto tem id único
- `Instituicao 1..1` — cada instituicao tem id único
- `Pessoa 0..1 instituicao` — campo `instituicao_id` pode ser nulo
- `Dataset -> Licenca 0..1` — `licenca_id` pode ser nulo
- `Arquivo` pode referenciar `projeto`, `instituicao` e `pessoa_autor` (todos opcionais nos templates)

Observações sobre tipos e limpeza de dados
- Datas estão no formato `YYYY-MM-DD` — converter para `date()` em Cypher se necessário.
- Campos vazios nos CSVs aparecem como string vazia ou como NULL; o importer Python trata '' como None automaticamente.

- **Projeto** (`Projeto`)
  - `id` (string, PK), `nome`, `sigla`, `descricao`, `status`, `data_inicio`, `data_fim`
- **Instituicao** (`Instituicao`)
  - `id` (string, PK), `nome`, `sigla`, `cnpj`, `tipo`
- **Pessoa** (`Pessoa`)
  - `id` (string, PK), `nome`, `email`, `funcao`, `instituicao_id`
- **Licenca** (`Licenca`)
  - `id`, `nome`, `url`, `codigo`
- **PalavraChave** (`Tag`)
  - `id`, `tag`
- **Dataset** (`Dataset`)
  - `id`, `titulo`, `descricao`, `tema`, `cobertura_espacial`, `cobertura_temporal_inicio`, `cobertura_temporal_fim`, `formato_principal`, `srid`, `licenca_id`, `projeto_id`
- **Camada** (`Camada`)
  - `id`, `nome`, `tipo`, `srid`, `formato`, `url_publicacao`, `servico`, `projeto_id`, `dataset_id`, `estilo`
- **Arquivo** (`Arquivo`)
  - `id`, `nome`, `extensao`, `mime_type`, `tamanho_bytes`, `hash_sha256`, `versao`, `caminho`, `data_criacao`, `data_modificacao`, `tipo_documento`, `resumo`, `projeto_id`, `instituicao_id`, `pessoa_autor_id`
- **Pasta** (`Pasta`)
  - `id`, `caminho`, `nome`, `nivel`, `pai_id`, `projeto_id`

Relações (tipos e mapeamento)
- `(:Arquivo)-[:EM_PASTA]->(:Pasta)` — de `rels_arquivo_em_pasta.csv` (arquivo_id -> pasta_id)
- `(:Arquivo)-[:REFERE_DATASET]->(:Dataset)` — de `rels_arquivo_refere_dataset.csv` (arquivo_id -> dataset_id)
- `(:Dataset)-[:PUBLICADO_COMO]->(:Camada)` — de `rels_dataset_publicado_como_camada.csv` (dataset_id -> camada_id)
- `(:Arquivo)-[:PRODUZIDO_POR]->(:Instituicao)` — de `rels_arquivo_produzido_por_instituicao.csv` (arquivo_id -> instituicao_id)
- `(:Arquivo)-[:AUTOR]->(:Pessoa)` — de `rels_arquivo_autor_pessoa.csv` (arquivo_id -> pessoa_id)
- `(:Arquivo)-[:TEM_TAG]->(:Tag)` — de `rels_arquivo_tem_tag.csv` (arquivo_id -> tag_id)
- `(:Dataset)-[:TEM_TAG]->(:Tag)` — de `rels_dataset_tem_tag.csv` (dataset_id -> tag_id)
- `(:Camada)-[:TEM_TAG]->(:Tag)` — de `rels_camada_tem_tag.csv` (camada_id -> tag_id)
- `(:Dataset)-[:LICENCIADO_POR]->(:Licenca)` — de `rels_dataset_licenciado_por.csv` (dataset_id -> licenca_id)
- `(:Arquivo)-[:PRECEDE]->(:Arquivo)` — de `rels_arquivo_precede_arquivo.csv` (arquivo_id_atual -> arquivo_id_anterior)

Constraints recomendadas
- Para cada label com `id`: `CREATE CONSTRAINT ON (n:Label) ASSERT n.id IS UNIQUE;`

Ordem de importação recomendada
1. Criar constraints
2. Importar nodes sem dependências (Instituicao, Licenca, Tag, Projeto)
3. Importar nodes com referências (Pessoa, Dataset, Camada, Pasta, Arquivo)
4. Importar relações (rels_*)

Estratégia de import
- Para datasets pequenos/medianos: usar `LOAD CSV WITH HEADERS` e `MERGE` por `id`.
- Para grandes volumes: usar `neo4j-admin import` (formato específico) ou um importer Python em lotes com transações.

Exemplo de fluxo (Cypher)
1. `:source import constraints.cypher`
2. `:source import_nodes.cypher`
3. `:source import_rels.cypher`

Notas
- O arquivo `Modelo_Dicionario_SIGMA_PLI.xlsx` pode conter descrições, tipos e cardinalidade detalhados; recomendo enriquecer este documento após análise das planilhas.
# Design do Grafo Neo4j

Este documento descreve o modelo de grafo Neo4j usado pelo projeto, os nós, propriedades, relacionamentos, constraints e o processo automático de sincronização a partir do PostgreSQL.

## Visão geral

- Fonte relacional: esquema `dicionario` no PostgreSQL (tabelas `arquivo`, `produtor`, `arquivo_produtor`).
- Destino grafo: Neo4j (nós `Arquivo`, `Produtor` e relacionamentos `PRODUZIDO_POR`).
- Sincronização: script Python `src/backend/app/db/neo4j_sync.py` (usa `neo4j` driver e `psycopg2`).

## Nós e propriedades

### Arquivo (Label: `Arquivo`)
- id: identificador (UUID/string) — chave única.
- nome: string — nome do arquivo.
- hash: string — hash do arquivo (se disponível).
- mime_type: string — tipo MIME.
- data_upload: string (ISO8601) — data/hora de upload.

Exemplo de criação/merge (Cypher):

```
MERGE (a:Arquivo {id: '...})
SET a.nome = '...', a.hash = '...', a.mime_type = '...', a.data_upload = '...'
```

### Produtor (Label: `Produtor`)
- id: identificador (UUID/string) — chave única.
- nome: string — nome do produtor.
- email: string — e-mail de contato.
- departamento: string — departamento ou unidade.

Exemplo de criação/merge (Cypher):

```
MERGE (p:Produtor {id: '...'} )
SET p.nome = '...', p.email = '...', p.departamento = '...'
```

## Relacionamentos

- `(:Arquivo)-[:PRODUZIDO_POR]->(:Produtor)`

Exemplo de criação (Cypher):

```
MATCH (a:Arquivo {id: $arquivo_id})
MATCH (p:Produtor {id: $produtor_id})
MERGE (a)-[:PRODUZIDO_POR]->(p)
```

## Constraints e índices

Recomenda-se criar constraints de unicidade nas propriedades `id` de cada label.

Exemplos:

```
CREATE CONSTRAINT IF NOT EXISTS arquivo_id FOR (a:Arquivo) REQUIRE a.id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS produtor_id FOR (p:Produtor) REQUIRE p.id IS UNIQUE;
```

Observações:
- Dependendo do volume, adicionar índices em propriedades frequentemente consultadas pode acelerar buscas.

## Processo de sincronização (implementação atual)

- O script `src/backend/app/db/neo4j_sync.py` realiza:
  1. Leitura das tabelas PostgreSQL via `psycopg2` (configurações via `DATABASE_URL` environment variable).
  2. Busca registros de `dicionario.arquivo`, `dicionario.produtor` e os pares em `dicionario.arquivo_produtor`.
  3. Usando um `neo4j` driver, executa `MERGE` por nó para inserir/atualizar propriedades e `MERGE` para relacionamentos.
  4. Cria constraints de unicidade (método `create_constraints`).

### Como rodar (local/infra existente)

1. Defina variáveis de ambiente (exemplo):

```powershell
SET NEO4J_URI=bolt://<neo4j-host>:7687
SET NEO4J_USER=neo4j
SET NEO4J_PASSWORD=<senha>
SET DATABASE_URL=postgresql://<user>:<pass>@<host>:5432/sigma_pli
```

2. Execute (no ambiente do backend):

```powershell
python src\backend\app\db\neo4j_sync.py
```

Ou importe e use as classes em um processo maior (ex.: endpoint ou job agendado).

## Estratégias de sincronização incremental

- Atualmente o script faz `MERGE` para todos os registros retornados (full sync). Para produção recomenda-se:
  - Implementar watermark por `data_update`/`data_upload` e sincronizar apenas registros novos/alterados.
  - Usar filas (ex.: Kafka/Service Bus) para alterações em tempo real que disparem pequenas sincronizações.
  - Registrar checkpoints e reconciliar periodicamente (full reconcile noturno).

## Mapeamentos e conversões

- UUIDs do Postgres são convertidos para string ao inserir nos nós.
- Datas são convertidas para ISO8601 via `.isoformat()` no script.

## Tratamento de erros e idempotência

- O uso de `MERGE` torna a sincronização idempotente por chave `id`.
- Em caso de falha parcial, reexecutar o script reaplica `MERGE` e corrige dados inconsistentes.
- Recomenda-se adicionar logs estruturados e métricas (sucesso/erro, contagem de nós/relacionamentos processados).

## Requisitos e permissões

- Neo4j: credenciais com permissões para criar constraints e escrever nós/relacionamentos.
- Postgres: usuário com permissão de leitura nas tabelas `dicionario.*`.

## Testes e validação

- Teste inicial: criar um pequeno conjunto de dados no Postgres e rodar o script em ambiente de teste; validar nós e relacionamentos com queries Cypher.
- Validação contínua: executar queries de amostragem (ex.: contar nós por label, checar relacionamentos esperados).

## Próximas melhorias sugeridas

- Documentar mais labels e propriedades conforme o dicionário de dados completo.
- Suportar mais tipos de nós (ex.: `VersaoArquivo`, `Workflow`) conforme a necessidade do grafo.
- Implementar sincronização incremental e monitoramento (jobs + alertas).
# Especificação do Modelo Neo4j

Este documento descreve o modelo de grafo Neo4j usado pelo projeto (nós, propriedades, relacionamentos, constraints) e o processo de sincronização a partir do PostgreSQL.

Status: rascunho gerado automaticamente a partir do código em `src/backend/app/db/neo4j_sync.py` e `neo4j_queries.py`. Revise e ajuste conforme necessário.

## Objetivo

- Representar entidades principais do domínio (ex.: `Arquivo`, `Produtor`) como nós no grafo.
- Permitir consultas semânticas, grafos de relacionamento e buscas por propriedades que complementem o modelo relacional no PostgreSQL (fonte de verdade).

## Labels / Nós

- `:Arquivo`
  - Propriedades observadas no código: `id`, `nome`, `hash`, `mime_type`, `data_upload`.
  - Observações: `id` é usado como identificador único (string/UUID).

- `:Produtor`
  - Propriedades observadas: `id`, `nome`, `email`, `departamento`.

Outros nodes podem ser adicionados conforme necessidade (ex.: `VersaoArquivo`, `Workflow`), mas não há implementação explícita no código atual.

## Relacionamentos

- `(Arquivo)-[:PRODUZIDO_POR]->(Produtor)`
  - Criado a partir da tabela `dicionario.arquivo_produtor` no PostgreSQL.
  - Use `MERGE` para evitar duplicações durante sincronização.

## Constraints e Indexes no Neo4j

- Constraints sugeridas (criadas por `create_constraints` no sync):
  - `CREATE CONSTRAINT arquivo_id IF NOT EXISTS FOR (a:Arquivo) REQUIRE a.id IS UNIQUE`
  - `CREATE CONSTRAINT produtor_id IF NOT EXISTS FOR (p:Produtor) REQUIRE p.id IS UNIQUE`

Recomenda-se criar indexes adicionais em propriedades frequentemente consultadas (ex.: `nome`, `email`) dependendo das consultas.

## Processo de sincronização (Resumo técnico)

- Origem: PostgreSQL (`dicionario.arquivo`, `dicionario.produtor`, `dicionario.arquivo_produtor`).
- Ferramenta: `src/backend/app/db/neo4j_sync.py`.
- Passos executados pelo sync:
  1. Lê `arquivo` do Postgres e gera `MERGE (a:Arquivo {id: $id}) SET ...` com propriedades.
  2. Lê `produtor` e faz `MERGE (p:Produtor {id: $id}) SET ...`.
 3. Lê relacionamentos (`arquivo_produtor`) e cria `MERGE (a)-[:PRODUZIDO_POR]->(p)`.
 4. Garante constraints únicas no Neo4j.

### Como rodar o sync (exemplo)

1. Configure variáveis de ambiente para conexão Neo4j e Postgres (ou edite o script `config.py`):

```powershell
setx NEO4J_URI bolt://<neo4j-host>:7687
setx NEO4J_USER neo4j
setx NEO4J_PASSWORD <senha>
setx DATABASE_URL postgresql://<user>:<pass>@<host>:5432/sigma_pli
```

2. Execute (na pasta `src/backend`):

```powershell
python -u app\db\neo4j_sync.py
```

Observação: o script atual usa `MERGE` e escreve no Neo4j; execute em ambiente de teste antes de rodar em produção.

## Exemplos de consultas úteis

- Obter relacionamentos de um arquivo:

```cypher
MATCH (a:Arquivo {id: $id})
OPTIONAL MATCH (a)-[r]->(n)
RETURN a, collect(DISTINCT {type: type(r), node: n}) as relacionamentos
```

- Buscar arquivos por termo (simples):

```cypher
MATCH (n)
WHERE (n:Arquivo OR n:Produtor) AND any(prop in keys(n) WHERE toString(n[prop]) CONTAINS $termo)
RETURN n, labels(n)
```

## Integração com PostgreSQL (AWS)

- O PostgreSQL permanece a fonte de verdade para dados tabulares e versões.
- Neo4j é usado como camada de grafo derivada (indexação/visualização/consulta semântica).
- Recomendações:
  - Garantir que o usuário de leitura no Postgres tenha permissões mínimas necessárias para as consultas do `neo4j_sync`.
  - Usar conexões seguras (SSL) ao acessar o Postgres na AWS.

## Observações operacionais

- Deploy do Neo4j em Azure:
  - Atualmente scaffoldado como Azure Container Instance (ACI) no `infra/azure` — bom para dev/test.
  - Para produção, preferir AKS com volumes persistentes ou VMs com discos gerenciados.
  - Configurar backups e monitoramento do container/VM.

- Segurança:
  - Não deixar senhas em código; usar Key Vault para Neo4j e parâmetros do Terraform.
  - Rotacionar credenciais periodicamente.

## Próximos passos sugeridos

1. Revisar e aprovar este rascunho; integrar no `sigma_pli_documento_teorico_conceitual_e_especificacao_de_dados_v_1.md` se desejar.
2. Implementar um modo `--dry-run` no `neo4j_sync.py` para validar mapeamentos antes de aplicar.
3. Adicionar testes de integração e um job agendado para sincronização incremental.

---
Arquivo gerado automaticamente. Peça para eu adaptar ou mover o conteúdo para o documento principal.
