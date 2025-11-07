# Parecer Tecnico SIGMA-PLI

Data: 2025-10-31
Responsavel: GitHub Copilot

## Inventario Geral

### Raiz do repositorio

- [x] .env (inventariado; nao inspecionado por conter segredos)
- [x] .github/ (ver Capitulo 9)
- [x] .last_home.html (ver Capitulo 0)
- [x] .pytest_cache/ (ver Capitulo 14)
- [x] .venv/ (ambiente virtual; fora do escopo do parecer)
- [x] .vscode/ (ver Capitulo 14)
- [x] 00_PARECER/ (este parecer)
- [x] app/ (ver Capitulo 1)
- [x] app_minimal.py (ver Capitulo 0)
- [x] app_simple.py (ver Capitulo 0)
- [x] app_test.py (ver Capitulo 0)
- [x] check_import.py (ver Capitulo 0)
- [x] cypher/ (ver Capitulo 5)
- [x] database.json (ver Capitulo 0)
- [x] ddl_modulo_autenticacao.sql (ver Capitulo 0)
- [x] ddl_sigma_pli_completo.sql (ver Capitulo 0)
- [x] detalhes_rds_sigma_pli.txt (ver Capitulo 0)
- [x] detect_neo4j_desktop.py (ver Capitulo 0)
- [x] diagnose_neo4j.py (ver Capitulo 0)
- [x] diagnose_neo4j_detailed.py (ver Capitulo 0)
- [x] docker-compose-neo4j-local.yml (ver Capitulo 0)
- [x] docker-compose.yml (ver Capitulo 0)
- [x] docs/ (ver Capitulo 6)
- [x] explore_db.sql (ver Capitulo 0)
- [x] GUIA_IMPLEMENTACAO_COMPLETO.md (ver Capitulo 0)
- [x] GUIA_NEO4J_VSCODE.md (ver Capitulo 0)
- [x] implementacao_sigma_pli_completa.sql (ver Capitulo 0)
- [x] importer/ (ver Capitulo 7)
- [x] infra/ (ver Capitulo 8)
- [x] migracao_dados_csv_legado.sql (ver Capitulo 0)
- [x] neo4j_aura_examples.py (ver Capitulo 0)
- [x] neo4j_best_practices.py (ver Capitulo 0)
- [x] neo4j_extension_config.md (ver Capitulo 0)
- [x] neo4j_manager.py (ver Capitulo 0)
- [x] neo4j_vscode_guide.md (ver Capitulo 0)
- [x] network_diagnostic.bat (ver Capitulo 0)
- [x] profiles/ (ver Capitulo 10)
- [x] queries_neo4j_extension.cypher (ver Capitulo 5)
- [x] README_NEO4J_IMPORT.md (ver Capitulo 6)
- [x] RELATORIO_TECNICO_IMPLEMENTACAO.md (ver Capitulo 0)
- [x] reports/ (ver Capitulo 11)
- [x] requirements.txt (ver Capitulo 0)
- [x] scripts/ (ver Capitulo 12)
- [x] sigma_pli_documento_teorico_conceitual_e_especificacao_de_dados_v_1.md (ver Capitulo 0)
- [x] sigma_pli_queries.cypher (ver Capitulo 5)
- [x] sigma_pli_queries.py (ver Capitulo 0)
- [x] Sigma-pli - Documento Teorico-conceitual E Especificacao De Dados_v1.docx (ver Capitulo 0)
- [x] simple_neo4j_test.py (ver Capitulo 0)
- [x] src/ (ver Capitulo 13)
- [x] static/ (ver Capitulo 2)
- [x] SUGESTAO_VISUAL/ (ver Capitulo 0)
- [x] templates/ (ver Capitulo 3)
- [x] teste_extensao_neo4j.cypher (ver Capitulo 5)
- [x] tests/ (ver Capitulo 4)
- [x] test_advanced_neo4j.py (ver Capitulo 0)
- [x] test_http_api.py (ver Capitulo 0)
- [x] test_local_neo4j.py (ver Capitulo 0)
- [x] test_neo4j.bat (ver Capitulo 0)
- [x] test_neo4j_connection.py (ver Capitulo 0)
- [x] test_neo4j_direct.py (ver Capitulo 0)
- [x] test_neo4j_example.py (ver Capitulo 0)
- [x] test_neo4j_functions.py (ver Capitulo 0)
- [x] test_neo4j_local.py (ver Capitulo 0)
- [x] triggers_auditoria_completos.sql (ver Capitulo 0)
- [x] v1.code-workspace (ver Capitulo 0)
- [x] v1.code-workspace1.code-workspace (ver Capitulo 0)
- [x] **pycache**/ (ver Capitulo 14)

---

# Capitulo 0 - Visao geral da raiz

## Proposito do sistema

- SIGMA-PLI combina backend FastAPI, frontend Jinja2/JS modular e integracoes com PostgreSQL e Neo4j para gerenciar metadados, repositorio de arquivos e catalogo interativo do PLI.
- Guias extensos documentam backlog completo (upload curado, workflow de aprovacao, integracao GeoServer), mas apenas o modulo M00-home esta ativo na API principal.

## Estado atual

- `app/main.py` publica somente o router M00. Modulos M01-M08 possuem stubs e assets vazios aguardando implementacao.
- Servicos/utilitarios do modulo Home retornam dados mockados; TODOs indicam persistencia real, email e auditoria pendentes.
- Testes automatizados cobrem apenas M00 (`tests/test_home.py`).
- `src/backend` guarda implementacao anterior focada em sincronizar dados PostgreSQL para Neo4j; coexistencia precisa ser resolvida.
- **Infraestrutura local atualizada (2025-11-01):** PostgreSQL 17 operante com banco `sigma_pli`, extensoes `postgis`, `uuid-ossp` e `pg_trgm` habilitadas e conexao administrada via pgAdmin utilizando o servidor nomeado `SIGMA-Local` (usuario `sigma_admin`).

## Riscos e alertas

- Credenciais reais expostas em `app/config.py`, `database.json`, `detalhes_rds_sigma_pli.txt`, scripts Python e documentos Markdown. Urgente migrar para `.env` seguro e rotacionar senhas.
- `detalhes_rds_sigma_pli.txt` revela RDS publico com porta 5432 aberta (0.0.0.0/0). Recomenda-se restringir security group imediatamente.
- `app/main.py` contem codigo duplicado (bloco repetido). Necessario refatorar para evitar confusao.
- `database.py` passa `ssl=settings.postgres_sslmode` (string) para asyncpg; substituir por `ssl=True` ou contexto `ssl.SSLContext`.
- Dois conjuntos de aplicacao (raiz `app/` e legado `src/backend/`). Planejar consolidacao.

## Registro operacional 2025-11-01

- Verificacao: `psql` 17.2 disponivel em `C:\Program Files\PostgreSQL\17\bin`. Caso o binario nao esteja no `PATH`, utilizar `& "C:\Program Files\PostgreSQL\17\bin\psql.exe"`.
- Credencial ativa: usuario `sigma_admin`, senha `Malditas131533*`, host `localhost`, porta `5432`.
- Criacao do banco local:
  - `& "C:\Program Files\PostgreSQL\17\bin\psql.exe" -h localhost -U sigma_admin -d postgres -c "CREATE DATABASE sigma_pli OWNER sigma_admin ENCODING 'UTF8';"`
  - Extensoes: `uuid-ossp`, `pg_trgm`, `postgis` via `CREATE EXTENSION IF NOT EXISTS ...;` (necessario definir `PGPASSWORD` antes dos comandos).
- Instalacao do PostGIS:
  1.  Download `https://download.osgeo.org/postgis/windows/pg17/postgis-bundle-pg17-3.5.3x64.zip`.
  2.  Extracao em `%TEMP%\postgis-pg17\postgis-bundle-pg17-3.5.3x64`.
  3.  Em PowerShell **administrador**, copiar `bin`, `lib`, `share\extension`, `share\contrib` e `gdal-data` para `C:\Program Files\PostgreSQL\17\...` com `Copy-Item -Recurse -Force`. Alguns DLLs em uso podem permanecer da instalacao original.
- Validacao final: `SELECT extname FROM pg_extension ORDER BY extname;` retornando `pg_trgm`, `plpgsql`, `postgis`, `uuid-ossp`.
- pgAdmin: servidor registrado como `SIGMA-Local`, apontando para `localhost`, banco de manutencao `postgres`, usuario `sigma_admin` (senha salva localmente). Utilizar Query Tool para aplicar `ddl_sigma_pli_completo.sql` na proxima fase.
- M01_auth isolado: `ddl_modulo_autenticacao.sql` continua separado, com insercao de exemplo ajustada para `instituicao_id`/`departamento_id` (nulos por padrao). Rodar apos o DDL principal; apos correcao, a pessoa `joao.silva@sigma.gov.br` e a conta `joao.silva` foram inseridas via comandos manuais (com `ON CONFLICT DO NOTHING`).
- Neo4j Aura: instancia `neo4j+ssc://6b7fc90e.databases.neo4j.io` atualizada com as novas credenciais (usuario `neo4j`). Constraints principais recriadas via driver Python e carga inicial realizada com os CSVs `neo4j_dicionario_de_dados`; validacao retorna 1 `Projeto`, 1 `Instituicao`, 1 `Dataset`, 1 `Camada`, 1 `Arquivo`, 1 `Pessoa`, 1 `Tag` e relacionamentos coerentes (TEM_TAG, PUBLICADO_COMO, LICENCIADO_POR etc.).
- Pos-operacao: recomendado limpar `PGPASSWORD` em sessoes interativas com `Remove-Item Env:PGPASSWORD`.

## Destaques de arquivos avulsos

- [x] `app_minimal.py`, `app_simple.py`, `app_test.py` - micro aplicacoes FastAPI para smoke tests e renderizacao direta.
- [x] `database.json` - JSON com credenciais completas do RDS; remover do controle de versao.
- [x] `detalhes_rds_sigma_pli.txt` - Relatorio de RDS AWS com senha e regras de firewall; tratar como sensivel.
- [x] `neo4j_manager.py` - Utilitario para alternar entre Neo4j local e Aura; tambem revela senha.
- [x] Scripts Neo4j (`check_import.py`, `detect_neo4j_desktop.py`, `diagnose_neo4j*.py`, `test_neo4j*.py`, `simple_neo4j_test.py`) - Ferramentas de diagnostico que assumem credenciais padrao.
- [x] DDL e migracoes (`ddl_sigma_pli_completo.sql`, `implementacao_sigma_pli_completa.sql`, `triggers_auditoria_completos.sql`, `migracao_dados_csv_legado.sql`, `ddl_modulo_autenticacao.sql`) - Base relacional completa com auditoria, perfis de arquivo, workflows.
- [x] Documentacao (`GUIA_IMPLEMENTACAO_COMPLETO.md`, `RELATORIO_TECNICO_IMPLEMENTACAO.md`, `sigma_pli_documento_teorico_conceitual_e_especificacao_de_dados_v_1.md`, `Sigma-pli ...docx`, `GUIA_NEO4J_VSCODE.md`, `neo4j_extension_config.md`, `neo4j_vscode_guide.md`) - Referencias funcionais e tecnicas.
- [x] `docker-compose*.yml` - Subida de Neo4j local e stack complementar.
- [x] `requirements.txt` - Dependencias FastAPI, asyncpg, neo4j, jinja2, email-validator.
- [x] `.vscode/`, `profiles/`, `scripts/switch-copilot-toolset.ps1`, `v1.code-workspace*` - Configuracoes VS Code (detalhamento em capitulos proprios).
- [x] `.last_home.html`, `.pytest_cache/`, `__pycache__/`, `.venv/` - Artefatos gerados automaticos (ver Capitulo 14).

---

# Capitulo 1 - Diretorio app/

## Arquitetura

- App FastAPI modular; `app/main.py` monta static, aplica CORS amplo (`*`) e inclui routers via `app/routers`.
- `app/database.py` gerencia pool asyncpg e driver Neo4j com fallback Aura.
- `app/config.py` usa `pydantic-settings`, mas mantem defaults sensiveis em codigo.

## Arquivos principais

- [x] `config.py` - Classe `Settings` com parametros da aplicacao, Postgres, Neo4j local/Aura, JWT, upload, GeoServer, feature flags. Urgente mover segredos para `.env`.
- [x] `database.py` - Funcoes `init_postgres`, `init_neo4j`, `execute_neo4j_query` (lazy). Registrar logs estruturados e tratar SSL adequadamente.
- [x] `main.py` - Duplicacao de definicao de app; precisa consolidar em unico bloco. `startup_event` chama `init_db()` com captura generica.

## Models

- [x] `models/model_dicionario_perfis_extensoes.py` - Schamas Pydantic para perfis e extensoes (Create/Update/Response) com `BaseModelSIGMA` generico.

## Services

- [x] `services/service_home.py` - Metodos assincronos que retornam dados simulados (overview, activity, stats, alerts). `process_contact_submission` valida campos e retorna ID ficticio. TODOs para persistencia, email e notificacoes.

## Utils

- [x] `utils/utils_home.py` - Utilitarios para validacao, formatacao, seguranca, dados, UI, cache e logging. Bem coberto por testes.

## Routers

- [x] `routers/__init__.py` - Registra apenas router M00.
- [x] `routers/M00_home/router_home_status_sistema.py` - Endpoints HTML e API (status, health, contact, stats, modules, neo4j tests). Retornos mockados; TODOs para checks reais.
- [x] `routers/M01_auth/router_auth_login_logout.py` - Stub.
- [x] `routers/M02_dashboard/router_dashboard_kpis_cards.py` - Stub.
- [x] Diretorios `M03_dicionario` a `M08_admin` - Presentes e vazios.

## Pendencias

- Externalizar segredos e usar `.env` carregado via `Settings`.
- Remover duplicacao em `main.py` e introduzir logging estruturado.
- Implementar checks reais em `check_services_health` e fluxos `process_contact_form` (persistencia/alertas).
- Habilitar modulos adicionais apenas quando rotas/servicos estiverem prontos.

---

# Capitulo 2 - Diretorio static/

## Estrutura

- CSS, JS e placeholder de imagens segregados por modulo (M00-M08).

## CSS

- [x] `style_global_reset_base.css`, `style_global_reset_base_1.css` - Resets globais (avaliar consolidacao em um unico arquivo).
- [x] `M00_home/style_home_layout_base.css` - Layout header/hero/footer responsivo.
- [x] `M00_home/style_home_hero_banner.css` - Hero com animacoes e counters.
- [x] `M00_home/style_home_navigation.css` - Menu desktop/mobile.
- [x] `M00_home/style_home_contact_forms.css` - Formularios com icones e validacao visual.
- [x] Diretorios `M01_auth` a `M08_admin` - Vazios aguardando assets.

## JS

- [x] `M00_home/script_home_status_loader.js` - Consome `/api/v1/status`, monta cards e fallback de erro.
- [x] `M00_home/script_home_navigation.js` - Controle de menu e scroll suave.
- [x] `M00_home/script_home_animations.js` - IntersectionObserver para animacoes.
- [x] `M00_home/script_home_form_validation.js` - Validacao basica do formulario antes do POST.
- [x] `M00_home/script_home_state_management.js` - State manager simples com cache e eventos.
- [x] Diretorios `M01_auth` a `M08_admin` - Vazios.

## Imagens

- [x] `static/img/` - Vazio; definir pipeline de assets (compressao/naming) antes de popular.

## Pendencias

- Consolidar reset CSS duplicado e definir tokens de design unificados.
- Documentar padrao de modulos JS (ESM vs script global) para futuros modulos.
- Introduzir testes end-to-end de UI quando funcionalidades alem de M00 estiverem prontas.

---

# Capitulo 3 - Diretorio templates/

## Estrutura

- `templates/pages/Mxx_modulo/` com HTML por modulo; `templates/components/` vazio.

## Conteudo

- [x] `pages/M00_home/template_home_index_pagina.html` - Landing page com hero, grid de modulos, cards de status (renderizados via JS) e formulario de contato.
- [x] Diretorios `pages/M01_auth` a `pages/M08_admin` - Vazios; aguardam templates futuros.
- [x] `components/` - Vazio; reservar para partials reutilizaveis.

## Pendencias

- Criar layout base (Jinja extends) quando multiplas paginas forem introduzidas.
- Externalizar textos repetitivos para evitar hardcode (ex.: emails, telefones) ou usar configuracao.

---

# Capitulo 4 - Diretorio tests/

- [x] `test_home.py` - Suite extensa cobrindo ValidationUtils, FormatUtils, SecurityUtils, DataUtils, UIUtils, HomeService, ContactService, SystemMonitorService e cenarios de integracao. Utiliza pytest e asyncio.
- [x] `run_dry_run.ps1` - Atalho PowerShell para executar `importer/neo4j_importer.py --dry-run`.
- [x] `__pycache__/` - Artefatos de bytecode.

## Observacoes

- Testes dependem de dados mock; nao ha fixtures para Postgres/Neo4j.
- Nenhuma cobertura para routers HTTP (FastAPI). Recomenda-se testar endpoints com `TestClient`.

---

# Capitulo 5 - Diretorio cypher/

- [x] `constraints.cypher` - Cria constraints de unicidade por label (Projeto, Instituicao, Pessoa, etc.).
- [x] `import_nodes.cypher` - `LOAD CSV` para criar nos (Projeto, Instituicao, Pessoa, Licenca, Tag, Dataset, Camada, Pasta, Arquivo).
- [x] `import_rels.cypher` - `LOAD CSV` para relacionamentos (EM_PASTA, REFERE_DATASET, PUBLICADO_COMO, PRODUZIDO_POR, AUTOR, TEM_TAG, LICENCIADO_POR, PRECEDE).
- [x] `teste_extensao_neo4j.cypher` - Consultas de validacao e playbook para extensao.
- [x] `queries_neo4j_extension.cypher` - Colecao de queries para extensao VS Code.

## Pendencias

- Validar caminhos `file:///neo4j_dicionario_de_dados/...` para garantir compatibilidade com ambiente de importacao atual.
- Adicionar scripts para limpeza/reprocessamento incremental conforme volume crescer.

---

# Capitulo 6 - Diretorio docs/

- [x] `README_M00_home.md` - Guia completo do modulo Home (assets, endpoints, validacoes, testes, roadmap).
- [x] `copilot_perfis_ferramentas.md` - Orienta montagem de toolsets Copilot (Core/Dados/DevOps).
- [x] `copilot_toolsets_perfis.jsonc` - Template agregador para toolsets.
- [x] `neo4j_design.md` - Especificacao do modelo de grafo (labels, propriedades, relacoes, sync PostgreSQL->Neo4j) com repeticoes do rascunho automatico.
- [x] `README_NEO4J_IMPORT.md` - Passo a passo para importar dados no Neo4j (citada no inventario).
- [x] `toolsets/` - Arquivos JSONC prontos por perfil (`t1.toolsets.sigma-core.jsonc`, `t1.toolsets.sigma-dados.jsonc`, `t1.toolsets.sigma-devops.jsonc`).

## Observacoes

- Documentos descrevem backlog detalhado e proximo roadmap; convergir com wiki oficial para evitar divergencia.

---

# Capitulo 7 - Diretorio importer/

- [x] `neo4j_importer.py` - Script Python para importar CSVs `neo4j_dicionario_de_dados` em Neo4j (diretorio ou ZIP). Suporta `--dry-run`. Usa driver oficial, `resolve_csv_dir`, e cria nos e relacoes idem aos scripts Cypher.

## Pendencias

- Substituir `session.run` sequencial por transacoes e lotes para performance.
- Parametrizar `neo4j`/`csv_dir` via `.env`.
- Adicionar logs estruturados e tratamento de excecoes com contagem de linhas problematicas.

---

# Capitulo 8 - Diretorio infra/

- [x] `azure/README.md` - Passos para provisionar Resource Group + Neo4j Container Instance via Terraform (Postgres permanece na AWS).
- [x] `azure/main.tf` - Resource group e container Neo4j (CPU=1, memoria=2GB, IP publico) com auth `neo4j/<senha>`.
- [x] `azure/variables.tf` - Valores default (rg, location, neo4j_name, neo4j_password).
- [x] `azure/outputs.tf` - Exibe nome do RG e FQDN do container.
- [x] `azure/create_sp.ps1` - Script para criar service principal e imprimir variaveis.

## Pendencias

- Parametrizar senha via `terraform.tfvars` seguro e evitar commitar default.
- Considerar uso de volumes persistentes e rede interna para producao.

---

# Capitulo 9 - Diretorio .github/

- [x] `copilot-instructions.md` - Guia detalhado de modularizacao, nomenclatura, configuracao de ambientes, checklist de novos modulos e boas praticas.

## Observacoes

- Documento norteia estrutura atual; manter alinhado com README oficial para evitar duplicidade.

---

# Capitulo 10 - Diretorio profiles/

- [x] `README.md` - Orienta importacao de perfis VS Code.
- [x] `SIGMA-Core.code-profile`, `SIGMA-Dados.code-profile`, `SIGMA-DevOps.code-profile`, `SIGMA-Minimal.code-profile` - Perfis pre configurados (conteudo minimo aguardando personalizacao).

## Observacoes

- Atualizar perfis com extensoes recomendadas conforme toolsets.

---

# Capitulo 11 - Diretorio reports/

- [x] `index_usage_report.csv` / `.txt` - Estatisticas de indices (principalmente GIN em esquema dicionario); exibem todos com 0 scans.
- [x] `schema_report.json` / `.txt` - Relatorio de estrutura do banco (mapeamento de tabelas, colunas, chaves).
- [x] `schema_recommendations.sql` - Sugerencias de ajustes (indices, chaves) baseadas no relatorio.
- [x] `rollback_recommendations.sql` - Script para desfazer recomendacoes aplicadas.
- [x] `recommendations_applied.log` - Log de execucoes de recomendacoes.
- [x] `recommendations_top10.txt` - Destaque das principais sugestoes.
- [x] `validation_report.txt` - Validacoes executadas.

## Observacoes

- Relatorios indicam foco em performance e governanca do banco relacional; integrar com pipeline CI para atualizacao periodica.

---

# Capitulo 12 - Diretorio scripts/

- [x] `inspect_zip_csvs.py` - Lista primeiras linhas de cada CSV em ZIP (debug importacao).
- [x] `list_zip_contents.py` - Mostra conteudo de ZIP.
- [x] `read_xlsx_summary.py` - Lista sheets e primeiras linhas de XLSX usando openpyxl.
- [x] `switch-copilot-toolset.ps1` - Copia template de toolset (Core/Dados/DevOps) para pasta de prompts do VS Code Insiders, com backup.

## Pendencias

- Converter scripts diagnosticos para CLI com argparse e logs.

---

# Capitulo 13 - Diretorio src/

## Estrutura geral

- Contem arquitetura anterior/alternativa com backend FastAPI, scripts de analise SQL e assets basicos.

## backend/

- [x] `main.py` - FastAPI que inclui router `app.routers.graph` e expone `/` e `/healthz`.
- [x] `app/database.py` - SQLAlchemy engine via `DATABASE_URL`.
- [x] `app/db/neo4j_sync.py` - Classe `Neo4jSync` que le dados de Postgres via psycopg2 e sincroniza com Neo4j (nos Arquivo, Produtor, relacoes PRODUZIDO_POR, constraints).
- [x] `app/db/neo4j_queries.py` - Consultas (relacionamentos de arquivo, arquivos de produtor, busca semantica, grafo com profundidade).
- [x] `app/routers/graph.py` - Endpoints `/graph/sync`, `/graph/arquivo/...`, `/graph/produtor/...`, `/graph/busca/...`, `/graph/arquivo/.../grafo`.
- [x] Scripts auxiliares (`apply_recommendations.py`, `compare_schema.py`, `generate_recommendations.py`, `generate_schema_report.py`, `index_usage_report.py`, `list_tables.py`, `validate_recommendations.py`, `test_connection.py`, `test_db.sh`) - Automatizam analise do esquema e aplicacao de recomendacoes.
- [x] `config.py`, `.env`, `Dockerfile`, `requirements.txt` - Configuracoes do backend legado.

## frontend/

- [x] `index.html` - Landing estatica simples (links e seções placeholder) com referencias a `css/style.css` e `js/main.js` (nao presentes neste repo).

## apache/

- [x] `conf/httpd.conf` - Configuracao Apache (nao analisada em detalhe; apenas inventariada).

## init-scripts/

- [x] `01-init.sql` - Script inicial (conteudo nao detalhado nesta etapa, apenas inventariado).

## neo4j/

- [x] `init.cypher` - Script de inicializacao (inventariado).

## Observacoes

- Estrutura `src/` difere da atual (`app/`). Necessario decidir qual sera mantida e migrar logica compartilhada.
- Scripts de recomendacao e sincronizacao sao valiosos; considerar integracao no pipeline principal.

---

# Capitulo 14 - Pastas auxiliares

- [x] `.vscode/` - Contem `extensions.json`, `launch.json`, `settings.json`, `tasks.json` ajustados para o projeto (rodar FastAPI, pytest, formatar com black e flake8).
- [x] `.pytest_cache/`, `__pycache__/` - Artefatos de execucao de testes e bytecode; podem ser limpos periodicamente.
- [x] `.last_home.html`, `SUGESTAO_VISUAL/` - Artefatos de prototipacao da home (HTML salvo e sugestoes visuais). Images nao analisadas em detalhe.

---

# Resumo executivo

- Backend principal FastAPI esta funcional apenas para Home; demais modulos sao stubs. Implementar gradativamente rotas/servicos reais.
- Credenciais sensiveis expostas em varios arquivos. Prioridade: mover para `.env`, atualizar configuracao `Settings`, rotacionar senhas (Postgres e Neo4j) e restringir security group do RDS.
- Verificar duplicidade `app/` vs `src/`; definir caminho oficial e desativar legacy para evitar manutencao duplicada.
- Scripts e relatorios de banco (reports/, docs/, src/backend) mostram foco em governanca; alinhar com pipeline automatizado.
- Objetos front-end (static/templates) seguem padrao modular; somente assets de M00 implementados. Planejar entrega incremental dos demais modulos.

# Proximos passos sugeridos

1. Saneamento de segredos e refatoracao de `app/main.py` (remover duplicacao, adicionar logging).
2. Definir estrategia unica para backend (escolher `app/` ou `src/backend/`) e migrar scripts utilitarios conforme necessario.
3. Implementar health-check reais para Postgres e Neo4j, alem de endpoint de contato com persistencia.
4. Criar pipeline de deploy/infra que leia Terraform Azure e stacks Docker, com variaveis de ambiente seguras.
5. Expandir cobertura de testes para endpoints FastAPI e iniciar testes de UI quando novos modulos estiverem ativos.
