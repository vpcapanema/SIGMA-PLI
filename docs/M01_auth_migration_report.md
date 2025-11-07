# Relatório da Migração/Integração do Módulo M01_auth (PLI -> SIGMA)

Data: 2025-11-02

Este documento descreve o objetivo, plano, ações executadas e próximos passos para portar e integrar o módulo de cadastros/autenticação (PLI) ao repositório SIGMA-PRINCIPAL.

## Objetivo

- Reimplementar o módulo de cadastros/autenticação (PLI) dentro do projeto `SIGMA-PRINCIPAL`, preservando estritamente a estrutura DOM, IDs e hooks JavaScript das páginas originais. Alterações aceitas: apenas estilos visuais (cores, tipografia, tamanhos) e organização modular conforme padrões SIGMA.
- Expor as páginas do módulo sob `templates/pages/M01_auth/`, assets em `static/css/M01_auth/` e `static/js/M01_auth/` e registrar rotas no backend (FastAPI).

## Critérios de sucesso

- Todas as páginas do módulo carregam via rotas registradas no backend e mantêm IDs/atributos originais.
- Os assets (imagens) referenciados pelas páginas são servidos corretamente sem depender de caminhos externos.
- O servidor inicia e as rotas públicas respondem (ex.: `/auth` → 200). Lint (flake8) sem erros nas modificações Python.

## Plano de Execução (alto nível)

1. Inventariar páginas e identificar IDs/elementos críticos.
2. Converter HTML estático para templates Jinja que estendam `template_base_auth.html` (modularizar head/js via blocos `extra_head`/`extra_js`).
3. Criar/atualizar CSS e JS por página em `static/{css,js}/M01_auth/` aplicando o padrão visual SIGMA (somente estilos, sem tocar markup).
4. Registrar rotas que servem os templates no backend (FastAPI routers) e incluí-las no compose de routers do app.
5. Garantir que assets (imagens) usados pelas páginas sejam servidos — copiar fisicamente para `SIGMA-PRINCIPAL/static/assets/` e/ou montar diretório legado como fallback.
6. Validar: lint, iniciar servidor, checar respostas HTTP e salvar snapshots de páginas.

## Ações realizadas (detalhadas)

- Templates criados/normalizados (exemplos):

  - `templates/pages/M01_auth/template_base_auth.html` (base do módulo, agora inclui server-side `navbar` e `footer`)
  - `templates/pages/M01_auth/template_auth_index_pagina.html` (index do módulo — conteúdo convertido do PLI)
  - `templates/pages/M01_auth/template_auth_login_pagina.html`
  - `templates/pages/M01_auth/template_auth_recuperar_senha_pagina.html`
  - `templates/pages/M01_auth/template_auth_cadastro_pagina.html`
  - `templates/pages/M01_auth/app/usuarios.html`
  - `templates/pages/M01_auth/app/solicitacoes-cadastro.html`
  - `templates/pages/M01_auth/app/pessoa-fisica.html`
  - `templates/pages/M01_auth/app/pessoa-juridica.html`
  - `templates/pages/M01_auth/app/meus-dados.html`

- Componentes adicionados:

  - `templates/pages/M01_auth/components/navbar.html`
  - `templates/pages/M01_auth/components/footer.html`
  - `templates/pages/M01_auth/components/modal-templates.html` (placeholders)

- CSS criados/atualizados em `static/css/M01_auth/` (ex.):

  - `style_pli_compat.css` (compatibilidade PLI → SIGMA, variáveis e mapeamentos)
  - `style_index.css` (ajustes visuais do index)
  - `style_pessoa_fisica.css`, `style_pessoa_juridica.css`, `style_usuarios.css`, `style_solicitacoes_cadastro.css`

- JS (skeletons) adicionados em `static/js/M01_auth/` para preservar hooks e inicializações (DataTables placeholders). Não foi alterada a lógica funcional do front-end além de organizar includes.

- Backend (FastAPI):

  - Novo router que serve as páginas do módulo: `app/routers/M01_auth/router_auth_pages.py` (rotas GET públicas e protegidas, ex.: `/auth`, `/login`, `/pessoa-fisica`, `/usuarios`, `/solicitacoes-cadastro`).
  - Inclusão do router no compose: `app/routers/__init__.py` (adição de `auth_pages_router`).

- Assets:

  - Copiados os arquivos binários (imagens) do repositório legado `PLI-CADASTRO/static/assets/*` para `SIGMA-PRINCIPAL/static/assets/`:
    - step1-pf.png, step2-pj.png, step3-user.png, step4-email.png, step5-approval.png
  - Para compatibilidade inicial também foi adicionado um mount em `app/main.py` apontando temporariamente para o diretório legado; posteriormente a cópia física foi realizada e o mount permanece (não prejudica).

- Tasks e utilitários:

  - Adicionada task VSCode `Executar FastAPI e abrir navegador` em `.vscode/tasks.json` que inicia o uvicorn em background e abre automaticamente `http://127.0.0.1:8010/` no navegador padrão (PowerShell Start-Process).

- Verificações realizadas:
  - Lint (flake8) executado e passou após correções.
  - Servidor iniciado via task e endpoints verificados (GET `/auth` e `/` retornaram 200).
  - Snapshots salvos em `docs/index_snapshot.html` e `docs/home_snapshot.html` com o HTML renderizado.

## O que falta / próximo passos (priorizados)

1. Integrar endpoints reais nos scripts JS/DataTables
   - Substituir URLs TODO em `static/js/M01_auth/*.js` para os endpoints REST reais (ex.: `/api/v1/usuarios`, `/api/v1/solicitacoes`) e testar carregamento/dados.
2. Testes e QA funcional do fluxo de autenticação
   - Testar fluxo login → dashboard com um usuário real/mocado; validar criação de cookie JWT e redirecionamentos.
3. Revisão visual e responsiva
   - Testar páginas em navegadores e dispositivos (ajustar CSS em `style_*` quando necessário).
4. Consolidar assets e remover dependência do diretório legado (opcional)
   - Remover mount de `PLI-CADASTRO/static/assets` de `app/main.py` e garantir que `static/assets` contenha todos os arquivos necessários para deploy independente.
5. Testes automatizados
   - Adicionar testes end-to-end ou tests de integração para rotas críticas (páginas públicas, APIs de listagem).
6. Documentação adicional
   - Instruções de deploy, mapeamento de endpoints e integração com serviços opcionais (Neo4j, Postgres) no README do módulo.

## Riscos e recomendações

- Risco: endpoints JS apontando para URLs erradas podem quebrar carregamento de tabelas; recomendação: definir uma lista única de endpoints (variável global JS ou `data-*` no HTML) e substituir programaticamente.
- Risco: manter mount do diretório legado pode ocultar a necessidade de consolidar assets para produção — recomendado copiar e remover o mount antes do empacotamento/deploy.
- Recomendação: executar um passe de testes manuais e automatizados antes do merge final e documentar endpoints reais que os scripts JS deverão usar.

## Como reproduzir localmente (comandos PowerShell)

1. Ativar ambiente virtual (PowerShell):

   & .\.venv\Scripts\Activate.ps1

2. Instalar dependências (se necessário):

   & .\.venv\Scripts\python.exe -m pip install -r requirements.txt

3. Iniciar app (task recomendada que abre navegador):

   - No VS Code: executar a task `Executar FastAPI e abrir navegador`
   - Ou manual via PowerShell:

     & .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload

4. Abrir a página inicial do módulo M01_auth:

   http://127.0.0.1:8010/auth

5. Snapshots gerados (para referência):

   - `docs/index_snapshot.html` (render do /auth)
   - `docs/home_snapshot.html` (render do /)

## Contato / responsáveis

- Trabalho realizado automaticamente via agente de codificação (par programador). Para decisões finais sobre endpoints e políticas de assets, contatar o mantenedor do repositório.

---

Se desejar, eu: (a) atualizo os scripts JS com os endpoints reais, (b) removo o mount legado e consolido todos os assets em `SIGMA-PRINCIPAL/static/assets/`, ou (c) gero screenshots PNG das páginas para revisão visual — diga qual opção prefere e eu executo o próximo passo.
