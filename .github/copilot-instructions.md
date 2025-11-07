# SIGMA-PLI – Instruções para Agentes de Código (Copilot)

Este repositório implementa o backend (FastAPI) e o frontend (Jinja2 + JS/CSS) com MODULARIZAÇÃO OBRIGATÓRIA em ambos. Use estas regras para ser produtivo rapidamente neste código.

## Padrão Generalista de Modularização e Nomenclatura
- Modularização por domínio: estruture por módulos/funcionalidades, cada módulo contendo suas rotas/handlers, serviços, modelos/esquemas, templates e assets. O arquivo/entrypoint principal apenas compõe (CORS, estáticos, include de módulos, startup) — não define rotas.
- Backend/API:
  - Estrutura: `app/routers/<modulo>/...`, `app/services/<modulo>/...`, `app/models/<modulo>/...`, `app/utils/...` (compartilhados), `app/database.py`, `app/config.py`.
  - Endpoints: prefixe como `/api/<modulo>/...`. Exceções controladas (ex.: Home define `/` e `/health`).
  - Nomes de arquivos: `router_<dominio>_<acao>.py` (ex.: `router_user_auth.py`), `service_<dominio>_<responsabilidade>.py`, `schema_<dominio>_<entidade>.py`.
  - Dependências: módulo não importa internals de outro — compartilhe apenas via `app/services`/`app/utils` públicos.
- Frontend/UI:
  - Templates por módulo: `templates/pages/<Modulo>/template_<pagina>_<descricao>.html`.
  - JS por módulo/página: `static/js/<Modulo>/script_<pagina>_<funcao>.js`.
  - CSS por módulo/seção: `static/css/<Modulo>/style_<pagina>_<secao>.css`.
  - Global: apenas resets/variáveis globais (evite lógica ou estilos de módulo no global).
- Configuração e ambientes:
  - Centralize em `config` (ex.: `pydantic-settings`, `.env`), usando flags de recursos para subir sem serviços externos quando necessário (ex.: `enable_<servico>=false`).
  - Nunca hardcode segredos; aceite override por env vars.
- Testes:
  - Espelhe a estrutura dos módulos em `tests/` (ex.: `tests/test_<modulo>_*.py`).
  - Prefira nomes descritivos de caso (ex.: `test_process_contact_submission_valid`).
- Convenções gerais de nomes:
  - Python: snake_case para arquivos/métodos; PascalCase para classes; nomes expressivos (evite 1 letra).
  - Web assets: mantenha o padrão `script_/style_/template_` com sufixos descritivos (`_<pagina>_<funcao|secao|descricao>`).
- Checklist para novo módulo (geral):
  1) Criar `app/routers/<Modulo>/router_<modulo>_*.py` e expor `/api/v1/<modulo>/...`
  2) Adicionar serviços e (se preciso) modelos/esquemas
  3) Criar `templates/pages/<Modulo>/template_<pagina>_<descricao>.html`
  4) Criar `static/js/<Modulo>/script_<pagina>_<funcao>.js` e `static/css/<Modulo>/style_<pagina>_<secao>.css`
  5) Registrar o router no compose central quando estiver estável

Nota: Abaixo estão os “Padrões aplicados” específicos deste repositório (SIGMA-PLI), que implementam o padrão generalista acima com exemplos reais.

## Padrões Essenciais

### Modularização
- Backend (por módulo/página):
  - Routers em `app/routers/<Mxx_modulo>/router_*.py` (ex.: `app/routers/M00_home/router_home_status_sistema.py`)
  - Services/Utils/Models do módulo em pastas do módulo ou compartilhados em `app/services` e `app/utils`
  - Composição via `app/routers/__init__.py`; habilite o módulo somente quando estável
  - `app/main.py` é MINIMALISTA (CORS, estáticos, include de routers, startup `init_db`) — NUNCA define rotas
- Frontend (por módulo/página):
  - Templates em `templates/pages/<Mxx_modulo>/...`
  - JS em `static/js/<Mxx_modulo>/...`
  - CSS em `static/css/<Mxx_modulo>/...`
  - Global apenas para resets/variáveis: `static/css/style_global_reset_base.css`
- Convenção de endpoints: `/api/v1/<modulo>/...` (exceção do M00: define `/`, `/health` e alias `/api/status`)

### Nomenclatura
- Routers: `router_<dominio>_<acao>.py` (ex.: `router_home_status_sistema.py`)
- Templates: `template_<pagina>_<descricao>.html` (ex.: `template_home_index_pagina.html`)
- JavaScript: `script_<pagina>_<funcao>.js` (ex.: `script_home_status_loader.js`)
- CSS: `style_<pagina>_<secao>.css` (ex.: `style_home_hero_banner.css`)
- Exemplos (M00_home):
  - Template: `templates/pages/M00_home/template_home_index_pagina.html`
  - JS: `static/js/M00_home/script_home_status_loader.js`, `script_home_navigation.js`, `script_home_animations.js`, `script_home_form_validation.js`, `script_home_state_management.js`
  - CSS: `static/css/M00_home/style_home_layout_base.css`, `style_home_hero_banner.css`, `style_home_navigation.css`, `style_home_contact_forms.css`
  - Router: `app/routers/M00_home/router_home_status_sistema.py` expõe `/`, `/health`, `/api/v1/status` e alias `/api/status`

## Arquitetura e Convenções
- Backend (modular por módulo/página):
  - Routers: `app/routers/<Mxx_modulo>/router_*.py`
  - Services/Utils/Models: em pastas do módulo (padrão aplicado no M00) ou compartilhados em `app/services`/`app/utils`
  - Composição: `app/main.py` é minimalista (CORS, estáticos, include de routers, startup `init_db`) e NÃO define rotas
  - Compose de routers: `app/routers/__init__.py` agrega routers dos módulos; habilite módulos somente quando prontos
- Frontend (modular por módulo/página):
  - Templates: `templates/pages/<Mxx_modulo>/template_<pagina>_<descricao>.html`
  - JavaScript: `static/js/<Mxx_modulo>/script_<pagina>_<funcao>.js`
  - CSS: `static/css/<Mxx_modulo>/style_<pagina>_<secao>.css`
  - Global: apenas resets/variáveis (ex.: `static/css/style_global_reset_base.css`)
- Exemplos (M00_home):
  - Template: `templates/pages/M00_home/template_home_index_pagina.html`
  - JS: `static/js/M00_home/script_home_status_loader.js`, `script_home_navigation.js`, `script_home_animations.js`, `script_home_form_validation.js`, `script_home_state_management.js`
  - CSS: `static/css/M00_home/style_home_layout_base.css`, `style_home_hero_banner.css`, `style_home_navigation.css`, `style_home_contact_forms.css`
  - Router: `app/routers/M00_home/router_home_status_sistema.py` expõe `/`, `/health`, `/api/v1/status` e alias `/api/status`
- Home (M00): router define `/`, `/health`, `/api/v1/status` (e alias `/api/status` para o JS da home), `/api/v1/stats`, `/api/v1/modules`, `/api/v1/contact`.
- Banco de dados:
  - Conexões em `app/database.py` (PostgreSQL via `asyncpg`, Neo4j via `neo4j-driver`).
  - Flags em `app/config.py`: `enable_postgres`, `enable_neo4j`. Quando `False`, a app sobe sem travar.
  - Config carrega via `pydantic-settings` (Pydantic v2). Use `.env` para overrides.
- Padrões de nomenclatura front:
  - JS: `script_<pagina>_<funcao>.js` (ex.: `script_home_status_loader.js`).
  - CSS: `style_<pagina>_<secao>.css`.
  - Templates: `template_<pagina>_<descricao>.html`.

## Workflows de Dev
- Ambiente Python (Windows/PowerShell):
  ```pwsh
  & .\.venv\Scripts\Activate.ps1
  python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
  ```
  - Variáveis úteis:
    - ` $env:ENABLE_NEO4J="false"` para desabilitar Neo4j na startup
- Testes (pytest):
  ```pwsh
  python -m pytest tests/test_home.py -v
  ```
  - Status atual: 33 testes passam (M00_home), 1 skip de carga.
- Neo4j:
  - Gerenciador auxiliar: `neo4j_manager.py` (testa local vs Aura, imprime dicas de Docker).
  - Import de dados: ver `README_NEO4J_IMPORT.md` e scripts em `cypher/` e `importer/`.

## Padrões de Implementação
- Mantenha o main enxuto: novas rotas sempre em routers de módulo.
- Inclua routers via `app/routers/__init__.py`. Só habilite módulos quando prontos.
- Para novos módulos (ex.: M01 Autenticação, M03 Dicionário):
  1) Crie `app/routers/M01_auth/router_auth_*.py`
  2) Adicione services/utils dedicados em `app/services`/`app/utils` ou pastas do módulo
  3) Templates em `templates/pages/M01_auth` e assets em `static/{js,css}/M01_auth`
  4) Exporte endpoints como `/api/v1/<modulo>/...`
  5) Registre no compose de routers quando estável
- Front-end consome APIs REST do módulo; a home usa JS para carregar status (`/api/status`).

## Dependências e Versões
- FastAPI 0.117+, Uvicorn 0.36+, Pydantic v2 + `pydantic-settings`, asyncpg, python-jose, passlib, aiofiles.
- Evite pins antigos que quebrem no Python 3.13 (ex.: `psycopg2-binary==2.9.9` foi atualizado para 2.9.10 automaticamente).

## Exemplos Úteis
- Template da home: `templates/pages/M00_home/template_home_index_pagina.html` carrega CSS/JS modulares e consulta `/api/status`.
- Loader de status: `static/js/M00_home/script_home_status_loader.js` — se mudar o endpoint, mantenha o alias `/api/status` no router M00.
- Conexão DB opcional: veja `app/config.py` flags e como `app/database.py` ignora init quando desabilitado.

## O que evitar
- Não definir rotas no `app/main.py`.
- Não quebrar o padrão modular de nomes e diretórios.
- Não acoplar chamadas de DB no template; usar services/routers.

## Dúvidas rápidas
- Porta em uso (Windows 10048): suba em outra, ex. `--port 8010`.
- Neo4j indisponível: use `ENABLE_NEO4J=false` até o Docker/Aura estar funcional.
- Onde começar novos módulos: replique o padrão do M00 e habilite no compose.

## Checklist rápido (novo módulo)
1) Router: `app/routers/Mxx_modulo/router_<modulo>_*.py` com `/api/v1/<modulo>/...`
2) Template: `templates/pages/Mxx_modulo/template_<pagina>_<descricao>.html`
3) JS: `static/js/Mxx_modulo/script_<pagina>_<funcao>.js`
4) CSS: `static/css/Mxx_modulo/style_<pagina>_<secao>.css`
5) Registrar no `app/routers/__init__.py` quando estável
