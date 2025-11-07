# 🏗️ ARQUITETURA COMPLETA - APIs de Auto-Preenchimento

## 🎯 Visão Geral do Sistema

```
┌─────────────────────────────────────────────────────────────────────┐
│                         🌐 NAVEGADOR DO USUÁRIO                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  Página 1: Cadastro Instituição          Página 2: Cadastro Pessoa│
│  ┌──────────────────────────────┐        ┌──────────────────────┐ │
│  │ CNPJ: [11.222.333/0001-81]  │        │ CPF: [123.456.789]  │ │
│  │ Razão Social: [Auto]        │        │ CEP: [01310-100]    │ │
│  │ Logradouro: [Auto]          │        │ Logradouro: [Auto]  │ │
│  │ Telefone: [Auto]            │        │ Cidade: [Auto]      │ │
│  │ Email: [Auto]               │        │ ...                 │ │
│  └──────┬───────────────────────┘        └──────┬──────────────┘ │
│         │                                       │                 │
└─────────┼───────────────────────────────────────┼─────────────────┘
          │                                       │
          │  Ambos incluem:                       │
          │  <script src="/.../script_cpf_cep_apis.js"></script>
          │
          ▼─────────────────────────────────────▼
┌──────────────────────────────────────────────────────────────────────┐
│                    📱 JAVASCRIPT (Navegador)                         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  script_cpf_cep_apis.js                                              │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                                                               │  │
│  │  setupCNPJValidation('cnpj') {                               │  │
│  │    addEventListener('blur', async () => {                   │  │
│  │      validarCNPJ() → POST /api/v1/externas/cnpj/validar    │  │
│  │                     → preencherEmpresa(dados)                │  │
│  │    })                                                        │  │
│  │  }                                                           │  │
│  │                                                               │  │
│  │  setupCEPConsultation('cep') {                               │  │
│  │    addEventListener('blur', async () => {                   │  │
│  │      consultarCEP() → POST /api/v1/externas/cep/consultar   │  │
│  │                     → preencherEndereco(dados)               │  │
│  │    })                                                        │  │
│  │  }                                                           │  │
│  │                                                               │  │
│  │  setupCPFValidation('cpf') {                                │  │
│  │    addEventListener('blur', async () => {                   │  │
│  │      validarCPF() → POST /api/v1/externas/cpf/validar       │  │
│  │    })                                                        │  │
│  │  }                                                           │  │
│  │                                                               │  │
│  └───────┬───────────────────────────────────────────────────┬──┘  │
│          │                                                   │       │
└──────────┼───────────────────────────────────────────────────┼───────┘
           │        HTTP REQUESTS                             │
           │        (JSON)                                    │
           ▼                                                   ▼
┌────────────────────────────────────────────────────────────────────┐
│                   🖥️ SERVIDOR (FastAPI - Python)                   │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  app/routers/M01_auth/router_externas_cpf_cep.py                 │
│  ┌───────────────────────────────────────────────────────────────┐│
│  │                                                               ││
│  │  POST /api/v1/externas/cnpj/validar                          ││
│  │  ├─ Recebe: { "cnpj": "11222333000181" }                    ││
│  │  ├─ Chama: CNPJService.validar_cnpj_formato()               ││
│  │  ├─ Chama: CNPJService.consultar_cnpj()                     ││
│  │  └─ Retorna: { valido, nome, email, telefone, ... }         ││
│  │                                                               ││
│  │  POST /api/v1/externas/cep/consultar                         ││
│  │  ├─ Recebe: { "cep": "01310100" }                            ││
│  │  ├─ Chama: CEPService.consultar_cep()                        ││
│  │  └─ Retorna: { logradouro, bairro, cidade, uf, ... }        ││
│  │                                                               ││
│  │  POST /api/v1/externas/cpf/validar                           ││
│  │  ├─ Recebe: { "cpf": "12345678910" }                         ││
│  │  ├─ Chama: CPFService.validar_cpf_formato()                 ││
│  │  └─ Retorna: { valido, cpf, mensagem }                       ││
│  │                                                               ││
│  └───────┬─────────────────────────────────┬─────────────────┬──┘│
│          │                                 │                 │    │
│          ▼                                 ▼                 ▼    │
│  ┌──────────────────┐            ┌──────────────────┐ ┌─────────┐│
│  │ CNPJService      │            │ CEPService       │ │CPFServ. ││
│  │ ┌──────────────┐ │            │ ┌──────────────┐ │ │┌────────┐│
│  │ │ validar_cpf_│ │            │ │ consultar_  │ │ ││validar│ │
│  │ │ formato()   │ │            │ │ cep()       │ │ ││cpf_   │ │
│  │ └──────────────┘ │            │ └──────────────┘ │ ││formato││
│  │ ┌──────────────┐ │            │ ┌──────────────┐ │ │└────────┘│
│  │ │ consultar_  │ │            │ │ (Calls       │ │ └─────────┘│
│  │ │ cnpj()      │ │            │ │  ViaCEP API) │ │            │
│  │ │ (Calls RF)  │ │            │ └──────────────┘ │            │
│  │ └──────┬───────┘ │            └──────────────────┘            │
│  └────────┼─────────┘                                             │
│           │                                                        │
└───────────┼────────────────────────────────────────────────────────┘
            │
            │  HTTP Request (via aiohttp)
            │
            ▼─────────────────────────────────────────────────────────
    ┌──────────────────────────────────────────────────────────────┐
    │         🌐 EXTERNAL APIs (Fora do Servidor)                  │
    ├──────────────────────────────────────────────────────────────┤
    │                                                              │
    │  1️⃣ ReceitaWS                                              │
    │     https://www.receitaws.com.br/v1/cnpj/{cnpj}           │
    │     ├─ Input: CNPJ (ex: 11222333000181)                   │
    │     └─ Output: Dados completos da empresa                 │
    │        {                                                   │
    │          "nome": "EMPRESA TESTE LTDA",                    │
    │          "nome_fantasia": "EMPRESA TESTE",                │
    │          "logradouro": "RUA TESTE",                       │
    │          "numero": "123",                                 │
    │          "telefone": "(11) 3333-3333",                    │
    │          "email": "contato@empresa.com.br"                │
    │        }                                                   │
    │                                                              │
    │  2️⃣ ViaCEP                                                │
    │     https://viacep.com.br/ws/{cep}/json/                  │
    │     ├─ Input: CEP (ex: 01310100)                          │
    │     └─ Output: Dados de endereço                          │
    │        {                                                   │
    │          "logradouro": "Avenida Paulista",                │
    │          "bairro": "Bela Vista",                          │
    │          "localidade": "São Paulo",                       │
    │          "uf": "SP"                                       │
    │        }                                                   │
    │                                                              │
    └──────────────────────────────────────────────────────────────┘
```

---

## 📊 Fluxo de Dados Detalhado

### CNPJ Flow:

```
USER TYPES IN BROWSER
        │
        ▼
CNPJ: [11.222.333/0001-81]
        │
        │ (blur event)
        ▼
JavaScript formatarCNPJ()
        │ "11.222.333/0001-81" → "11222333000181"
        ▼
POST /api/v1/externas/cnpj/validar
Body: { "cnpj": "11222333000181" }
        │
        ▼
Backend: router_externas_cpf_cep.py
        │
        ▼
CNPJService.consultar_cnpj(cnpj)
        │
        ├─ Valida checksum
        │
        ├─ Formata URL: https://www.receitaws.com.br/v1/cnpj/11222333000181
        │
        ├─ Faz requisição aiohttp
        │
        └─ ReceitaWS retorna dados
        │
        ▼
Backend monta resposta:
{
  "valido": true,
  "cnpj": "11222333000181",
  "nome": "EMPRESA TESTE LTDA",
  "nome_fantasia": "EMPRESA TESTE",
  "logradouro": "RUA TESTE",
  "numero": "123",
  "complemento": "APT 401",
  "bairro": "BAIRRO TESTE",
  "municipio": "SAO PAULO",
  "uf": "SP",
  "cep": "01310100",
  "telefone": "(11) 3333-3333",
  "email": "contato@empresa.com.br",
  "mensagem": "CNPJ validado com sucesso"
}
        │
        ▼
HTTP Response 200 OK
        │ (JSON)
        ▼
Javascript recebe response.json()
        │
        ▼
preencherEmpresa(data)
        │
        ├─ document.getElementById('razaoSocial').value = "EMPRESA TESTE LTDA"
        ├─ document.getElementById('nomeFantasia').value = "EMPRESA TESTE"
        ├─ document.getElementById('logradouro').value = "RUA TESTE"
        ├─ document.getElementById('numero').value = "123"
        ├─ document.getElementById('complemento').value = "APT 401"
        ├─ document.getElementById('bairro').value = "BAIRRO TESTE"
        ├─ document.getElementById('cidade').value = "SAO PAULO"
        ├─ document.getElementById('uf').value = "SP"
        ├─ document.getElementById('cep').value = "01310-100"
        ├─ document.getElementById('telefone').value = "(11) 3333-3333"
        └─ document.getElementById('email').value = "contato@empresa.com.br"
        │
        ▼
USER SEES ALL FIELDS FILLED ✨
```

### CEP Flow:

```
USER TYPES IN BROWSER
        │
        ▼
CEP: [01310-100]
        │
        │ (blur event)
        ▼
Javascript formatarCEP()
        │ "01310-100" → "01310100"
        ▼
POST /api/v1/externas/cep/consultar
Body: { "cep": "01310100" }
        │
        ▼
Backend: router_externas_cpf_cep.py
        │
        ▼
CEPService.consultar_cep(cep)
        │
        ├─ Valida formato
        │
        ├─ Formata URL: https://viacep.com.br/ws/01310100/json/
        │
        ├─ Faz requisição aiohttp
        │
        └─ ViaCEP retorna dados
        │
        ▼
Backend monta resposta:
{
  "cep": "01310-100",
  "logradouro": "Avenida Paulista",
  "bairro": "Bela Vista",
  "localidade": "São Paulo",
  "uf": "SP",
  "complemento": "",
  "mensagem": "CEP consultado com sucesso"
}
        │
        ▼
HTTP Response 200 OK
        │ (JSON)
        ▼
Javascript recebe response.json()
        │
        ▼
preencherEndereco(data)
        │
        ├─ document.getElementById('logradouro').value = "Avenida Paulista"
        ├─ document.getElementById('bairro').value = "Bela Vista"
        ├─ document.getElementById('cidade').value = "São Paulo"
        └─ document.getElementById('uf').value = "SP"
        │
        ▼
USER SEES ADDRESS FILLED ✨
```

---

## 🎯 Mapeamento de Componentes

```
┌───────────────────────────────────────────────────────────────────┐
│                      FRONTEND (Cliente)                           │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  templates/pages/M01_auth/                                        │
│  ├─ template_auth_cadastro_pessoa_fisica_pagina.html             │
│  │  └─ Inclui: script_cpf_cep_apis.js                            │
│  │     setupCPFValidation('cpf')                                 │
│  │     setupCEPConsultation('cep')                               │
│  │                                                                │
│  └─ template_auth_cadastro_instituicao_pagina.html              │
│     └─ Inclui: script_cpf_cep_apis.js                            │
│        setupCNPJValidation('cnpj')                               │
│        setupCEPConsultation('cep')                               │
│                                                                   │
│  static/js/M01_auth/                                              │
│  └─ script_cpf_cep_apis.js                                       │
│     ├─ formatarCPF(cpf)                                          │
│     ├─ limparCPF(cpf)                                            │
│     ├─ validarCPF(cpf)                                           │
│     ├─ formatarCNPJ(cnpj)                                        │
│     ├─ limparCNPJ(cnpj)                                          │
│     ├─ validarCNPJ(cnpj)                                         │
│     ├─ preencherEmpresa(dados)                                   │
│     ├─ consultarCEP(cep)                                         │
│     ├─ preencherEndereco(dados)                                  │
│     ├─ setupCPFValidation(fieldId)                               │
│     ├─ setupCNPJValidation(fieldId)                              │
│     ├─ setupCEPConsultation(fieldId)                             │
│     └─ window.CPFCEPApis = {...}                                 │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
                        ↕️ HTTP JSON
┌───────────────────────────────────────────────────────────────────┐
│                    BACKEND (Servidor)                             │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  app/routers/M01_auth/                                            │
│  └─ router_externas_cpf_cep.py                                   │
│     ├─ POST /api/v1/externas/cnpj/validar                        │
│     │  └─ CNPJService.consultar_cnpj()                           │
│     ├─ POST /api/v1/externas/cpf/validar                         │
│     │  └─ CPFService.consultar_cpf()                             │
│     └─ POST /api/v1/externas/cep/consultar                       │
│        └─ CEPService.consultar_cep()                             │
│                                                                   │
│  app/services/M01_auth/                                           │
│  └─ service_external_apis.py                                     │
│     ├─ class CNPJService:                                        │
│     │  ├─ validar_cnpj_formato(cnpj)                             │
│     │  └─ consultar_cnpj(cnpj) → ReceitaWS API call            │
│     ├─ class CPFService:                                         │
│     │  ├─ validar_cpf_formato(cpf)                               │
│     │  └─ consultar_cpf(cpf) → Validation (ready for RF)       │
│     └─ class CEPService:                                         │
│        └─ consultar_cep(cep) → ViaCEP API call                 │
│                                                                   │
│  app/schemas/ (ou models)                                         │
│  └─ Pydantic Models                                              │
│     ├─ CNPJValidationRequest                                     │
│     ├─ CNPJValidationResponse (15 fields)                        │
│     ├─ CPFValidationRequest                                      │
│     ├─ CPFValidationResponse                                     │
│     ├─ CEPConsultaRequest                                        │
│     └─ CEPConsultaResponse                                       │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
                    ↕️ aiohttp (async)
┌───────────────────────────────────────────────────────────────────┐
│                   EXTERNAL APIs                                   │
├───────────────────────────────────────────────────────────────────┤
│                                                                   │
│  📦 ReceitaWS                                                    │
│  ├─ Base URL: https://www.receitaws.com.br/                     │
│  ├─ Endpoint: v1/cnpj/{cnpj}                                    │
│  └─ Retorna: Empresa + Endereço + Contato (13+ fields)         │
│                                                                   │
│  📦 ViaCEP                                                       │
│  ├─ Base URL: https://viacep.com.br/                            │
│  ├─ Endpoint: ws/{cep}/json/                                    │
│  └─ Retorna: Endereço (7 fields)                                │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Ciclo de Vida da Requisição

```
┌─────────────────────────────────────────────────────────────────────┐
│                                                                     │
│  1. INICIALIZAÇÃO (DOMContentLoaded)                               │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                             │
│     ├─ Script carrega: script_cpf_cep_apis.js                      │
│     ├─ setupCNPJValidation('cnpj') cria listener                   │
│     ├─ setupCPFValidation('cpf') cria listener                     │
│     └─ setupCEPConsultation('cep') cria listener                   │
│                                                                     │
│  2. USUÁRIO DIGITA                                                 │
│  ━━━━━━━━━━━━━━━━━━                                               │
│     └─ CNPJ: [11.222.333/0001-81]                                 │
│     └─ CPF: [123.456.789-10]                                      │
│     └─ CEP: [01310-100]                                           │
│                                                                     │
│  3. EVENTO BLUR (Sai do campo)                                     │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                     │
│     └─ addEventListener('blur', async () => { ... })              │
│                                                                     │
│  4. VALIDAÇÃO CLIENT-SIDE                                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━                                        │
│     ├─ Formata: remove máscaras                                    │
│     ├─ Valida checksum (CPF/CNPJ) OU se é CEP válido             │
│     └─ Se inválido → exibe erro, para aqui                        │
│                                                                     │
│  5. HTTP REQUEST (Assíncrono)                                      │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━                                       │
│     └─ fetch() POST para /api/v1/externas/{tipo}/...             │
│        Body: { "cnpj": "..." } ou { "cep": "..." }               │
│                                                                     │
│  6. BACKEND PROCESSAMENTO                                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━                                        │
│     ├─ Recebe requisição em router                                │
│     ├─ Chama Service correspondente                               │
│     ├─ Service faz aiohttp request para API externa              │
│     ├─ Processa resposta da API                                   │
│     └─ Retorna JSON estruturado                                   │
│                                                                     │
│  7. API EXTERNA RESPONDE                                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━                                        │
│     ├─ ReceitaWS: retorna dados da empresa (se CNPJ)             │
│     └─ ViaCEP: retorna dados do endereço (se CEP)                │
│                                                                     │
│  8. HTTP RESPONSE (JSON)                                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━                                          │
│     └─ 200 OK { "valido": true, "nome": "...", ... }             │
│     └─ 400 Bad Request (validação falhou)                        │
│     └─ 500 Server Error (erro no backend)                        │
│                                                                     │
│  9. JAVASCRIPT PROCESSA RESPOSTA                                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━                                   │
│     ├─ Se response.ok:                                            │
│     │  ├─ data = response.json()                                  │
│     │  ├─ if (data.valido) {                                      │
│     │  │   preencherEmpresa(data)   OU                            │
│     │  │   preencherEndereco(data)                                │
│     │  │ }                                                        │
│     │  └─ mostrarSucesso(fieldId)                                 │
│     └─ Se !response.ok:                                           │
│        └─ mostrarErro(fieldId, mensagem)                          │
│                                                                     │
│  10. PREENCHER CAMPOS                                              │
│  ━━━━━━━━━━━━━━━━━━━━━━━                                          │
│      ├─ document.getElementById('razaoSocial').value = data.nome  │
│      ├─ document.getElementById('logradouro').value = data.rua    │
│      ├─ document.getElementById('cidade').value = data.cidade     │
│      └─ ... todos os campos ...                                   │
│                                                                     │
│  11. ESTILO VISUAL                                                 │
│  ━━━━━━━━━━━━━━━━━                                                │
│      ├─ Adiciona classe 'is-valid' (campo fica verde)            │
│      └─ Exibe mensagem de sucesso                                 │
│                                                                     │
│  12. USUÁRIO VÊ RESULTADO                                          │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━                                        │
│      └─ ✨ Todos os campos preenchidos!                            │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Checklist de Integração

```
FRONTEND
├─ [x] script_cpf_cep_apis.js existe
├─ [x] HTML tem IDs corretos (cnpj, razaoSocial, logradouro, etc)
├─ [x] Script incluído em template_auth_cadastro_instituicao_pagina.html
├─ [x] Script incluído em template_auth_cadastro_pessoa_fisica_pagina.html
├─ [x] setupCNPJValidation('cnpj') inicializado
├─ [x] setupCPFValidation('cpf') inicializado
└─ [x] setupCEPConsultation('cep') inicializado

BACKEND
├─ [x] router_externas_cpf_cep.py existe
├─ [x] Endpoint POST /api/v1/externas/cnpj/validar implementado
├─ [x] Endpoint POST /api/v1/externas/cpf/validar implementado
├─ [x] Endpoint POST /api/v1/externas/cep/consultar implementado
├─ [x] service_external_apis.py com CNPJService
├─ [x] service_external_apis.py com CPFService
├─ [x] service_external_apis.py com CEPService
├─ [x] aiohttp instalado (para requisições assíncronas)
└─ [x] Pydantic models/schemas para requests/responses

EXTERNAL APIs
├─ [x] ReceitaWS está acessível (testa com curl)
├─ [x] ViaCEP está acessível (testa com curl)
└─ [x] Sem autenticação necessária (ambas free)

TESTES
├─ [ ] CNPJ válido → Preenche todos os campos
├─ [ ] CNPJ inválido → Exibe erro
├─ [ ] CEP válido → Preenche endereço
├─ [ ] CEP inválido → Exibe erro
├─ [ ] CPF válido → Campo fica verde
├─ [ ] CPF inválido → Campo fica vermelho
└─ [ ] Sem erros no console do navegador
```

---

**Status:** ✅ **ARQUITETURA COMPLETA**

**Próximos passos:** Testar em `http://127.0.0.1:8010/docs` e nas páginas HTML!
