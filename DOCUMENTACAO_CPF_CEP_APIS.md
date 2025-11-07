# Integração de APIs de CPF e CEP - Documentação

## 📋 Visão Geral

Este documento descreve a implementação de validação automática de CPF e consulta de CEP no formulário de cadastro de pessoa física do SIGMA-PLI.

## 🎯 Funcionalidades Implementadas

### 1. **Validação de CPF em Tempo Real**

- Validação de formato (11 dígitos)
- Validação de dígitos verificadores (algoritmo oficial)
- Feedback visual instantâneo
- Formatação automática: `XXX.XXX.XXX-XX`

### 2. **Consulta Automática de CEP**

- Integração com API ViaCEP (gratuita e confiável)
- Busca automática ao sair do campo
- Preenchimento automático de:
  - Logradouro
  - Bairro
  - Cidade
  - Estado (UF)
- Formatação automática do CEP: `XXXXX-XXX`

### 3. **Feedback Visual**

- ✅ Validação bem-sucedida (verde)
- ❌ Validação falha (vermelho)
- ⏳ Carregamento (animação de spinner)
- 📝 Mensagens descritivas de erro

## 📂 Estrutura de Arquivos

```
SIGMA-PRINCIPAL/
├── app/
│   ├── services/M01_auth/
│   │   └── service_external_apis.py          # Serviços de CPF e CEP
│   └── routers/M01_auth/
│       ├── router_externas_cpf_cep.py        # Endpoints das APIs
│       └── router_pages_cadastro_pessoa_fisica.py  # Página de cadastro
├── templates/pages/M01_auth/
│   └── template_cadastro_pessoa_fisica.html  # Formulário HTML
├── static/
│   ├── js/M01_auth/
│   │   └── script_cpf_cep_apis.js           # Lógica do cliente
│   └── css/M01_auth/
│       └── style_cadastro_pessoa_fisica.css # Estilos
```

## 🔌 APIs Disponíveis

### POST `/api/v1/externas/cpf/validar`

Valida um CPF usando algoritmo de dígitos verificadores.

**Requisição:**

```json
{
  "cpf": "123.456.789-09"
}
```

**Resposta (válido):**

```json
{
  "valido": true,
  "cpf": "12345678909",
  "mensagem": "CPF válido"
}
```

**Resposta (inválido):**

```json
{
  "valido": false,
  "cpf": null,
  "mensagem": "CPF inválido"
}
```

---

### POST `/api/v1/externas/cep/consultar`

Consulta dados de endereço pelo CEP usando a API ViaCEP.

**Requisição:**

```json
{
  "cep": "01310-100"
}
```

**Resposta (encontrado):**

```json
{
  "cep": "01310100",
  "logradouro": "Avenida Paulista",
  "bairro": "Bela Vista",
  "localidade": "São Paulo",
  "uf": "SP",
  "complemento": "lado par",
  "erro": false,
  "mensagem": null
}
```

**Resposta (não encontrado):**

```json
{
  "cep": null,
  "logradouro": null,
  "bairro": null,
  "localidade": null,
  "uf": null,
  "complemento": null,
  "erro": true,
  "mensagem": "CEP não encontrado"
}
```

---

### POST `/api/v1/externas/endereco/validar`

Valida e consulta endereço pelo CEP (com fallback para entrada manual).

**Requisição:**

```json
{
  "cep": "01310100"
}
```

**Resposta:**

```json
{
  "sucesso": true,
  "origem": "cep",
  "dados": {
    "cep": "01310100",
    "logradouro": "Avenida Paulista",
    "bairro": "Bela Vista",
    "localidade": "São Paulo",
    "uf": "SP",
    "complemento": "lado par"
  }
}
```

## 🖥️ Página de Cadastro

**URL:** `/cadastro/pessoa-fisica`

A página possui:

1. **Seção de Dados Pessoais**

   - Nome Completo
   - CPF (com validação automática)
   - Data de Nascimento
   - E-mail
   - Telefone

2. **Seção de Dados de Endereço**
   - CEP (com busca automática)
   - Logradouro (preenchido automaticamente)
   - Número
   - Complemento
   - Bairro (preenchido automaticamente)
   - Cidade (preenchido automaticamente)
   - Estado (preenchido automaticamente)

## 💻 Como Usar no Frontend

### Validação de CPF

```javascript
// Validar um CPF
const resultado = await window.CPFCEPApis.validarCPF("123.456.789-09");
console.log(resultado); // { valido: true, ... }

// Formatar CPF
const cpf_formatado = window.CPFCEPApis.formatarCPF("12345678909");
console.log(cpf_formatado); // "123.456.789-09"

// Limpar formatação
const cpf_limpo = window.CPFCEPApis.limparCPF("123.456.789-09");
console.log(cpf_limpo); // "12345678909"
```

### Consulta de CEP

```javascript
// Consultar CEP
const endereco = await window.CPFCEPApis.consultarCEP("01310-100");
console.log(endereco); // { cep: "01310100", logradouro: "Avenida Paulista", ... }

// Formatar CEP
const cep_formatado = window.CPFCEPApis.formatarCEP("01310100");
console.log(cep_formatado); // "01310-100"

// Limpar formatação
const cep_limpo = window.CPFCEPApis.limparCEP("01310-100");
console.log(cep_limpo); // "01310100"

// Preencher endereço automaticamente
window.CPFCEPApis.preencherEndereco(endereco);
```

## 🔐 Segurança

- ✅ Validação no cliente (feedback rápido)
- ✅ Validação no servidor (segurança)
- ✅ Sem armazenamento de dados sensíveis
- ✅ HTTPS obrigatório em produção
- ✅ Rate limiting recomendado para APIs públicas

## 🌐 APIs Externas Utilizadas

### ViaCEP

- **URL:** https://viacep.com.br/ws/
- **Documentação:** https://viacep.com.br/
- **Limite:** Até 1 requisição por segundo
- **Autenticação:** Não requerida
- **Custo:** Gratuito

## 🧪 Testando as APIs

Use o Swagger/OpenAPI em `/docs`:

1. Acesse: `http://localhost:8010/docs`
2. Procure por `/api/v1/externas/`
3. Clique em "Try it out"
4. Preencha o CPF ou CEP
5. Clique em "Execute"

## 🐛 Tratamento de Erros

| Erro                         | Causa                            | Solução           |
| ---------------------------- | -------------------------------- | ----------------- |
| "CPF deve conter 11 dígitos" | Formato incorreto                | Verifique o CPF   |
| "CPF inválido"               | Dígitos verificadores incorretos | Valide o CPF      |
| "CEP deve conter 8 dígitos"  | Formato incorreto                | Verifique o CEP   |
| "CEP não encontrado"         | CEP inexistente                  | Use um CEP válido |
| Timeout                      | API externa indisponível         | Tente novamente   |

## 📱 Responsividade

O formulário é totalmente responsivo:

- ✅ Desktop (1024px+)
- ✅ Tablet (768px - 1023px)
- ✅ Mobile (< 768px)
- ✅ Fonte maior em mobile para melhor legibilidade
- ✅ Botões em tamanho touch-friendly

## 🚀 Próximas Melhorias

- [ ] Integração com API de validação de CPF (retornando dados da Receita Federal)
- [ ] Cache de CEPs consultados
- [ ] Busca de CEP por logradouro/cidade
- [ ] Validação de e-mail em tempo real
- [ ] Formatação automática de telefone
- [ ] Suporte a endereços internacionais

## 📞 Suporte

Para dúvidas ou problemas:

1. Consulte a documentação de APIs: `/docs`
2. Verifique o console do navegador para erros
3. Contate o desenvolvedor do projeto

---

**Versão:** 1.0.0  
**Última atualização:** 4 de novembro de 2025
