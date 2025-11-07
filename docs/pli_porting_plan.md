# Plano de Portabilidade — Módulo M01_auth (PLI → SIGMA)

Objetivo: Migrar o frontend (templates, CSS, JS) do PLI-CADASTRO para o repositório SIGMA-PRINCIPAL sob o módulo `M01_auth`, preservando a estrutura funcional e adaptando a aparência para o design system do SIGMA.

Diretórios-alvo:

- Templates: templates/pages/M01_auth/
- CSS: static/css/M01_auth/
- JS: static/js/M01_auth/

Fases:

1. Inventário completo: listar todos os templates PLI originais e mapear para os targets.
2. Onda 1 (prioritária): Login, Cadastro usuário, Recuperar senha, Dashboard.
3. Onda 2: Páginas auxiliares (pessoa física/jurídica, solicitações, usuários).
4. QA e consolidação: migrar regras do `style_pli_compat.css` para arquivos específicos do módulo e remover inline styles.
5. Integração backend: adaptar endpoints JS para `/api/v1/auth/*` do SIGMA e garantir hooks de email/recuperação.

Checklist por página (template):

- Copiar template original para templates/pages/M01_auth/<nome>.html (ou .ejs em legacy/)
- Substituir includes/partials por includes Jinja2 do SIGMA onde aplicável
- Criar arquivo CSS específico `static/css/M01_auth/style_<pagina>.css` contendo regras novas
- Copiar / adaptar JS para `static/js/M01_auth/script_<pagina>.js` e atualizar chamadas de API
- Executar testes de render (visual) no ambiente local

Observações:

- Preserve arquivos originais na pasta `templates/pages/M01_auth/legacy/` para referência
- Use `style_pli_compat.css` como camada temporária de compatibilidade — planejar consolidação
- Evitar hardcode de URLs no JS: use endpoints relativos (`/api/v1/auth/login`)

# Plano detalhado de portabilidade — PLI-CADASTRO → SIGMA-PRINCIPAL

Data: 2025-11-02

## Resumo curto

Este documento descreve precisamente o que irei (e já comecei a) fazer para portar o front-end do módulo PLI-CADASTRO para o projeto SIGMA-PRINCIPAL. Inclui: cópia dos `base.html` e `base.ejs`, criação de classes de compatibilidade no CSS global do SIGMA, clonagem página-a-página, adaptação de JS e mapeamento dos serviços referenciados (ex.: email/recuperação de senha).

## Principais decisões tomadas até agora

- Criei `static/css/style_pli_compat.css` com definições CSS base para as classes usadas no `base.html`/`base.ejs` do PLI que não existiam no CSS global do SIGMA. Essas classes utilizam as variáveis de cores/typo do `style_global_reset_base.css` do SIGMA.
- Salvei cópias originais dos arquivos PLI em `templates/legacy_pli/base_from_pli.html` e `base_from_pli.ejs` — para referência e para facilitar auditoria/roll-back.
- Adicionei um template adaptado `templates/pages/PLI_base/template_pli_base_pagina.html` que referencia o CSS global do SIGMA e o CSS de compat (para permitir testes visuais) e mantém a estrutura original do PLI.

## O que vou fazer a seguir (passos detalhados)

1. Inventariar todas as páginas do PLI a serem copiadas

   - Ler `views/templates/` no repositório PLI-CADASTRO e listar todos os arquivos HTML/EJS/JS/CSS/ imagens referenciadas.
   - Gerar uma planilha simples (README/MD) com: caminho original, destino proposto no SIGMA, prioridade (1=essencial, 2=UI, 3=assets extras).

2. Página-a-página: clonagem e adaptação
   Para cada página PLI (ex.: `login.html`, `cadastro-usuario.html`, `pessoa-fisica.html`):

   - Copiar o template original para `templates/pages/<Mxx_modulo>/template_<pagina>_<descricao>.html` usando a mesma estrutura DOM.
   - Incluir no head: `/static/css/style_global_reset_base.css` e `/static/css/style_pli_compat.css` (já criado). Quando a página tiver CSS próprio, migrar o conteúdo para `static/css/<Mxx_modulo>/style_<pagina>_<secao>.css` e importar no template.
   - Mapear classes usadas: se a classe existir no CSS global do SIGMA, reaproveitar; caso contrário, adicionar uma definição em `style_pli_compat.css` ou em `static/css/<Mxx_modulo>/style_<pagina>_<secao>.css` se específica.
   - Copiar/ajustar o JS da página para `static/js/<Mxx_modulo>/script_<pagina>_<funcao>.js`. Adaptar chamadas de API para `/api/v1/...` do SIGMA (ex.: `/api/v1/auth/login`), e garantir que o fluxo de autenticação use o formato JWT/cookie adotado no SIGMA.
   - Remover estilos inline quando possível e movê-los para as classes criadas, mantendo a consistência visual do SIGMA (cores, fontes, tamanhos via variáveis CSS).

3. Mapeamento de serviços e dependências

   - Para cada página, coletar referências a serviços (endpoints XHR/fetch, action forms, email templates, images and external assets). Exemplo inicial já detectado: serviço de recuperação de senha por email (token), endpoints de login/registro.
   - Marcar serviços que já existem no SIGMA (ex.: rota de login atual) e aqueles a criar (ex.: endpoints administrativos, import CSV, etc.).

4. Testes e QA visual

   - Para cada página clonada: testar GET -> carregar template, verificar console JS para erros, testar fluxos principais (login válido/ inválido, envio de formulário de cadastro/recuperação).
   - Realizar ajuste fino: remover inline styles, arregimentar classes para usar as variáveis SIGMA.

5. Documentação e handoff
   - Gerar um documento por página com lista de arquivos copiados, classes adicionadas ao `style_pli_compat.css`, e endpoints que a página consome.
   - Incluir testes mínimos (pytest ou TestClient) para endpoints novos/alterados.

## Arquivos criados/alterados nesta etapa

- `static/css/style_pli_compat.css` — definições compat (novas classes mapeadas para variáveis SIGMA).
- `templates/legacy_pli/base_from_pli.html` — cópia fiel do `base.html` original do PLI para referência.
- `templates/legacy_pli/base_from_pli.ejs` — cópia fiel do `base.ejs` original do PLI para referência.
- `templates/pages/PLI_base/template_pli_base_pagina.html` — versão adaptada para o SIGMA que referencia CSS global + compat.

## Mapeamento inicial de assets/JS/serviços referenciados (prioridade)

Esses itens serão conferidos página-a-página; lista inicial (encontrados nos bases):

- `/static/js/auto/base_auto.js` — script automático; copiar para SIGMA se fizer parte do comportamento da UI.
- `/static/images/avatar-default.png` — imagem de avatar (copiar para `static/images/` se necessário).
- Endpoints HTML links: `/cadastro-pessoa-fisica.html`, `/cadastro-pessoa-juridica.html`, `/cadastro-usuario.html`, `/login.html`, `/dashboard.html`, `/pessoa-fisica.html`, `/pessoa-juridica.html`, `/usuarios.html`, `/solicitacoes-cadastro.html`, `/sessions-manager.html` — mapear para rotas ou templates SIGMA.
- Serviços: recuperação de senha por email (token), login/registro APIs — confirmar implementação em `app/routers/M01_auth` e adaptar se necessário.

## Como eu irei documentar (formato e local)

- Para cada página clonada, criarei um `docs/pli_pages/<pagina>_mapping.md` com:
  - Origem (caminho no PLI)
  - Destino (caminho no SIGMA)
  - Arquivos de CSS/JS adicionados
  - Classes novas adicionadas ao `style_pli_compat.css` (ou locais)
  - Endpoints consumidos e status (exists/not-exists)
  - Testes manuais executados

## Checklist de aceite para cada página (definição de feito)

1. HTML copiado e renderizável via Jinja no SIGMA.
2. Todas as classes visuais utilizadas existem em CSS (global ou local). Se foram criadas, estão documentadas.
3. JS da página adaptado para as rotas do SIGMA, sem erros no console.
4. Fluxos essenciais (login/cadastro/recuperação) testados (happy path + invalid inputs).

## Próximo passo imediato (a executar agora, se confirmar):

1. Executar inventário completo dos templates em `D:\SIGMA-PLI-IMPLEMENTACAO\PLI-CADASTRO\views\templates\` e gerar um `docs/pli_pages_index.md` com os arquivos e prioridade. (Posso executar isso agora.)

Se concordar, eu executo o inventário e trago a lista completa com proposta de ordem de portabilidade.

## Observações e notas para o próximo agente

- O CSS de compat (`style_pli_compat.css`) foi criado para diminuir retrabalho inicial — porém a intenção final é migrar estilos para o padrão SIGMA (remover gradientes inline, consolidar variáveis, evitar !important).
- Algumas páginas do PLI usam estilos inline fortemente; idealmente removeremos inline styles durante a fase de QA visual.
- Serviços back-end (email/recovery) precisam ser mapeados explicitamente — eu já localizei endpoints de autenticação no SIGMA; integração do envio de email precisa de credenciais/config que não estão no repositório (usar env vars).

Este arquivo foi gerado automaticamente pelo agente que iniciou a portabilidade. Edite e complemente conforme avançamos.
