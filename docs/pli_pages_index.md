# Índice inicial de páginas PLI a portar

Este arquivo lista as principais páginas do PLI-CADASTRO que serão portadas para o módulo `M01_auth` em ondas.

Onda 1 (prioridade alta)

- Login — templates/pages/M01_auth/template_auth_login_pagina.html
- Cadastro usuário — templates/pages/M01_auth/template_auth_cadastro_pagina.html
- Recuperar senha — templates/pages/M01_auth/template_auth_recuperar_senha_pagina.html
- Dashboard — templates/pages/M01_auth/template_auth_dashboard_pagina.html (a criar)

Onda 2 (prioridade média)

- Cadastro Pessoa Física — templates/pages/M01_auth/template_pessoa_fisica_pagina.html
- Cadastro Pessoa Jurídica — templates/pages/M01_auth/template_pessoa_juridica_pagina.html
- Usuarios (lista/gestão) — templates/pages/M01_auth/template_usuarios_list_pagina.html
- Solicitações de cadastro — templates/pages/M01_auth/template_solicitacoes_pagina.html

Notas:

- O arquivo `templates/pages/M01_auth/legacy/` conterá cópias originais dos templates PLI (.ejs/.html)
- Cada página terá seu CSS (static/css/M01*auth/style*<pagina>.css) e JS (static/js/M01*auth/script*<pagina>.js)

# Inventário inicial de páginas referenciadas pelo `base` do PLI-CADASTRO

Este arquivo lista as rotas/arquivos referenciados nos templates base do PLI (links no menu/rodapé) e propõe um destino/ação no SIGMA-PRINCIPAL.

Formato: Origem (link no base) -> Proposta destino no SIGMA (template / css / js )

Lista inicial (extraída de `base.html` / `base.ejs`):

- /index.html

  - Proposta: `templates/pages/M00_home/template_home_index_pagina.html` (já existe no SIGMA)

- /cadastro-pessoa-fisica.html

  - Proposta destino: `templates/pages/M03_cadastros/template_cadastro_pessoa_fisica_pagina.html`
  - CSS: `static/css/M03_cadastros/style_pessoa_fisica.css`
  - JS: `static/js/M03_cadastros/script_pessoa_fisica_form.js`

- /cadastro-pessoa-juridica.html

  - Proposta destino: `templates/pages/M03_cadastros/template_cadastro_pessoa_juridica_pagina.html`
  - CSS: `static/css/M03_cadastros/style_pessoa_juridica.css`
  - JS: `static/js/M03_cadastros/script_pessoa_juridica_form.js`

- /cadastro-usuario.html

  - Proposta destino: `templates/pages/M01_auth/template_auth_cadastro_pagina.html` (já existe, ajustar se necessário)
  - CSS: `static/css/M01_auth/style_auth_cadastro.css` (já existe)
  - JS: `static/js/M01_auth/script_auth_cadastro.js` (já existe)

- /login.html

  - Proposta destino: `templates/pages/M01_auth/template_auth_login_pagina.html` (já existe)
  - CSS: `static/css/M01_auth/style_auth_login_layout.css` (já existe)
  - JS: `static/js/M01_auth/script_auth_login.js` (verificar/adaptar)

- /dashboard.html

  - Proposta destino: `templates/pages/M02_dashboard/template_dashboard_index_pagina.html` (já existe)

- /pessoa-fisica.html

  - Proposta destino: `templates/pages/M03_cadastros/template_pessoa_fisica_view.html`

- /pessoa-juridica.html

  - Proposta destino: `templates/pages/M03_cadastros/template_pessoa_juridica_view.html`

- /usuarios.html

  - Proposta destino: `templates/pages/M04_gerencial/template_usuarios_list_pagina.html`

- /solicitacoes-cadastro.html

  - Proposta destino: `templates/pages/M04_gerencial/template_solicitacoes_pagina.html`

- /sessions-manager.html

  - Proposta destino: `templates/pages/M04_gerencial/template_sessions_manager_pagina.html`

- /meus-dados.html

  - Proposta destino: `templates/pages/M01_auth/template_meus_dados_pagina.html`

- /configuracoes.html

  - Proposta destino: `templates/pages/M01_auth/template_configuracoes_pagina.html`

- /sobre.html, /ajuda.html, /contato.html, /privacidade.html
  - Proposta destino: `templates/pages/M00_home/...` (páginas informativas, criar se necessário)

Observações iniciais:

- Muitos dos destinos propostos já existem parcialmente no SIGMA (M00_home, M01_auth, M02_dashboard). Os módulos gerenciais e de cadastros (M03/M04) precisarão ser criados se ainda não existirem.
- Próximo passo: inspecionar o diretório `D:\SIGMA-PLI-IMPLEMENTACAO\PLI-CADASTRO\views\templates\` para listar páginas reais (se houver mais além do base), e então iniciar a clonagem por prioridade (recomendo: login/cadastro/usuarios/dashboard como primeira onda).

Atualização: já criei um clone skeleton da página de Recuperar Senha no SIGMA (estrutura preservada). Arquivos adicionados:

- `templates/pages/M01_auth/public/recuperar-senha.html` — template com DOM/IDs preservados
- `static/css/M01_auth/style_recuperar_senha.css` — CSS mínimo/skeleton
- `static/js/M01_auth/script_recuperar_senha.js` — JS skeleton que mantém os hooks:
  - `emailForm`, `tokenForm`, `passwordForm` (forms)
  - `email`, `token`, `newPassword`, `confirmPassword` (inputs)
  - `resendLink`, `resendTimer` (reenviar código)

Observação: os handlers são placeholders (logs) — integração com endpoints `/api/v1/...` ficará para a fase de ligação backend.

Posso prosseguir com o próximo arquivo da Onda 1 (Dashboard) mantendo o mesmo nível de fidelidade estrutural. Se sim, iniciarei a criação dos arquivos:

- `templates/pages/M01_auth/app/dashboard.html`
- `static/css/M01_auth/style_dashboard.css`
- `static/js/M01_auth/script_dashboard.js`

Atualização: os arquivos da Dashboard foram adicionados em modo skeleton. Hooks importantes preservados:

- IDs: `welcomeUser`, `welcomeDate`, `totalPessoasFisicas`, `totalPessoasJuridicas`, `totalUsuarios`, `todosOsCadastros`, `totalSolicitacoes`, `ultimosCadastros`
- Modais e formulários: `changePasswordForm` (modal Alterar Senha)

Observação: os scripts atuais são placeholders que setam textos e logs; integração com fontes de dados e charts será feita na fase de ligação com a API.

Atualização: adicionei a página 'Meus Dados' em modo skeleton. Arquivos criados:

- `templates/pages/M01_auth/app/meus-dados.html` — template com estrutura e IDs preservados
- `static/css/M01_auth/style_meus_dados.css` — CSS mínimo/skeleton
- `static/js/M01_auth/script_meus_dados.js` — JS skeleton que preserva os hooks:
  - `userDataForm`, `passwordForm`, `editButtons`, `auto_evt_6bcf612e` (modo editar)

Observação: handlers são placeholders; integração com `services/api.js` e endpoints ficará para a fase de integração.

Status: também criei os templates canônicos SIGMA (nomes conforme padronização do repositório) que apontam para as versões já clonadas:

- `templates/pages/M01_auth/template_auth_recuperar_senha_pagina.html`
- `templates/pages/M01_auth/template_auth_dashboard_pagina.html`
- `templates/pages/M01_auth/template_meus_dados_pagina.html`

Adicionei também o clone de `cadastro-usuario` (público) e o template canônico correspondente:

- `templates/pages/M01_auth/public/cadastro-usuario.html` — clone estrutural do PLI
- `static/css/M01_auth/style_cadastro_usuario.css` — CSS skeleton
- `static/js/M01_auth/script_cadastro_usuario.js` — JS skeleton (hooks: `usuarioPublicForm`, `toggleSenha`, `toggleConfirmarSenha`)
- `templates/pages/M01_auth/template_auth_cadastro_pagina.html` — template canônico
- `static/css/M01_auth/style_auth_cadastro.css` — wrapper CSS que importa o skeleton

E os CSS-wrappers canônicos em `static/css/M01_auth/` para manter compatibilidade de nomes e permitir substituições futuras sem quebrar referências.

## Modificações realizadas em 2025-11-02

Nesta sessão foram concluídas as seguintes entregas, respeitando a restrição de não alterar IDs/atributos/data-\* do HTML original:

- Normalização de templates: remoção de wrappers DOCTYPE/HTML/HEAD/BODY em templates que foram convertidos para estender `pages/M01_auth/template_base_auth.html`.
- Padronização visual (CSS): introdução de variáveis e regras SIGMA mínimas em arquivos CSS do módulo (`style_pessoa_fisica.css`, `style_pessoa_juridica.css`, `style_usuarios.css`, `style_solicitacoes_cadastro.css`), mantendo compatibilidade com o markup legado.
- Páginas recriadas/atualizadas (conteúdo completo ou skeleton pronto para uso):
  - `templates/pages/M01_auth/app/usuarios.html` — tabela `usuariosTable`, modal `usuarioModal`, form `usuarioForm`, filtros `filtroNome`, `filtroEmail`.
  - `templates/pages/M01_auth/app/solicitacoes-cadastro.html` — tabela `solicitacoesTable`, modal `solicitacaoModal`, form `solicitacaoForm`, filtros `filtroProtocolo`, `filtroNomeSolicitante`.
  - Confirmação/normalização de: `pessoa-fisica.html`, `pessoa-juridica.html`, `meus-dados.html`, `template_auth_login_pagina.html`, `template_auth_recuperar_senha_pagina.html`, `template_auth_dashboard_pagina.html`, `template_auth_cadastro_pagina.html`.
- QA: executei lint (`flake8`) no workspace — sem problemas detectados.

Próximos passos sugeridos (posso executar se confirmar):

- Substituir URLs TODO nos scripts JS pelos endpoints reais do SIGMA (ex.: `/api/v1/usuarios`, `/api/v1/solicitacoes`) e testar integração do DataTable.
- Rodar o servidor local e validar visualmente as páginas (posso subir o uvicorn se desejar).
- Gerar testes funcionais mínimos para os endpoints de listagem (opcional, sob demanda).

Se quiser que eu prossiga com algum dos itens acima agora, diga qual (ex.: integrar DataTables, subir app local, ajustar JS endpoints).
