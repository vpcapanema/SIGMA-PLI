# SIGMA-PLI - M00: Home Module

## Visão Geral

O módulo Home (M00) é a página inicial e navegação principal do sistema SIGMA-PLI. Ele fornece uma interface de boas-vindas, status do sistema, formulário de contato e links para os demais módulos.

## Estrutura de Arquivos

```
M00_home/
├── router_home_status_sistema.py      # Router FastAPI com endpoints
├── service_home.py                    # Serviços de negócio
├── utils_home.py                      # Utilitários e helpers
├── template_home_index_pagina.html    # Template HTML principal
├── script_home_*.js                   # Scripts JavaScript modulares
├── style_home_*.css                   # Estilos CSS modulares
└── test_home.py                       # Testes unitários
```

## Funcionalidades

### 1. Página Inicial
- **Hero Section**: Apresentação do sistema com estatísticas
- **Módulos**: Cards dos módulos disponíveis
- **Status**: Indicadores de saúde do sistema
- **Contato**: Formulário para contato

### 2. API Endpoints

#### GET `/`
Página inicial renderizada

#### GET `/api/v1/status`
```json
{
  "status": "operational",
  "version": "1.0.0",
  "uptime": 3600.5,
  "modules": {
    "M00_home": "✅ operational",
    "M01_auth": "🚧 under_development"
  },
  "databases": {
    "postgresql": "✅ connected",
    "neo4j": "✅ connected"
  },
  "last_updated": "2025-01-15T10:30:00Z"
}
```

#### GET `/api/v1/health`
Health check detalhado do sistema

#### POST `/api/v1/contact`
Processa formulário de contato
```json
{
  "name": "João Silva",
  "email": "joao@example.com",
  "message": "Mensagem de contato"
}
```

#### GET `/api/v1/stats`
Estatísticas gerais do sistema

#### GET `/api/v1/modules`
Lista de todos os módulos disponíveis

## Scripts JavaScript

### script_home_status_loader.js
- Carrega status do sistema via AJAX
- Atualiza indicadores em tempo real
- Trata erros de conectividade

### script_home_navigation.js
- Gerencia navegação mobile
- Efeitos de scroll
- Smooth scrolling para âncoras

### script_home_animations.js
- Animações de entrada (fade-in, slide-in)
- Efeitos hover
- Animação do hero banner

### script_home_form_validation.js
- Validação de formulários
- Máscaras de entrada (CPF, telefone, data)
- Feedback visual de validação

### script_home_state_management.js
- Gerenciamento de estado da aplicação
- Cache de dados
- Comunicação com APIs

## Estilos CSS

### style_home_layout_base.css
- Layout responsivo
- Grid system
- Componentes base (botões, cards)

### style_home_hero_banner.css
- Hero section com background
- Estatísticas animadas
- Call-to-action buttons

### style_home_navigation.css
- Header e navegação
- Menu mobile
- Efeitos de scroll

### style_home_contact_forms.css
- Formulários de contato
- Estados de validação
- Cards de informação

## Validações

### Formulário de Contato
- **Nome**: 2-50 caracteres, apenas letras
- **Email**: Formato válido
- **Mensagem**: 10-1000 caracteres

### Sanitização
- Remoção de tags HTML
- Limitação de comprimento
- Filtragem de caracteres especiais

## Testes

### Cobertura de Testes
- Utilitários de validação
- Formatação de dados
- Segurança
- Serviços de negócio
- Endpoints da API

### Como Executar
```bash
# Todos os testes
pytest tests/test_home.py -v

# Testes específicos
pytest tests/test_home.py::TestValidationUtils -v

# Com cobertura
pytest tests/test_home.py --cov=app.services.service_home --cov-report=html
```

## Performance

### Otimizações Implementadas
- Cache de dados com TTL
- Debounce para validações
- Lazy loading de componentes
- Compressão de assets

### Métricas Monitoradas
- Tempo de resposta da API
- Taxa de erro de formulários
- Performance do JavaScript
- Uso de memória

## Segurança

### Medidas Implementadas
- Sanitização de inputs
- Validação de dados
- Tokens CSRF
- Rate limiting (a implementar)

### Validações de Segurança
- Prevenção de XSS
- Validação de email
- Sanitização de filenames
- Controle de comprimento

## Acessibilidade

### Recursos Implementados
- Navegação por teclado
- Screen reader support
- Contraste adequado
- Focus management

### Conformidade
- WCAG 2.1 AA
- Suporte a leitores de tela
- Navegação sem mouse

## Responsividade

### Breakpoints
- Mobile: < 768px
- Tablet: 768px - 1024px
- Desktop: > 1024px

### Estratégias
- Mobile-first design
- Flexbox e Grid
- Imagens responsivas
- Tipografia escalável

## Próximos Passos

### Funcionalidades Planejadas
- [ ] Sistema de notificações
- [ ] Dashboard em tempo real
- [ ] Cache avançado
- [ ] PWA capabilities
- [ ] Multi-idioma

### Melhorias Técnicas
- [ ] GraphQL API
- [ ] WebSockets para updates
- [ ] Service Worker
- [ ] CDN para assets
- [ ] Monitoring avançado

## Dependências

### Python
- fastapi
- pydantic
- aiofiles
- python-multipart

### JavaScript
- Navegador moderno (ES6+)
- Fetch API
- No frameworks externos

### CSS
- CSS Grid e Flexbox
- CSS Custom Properties
- Modern CSS features

## Troubleshooting

### Problemas Comuns

**Formulário não envia**
- Verificar validações JavaScript
- Checar conectividade de rede
- Validar dados de entrada

**Status não carrega**
- Verificar endpoint `/api/v1/status`
- Checar logs do servidor
- Validar CORS

**Animações não funcionam**
- Suporte a CSS transforms
- JavaScript habilitado
- Preferências de redução de movimento

### Debug
```javascript
// Debug state management
console.log(stateManager.getState());

// Debug API calls
window.debugAPICalls = true;
```

## Contribuição

### Padrões de Código
- Padrão de nomenclatura: [tipo]_[modulo]_[funcao]
- Testes obrigatórios para novas funcionalidades
- Documentação em docstrings
- Type hints em Python

### Pull Request Process
1. Criar branch feature/[modulo]/[funcionalidade]
2. Implementar com testes
3. Executar linting e testes
4. Criar PR com descrição detalhada
5. Code review e merge

---

**Módulo Desenvolvido por**: Equipe SIGMA-PLI
**Última Atualização**: Janeiro 2025
**Versão**: 1.0.0