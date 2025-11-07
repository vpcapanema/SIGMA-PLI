# SIGMA–PLI — Documento Teórico‑Conceitual e Especificação de Dados (v1.2)

> **Changelog v1.2**
> - **GeoServer 2.27.2 (Linux)** definido como padrão.
> - **Java 17 LTS** (Temurin/OpenJDK) obrigatório para o GeoServer.
> - **PostgreSQL 17 + PostGIS 3.5.x** (compatível e atual).
> - **Sem Tomcat no MVP**: GeoServer roda com **Jetty embutido** atrás do **Apache 2.4** (reverse proxy). Tomcat 9 fica **opcional** se, no futuro, optarmos por WAR.
> - **Apache 2.4** documentado com módulos `proxy`, `proxy_http`, `headers` e rota `/geoserver/*`.
> - **Segurança**: PostgreSQL acessível **somente por IPs permitidos** (NSG + `pg_hba.conf`); GeoServer **público** via Apache/NSG.
> - Mantidos: FastAPI no backend, HTML/JS/CSS no front, OCI Free Tier com automação via OCI‑CLI/PowerShell.

---

## 0) Glossário rápido
**Perfil:** categoria semântica de arquivo (ex.: `tabular`, `geoespacial_vetor`).  
**Extensão:** formato aceito por um perfil (ex.: `.csv`, `.shp`).  
**Dicionário:** metadados obrigatórios do arquivo (técnicos e de conteúdo).  
**Repositório interativo:** catálogo público/privado + fluxo de upload curado.  
**Aplicações acopláveis:** módulos externos que compartilham navegação, autenticação e autorização na mesma UI.

---

## 1) Objetivo do sistema
O **SIGMA–PLI** combina **governança de dados** (nada é publicado sem metadados) com **usabilidade** (autopreenchimento, catálogo facetado, histórico/versões). Metadados em **PostgreSQL**, relações semânticas em **Neo4j**, camadas geográficas via **GeoServer**. Infraestrutura cabe no **OCI Free Tier** e permite acoplar novas aplicações mantendo experiência única.

---

## 2) Módulos funcionais (navegável por páginas)
- **M00 — Boas‑vindas (Home)**: landing, avisos, atalhos.
- **M01 — Autenticação/Acesso**: login, recuperação, política de senhas.
- **M02 — Dashboard (Minha Área – Home)**: visão pessoal com 4 cards (Agenda, Home Office, Minhas Tarefas, Logs) + KPIs do Dicionário/Repositório.
- **M03 — Dicionário & Repositório Interativo (núcleo)**: catálogo com facetas; upload curado; administração de perfis/extensões e auditoria.
- **M04 — Minha Área**: tarefas, notificações, meus uploads, aprovações, favoritos/coleções.
- **M05 — Calendário Interativo**: agenda pessoal/equipe/produtos; integração com os cards Agenda/Home Office.
- **M06 — Institucional (sobre o PLI)**: entregas oficiais, produtos, documentos normativos.
- **M07 — Ferramentas Avançadas**: GeoServer (view/console), ETL/Jobs, APIs Explorer, **Aplicações acopláveis**.
- **M08 — Administração**: usuários, papéis/permissões, config, saúde do sistema, logs/auditoria, backup/restore, integrações.

> **Nota:** SIGATA foi descontinuado e removido.

---

## 3) Arquitetura técnica (visão 1000 m)
### 3.1 Front‑end
- **HTML/JS/CSS** como base (progressive enhancement; SPA opcional onde fizer sentido).
- Lista de extensões (upload) **controlada no front** conforme o perfil.
- Componentes reutilizáveis (cards do dashboard, calendário, tabela de logs etc.).

### 3.2 Back‑end
- **FastAPI** (Python) expõe API para metadados, upload, catálogo, auditoria, fila de publicação (GeoServer) e sincronização Neo4j.
- Webhooks/jobs para ETL leve e indexação.
- (Opcional) GraphQL Gateway para queries ricas.
- **Servidores Java**: **não** usaremos **Tomcat** no MVP; o **GeoServer 2.27.2** rodará via **binário com Jetty embutido**, **atrás do Apache** (reverse proxy). Se necessário no futuro, suportamos deploy **WAR** em **Tomcat 9**.

### 3.3 Persistência
- **PostgreSQL 17 + PostGIS 3.5.x** (mesmo que rasters/vetores fiquem como arquivos externos):
  - Esquema `dicionario` (núcleo de metadados de arquivo).
  - Esquema `usuarios` **[provisório]** (identidade/autorização; tarefas/agenda/home office).
  - Esquema `cadastro` **[provisório]** (instituições, pessoas, produtos, entregas).

### 3.4 Publicação geográfica
**GeoServer 2.27.2** dedicado (M07), com workspaces/stores por projeto; camadas apontam para arquivos no Object Storage (GeoPackage, GeoTIFF, etc.) ou para tabelas PostGIS quando pertinente.

### 3.5 Observabilidade e segurança (visão)
- **Logging**: Apache (access/error), logs de app (JSON), e eventos de auditoria.
- **Métricas**: OCI Monitoring (CPU, memória, disco) + endpoints `/healthz` e (opcional) `/metrics`.
- **TLS**: Apache (Let’s Encrypt).
- **Segurança de rede**: NSGs/VCN; privilégios mínimos.

---

## 4) Fluxos operacionais críticos
### 4.1 Upload curado (M03)
1. Selecionar **perfil** e **extensão** (lista no front).  
2. Enviar arquivo e autopreencher metadados (MIME, hash, idioma, SRID, bandas, cabeçalho CSV etc.).  
3. Complemento obrigatório por perfil (mínimos para publicar).  
4. Persistir em PostgreSQL: `arquivo` → `produtor` → `estrutura__perfil` → `conteudo__perfil`.  
5. Indexar/atualizar **Neo4j** e registrar **auditoria**.  
6. Se geoespacial, publicar no **GeoServer** (fila/ETL leve).

### 4.2 Catálogo & detalhe
View base (arquivo+produtor); colunas de estrutura/conteúdo carregadas on‑demand conforme o perfil.

### 4.3 Aprovações/versões (M04)
Histórico de versões por arquivo; workflow simples (solicitação/decisão) e notificações.

---

## 5) Modelo de dados (PostgreSQL)
### 5.0 Padrões gerais
PK UUID; cadeia canônica: `conteudo__*.estrutura_id → estrutura__*.id → produtor.id → arquivo.id`.  
Índices: BTREE em FKs/datas; GIN para arrays/JSONB quando útil.

### 5.1 Esquema `dicionario` (núcleo)
**Fixas**: `arquivo`, `produtor`, `perfil`, `extensao` (mesmas definições da v1.1).  
**Por perfil**: `estrutura__*` e `conteudo__*` para cada perfil (`documentos_texto`, `midia`, `tabular`, `geoespacial_vetor`, `geoespacial_raster`, `nuvem_pontos`, `desenho_2d3d`, `database`, `geodatabase`, `pacote`).

### 5.2 Esquema `usuarios` [provisório]
- `usuario`, `papel`, `usuario_papel`, `permissao`, `papel_permissao`, `auditoria_login`.  
- **`tarefa`**, **`evento`**, **`homeoffice`** para Minha Área.

### 5.3 Esquema `cadastro` [provisório]
- `instituicao`, `departamento`, `pessoa`, `produto`, `entrega`, `documento_normativo`.

---

## 6) Grafo (Neo4j Aura)
Nós: Arquivo, Produtor, Perfil, Extensao, Estrutura, Conteudo, Instituicao, Pessoa, Camada, Tabela, Tema.  
Arestas principais: `(Arquivo)-[:PRODUZIDO_POR]->(Produtor)`, `(Arquivo)-[:TEM_PERFIL]->(Perfil)`, `(Perfil)-[:ACEITA_EXTENSAO]->(Extensao)`, `(Arquivo)-[:DESCRITO_POR]->(Estrutura)-[:DESCREVE]->(Conteudo)`, `(Produtor)-[:PERTENCE_A]->(Instituicao)`, `(Produtor)-[:CONTATO]->(Pessoa)`, `(Conteudo)-[:RELATA_A]->(Tema)`, `(Camada)-[:PUBLICA]->(Arquivo)`, `(Tabela)-[:REPRESENTA]->(Camada)`.

---

## 7) Segurança, conformidade e auditoria
- **RBAC** por papéis + permissões por recurso/ação.
- **Auditoria**: uploads, edições, aprovações, publicações (tabela de eventos + triggers).
- **Privacidade**: dados pessoais com acesso restrito.
- **Rede/NSGs**: DB em subnet privada.
- **PostgreSQL (produção)**: acessível **somente por IPs específicos**. Implementação dupla:
  1) **NSG** limitando **5432/TCP** aos **CIDRs/IPs autorizados**; e
  2) **`pg_hba.conf`** com entradas `hostssl` por IP/CIDR (SCRAM) + `listen_addresses` restrito.
- **GeoServer**: **acesso externo público** via **Apache** (reverse proxy em `/geoserver/`), mantendo a porta interna (8080) não exposta. NSG libera **80/443`**.

---

## 8) Infraestrutura (OCI Free Tier)
- **VM‑APP (pública)**: Apache + FastAPI (SIGMA‑PLI e Cadastro) + front HTML/JS/CSS.  
  Shape: A1.Flex 1 OCPU/6 GB.  
- **VM‑GEO (pública)**: **GeoServer 2.27.2** (JDK 17) + Apache (proxy `/geoserver`).  
  Shape: A1.Flex 2 OCPUs/12 GB (ou 1/6 GB se necessário).  
- **VM‑DB (privada)**: **PostgreSQL 17 + PostGIS 3.5.x**.  
  Shape: A1.Flex 1 OCPU/6 GB.  
- **Object Storage (OCI)**: bucket versionado para arquivos (`files`) e backups.  
- **Neo4j Aura (Free)**: externo gerenciado.  
- **TLS** via Apache; **Monitoring/Logging** habilitados.  
- **Automação**: scripts PowerShell com **OCI CLI** (ex.: `copilot-bootstrap.ps1`).

---

## 9) Plano de ação (MVP → Operação)
1. Validar **v1.2** com a equipe.  
2. Gerar **DDL** (`CREATE SCHEMA/TABLE/INDEX/VIEW`) + triggers de auditoria (ajustar com CSV do legado).  
3. Implantar na **OCI Free Tier** (rede/NSGs, VMs, buckets).  
4. Fluxo de Upload (M03): perfis/extensões, leitura automática, manifesto “pacote”.  
5. Integração GeoServer/Neo4j: publicar camadas e popular grafo.  
6. Migração RDS: importar `usuarios/cadastro` conforme CSV real.  
7. Teste de carga/aceite: datasets por perfil, catálogo, auditoria e KPIs.

---

## 10) Views (catálogo público)
- View base fixa: `arquivo ⨝ produtor` (lista/facetas).  
- Join sob demanda: front chama a view/tabela específica (`estrutura__perfil`, `conteudo__perfil`) ao filtrar por perfil. Evita view monolítica.

---

## 11) Dashboard — Minha Área (Home)
**Layout:** grid **2×2**, cartões **retangulares (paisagem)**, **tamanhos idênticos**; **largura fixa**, **altura variável** com **altura máxima**.

**Boas‑vindas (acima dos cards):** “**Bem‑vindo, _{primeiro_nome}_**. Hoje é dia **{dd} de {mês} de {aaaa}**.” (pt‑BR).

### CARD 1 — Agenda (ex.: “Agenda — Marina”)
- **Calendário mensal** (uma **única coluna** de grade mensal; células podem ser maiores para exibir o compromisso).  
- **Lista de compromissos/eventos** organizada em **colunas** sob o calendário quando houver espaço.
- **Clique** em evento → abre **Calendário Interativo (M05)** no dia correspondente.

### CARD 2 — Aviso de Home Office (mês inteiro)
- **Calendário mensal completo**.  
- **Cores por usuário**; **opacidade** para qualificar: dias passados (mais translúcidos), **dia atual** (menos transparente), **confirmado semana que vem** (realce).  
- **Ação**: “**Definir/confirmar meus dias de home office da próxima semana**” → página de confirmação (M05).

### CARD 3 — Minhas Tarefas
- Limitar a **5 tarefas** visíveis (ordenar por prioridade/data); concluir/reabrir; ver todas em Minha Área.

### CARD 4 — Logs do Servidor (tempo real)
- Tabela compacta: **Subsistema**, **Último status (ação)**, **Data e hora**, **Status**.  
- Subsistemas: Dicionário de Dados, Repositório Interativo, Neo4j, Banco de Dados.  
- Data/hora pt‑BR; cores por natureza (erro/aviso/sucesso).  
- Atualização **streaming** (SSE/WebSocket) sem ultrapassar limites do card.

---

## Anexo A — Lista consolidada de tabelas por esquema
**dicionario**: `arquivo`, `produtor`, `perfil`, `extensao`; pares `estrutura__/conteudo__` por perfil.  
**usuarios [provisório]**: `usuario`, `papel`, `usuario_papel`, `permissao`, `papel_permissao`, `auditoria_login`, `tarefa`, `evento`, `homeoffice`.  
**cadastro [provisório]**: `instituicao`, `departamento`, `pessoa`, `produto`, `entrega`, `documento_normativo`.

---

## Anexo B — Tipos de campo (guia)
Identificadores: **UUID**.  
Texto: **TEXT** (usar CHECK/enum quando convier).  
Números: **INTEGER**, **BIGINT**, **FLOAT**.  
Temporais: **TIMESTAMP**, **DATE**.  
Listas: **TEXT[]**.  
Estruturados: **JSONB**.

---

## Anexo C — Automação (OCI CLI / PowerShell)
- **Orquestração**: `copilot-bootstrap.ps1` cria/reusa rede (VCN/NSGs), buckets, grava cloud‑init e lança VMs (APP/GEO/DB).  
- Cloud‑init **GeoServer 2.27.2 + OpenJDK 17** (binário com Jetty), **Apache 2.4** com módulos `proxy`, `proxy_http`, `headers` e virtual host `/geoserver/`.  
- Smoke test: `Invoke-WebRequest -Method Head` em `http://APP_IP/` e `http://GEO_IP/geoserver/web/`.  
- Backups do PostgreSQL para bucket `backups` (job dedicado posterior).

---

## Anexo D — Apache 2.4 (Reverse Proxy para GeoServer)
**Habilitar módulos**
```
a2enmod proxy proxy_http headers && systemctl reload apache2
```

**VirtualHost base**
```apache
<VirtualHost *:80>
  ServerName SEU_DOMINIO
  Header always set X-Content-Type-Options "nosniff"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"

  ProxyPreserveHost On
  ProxyPass        /geoserver/ http://127.0.0.1:8080/geoserver/
  ProxyPassReverse /geoserver/ http://127.0.0.1:8080/geoserver/

  ErrorLog  ${APACHE_LOG_DIR}/geo-error.log
  CustomLog ${APACHE_LOG_DIR}/geo-access.log combined
</VirtualHost>
```

