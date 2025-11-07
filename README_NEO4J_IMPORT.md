Resumo rápido — importar CSVs para Neo4j

Pré-requisitos
- Neo4j disponível (local, container ou Aura)
- CSVs no diretório `neo4j_dicionario_de_dados` (conforme `csv_templates_SIGMA_PLI.zip`)
- Dependências Python: `pip install -r requirements.txt`

Import via Cypher (simples)
1. Inicie o Neo4j e coloque os arquivos CSV na pasta `import` do Neo4j (ou ajuste paths `file:///` para apontar para os CSVs)
2. No `cypher/constraints.cypher`, `cypher/import_nodes.cypher` e `cypher/import_rels.cypher` execute via `cypher-shell` ou `Neo4j Browser` via `:source`.

Import via Python (controle e batches)
1. Copie a pasta `neo4j_dicionario_de_dados` para o projeto root (já existe no workspace)
2. Rode (dry-run):

```powershell
python .\importer\neo4j_importer.py --dry-run
```

3. Para executar contra um Neo4j ativo:

```powershell
python .\importer\neo4j_importer.py --uri bolt://host:7687 --user neo4j --password S3nh@Segura
```

Notas de segurança
- Nunca comite credenciais no repositório. Use variáveis de ambiente ou Azure Key Vault / HashiCorp Vault quando for automatizar.
- Para Neo4j Aura use credenciais temporárias e seguras.
