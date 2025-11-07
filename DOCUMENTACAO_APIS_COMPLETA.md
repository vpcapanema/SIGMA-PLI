# 📋 APIs de CPF, CNPJ e CEP - Implementação Completa

## 🎯 Resumo da Implementação

Implementei **3 APIs de preenchimento automático** que consultam dados em tempo real de órgãos públicos:

### 1. **API de CPF** (Pessoa Física)

- ✅ Validação de formato (11 dígitos)
- ✅ Validação de dígitos verificadores
- ✅ Feedback visual instantâneo
- 📌 Pronto para integração com APIs de CPF (RF)

### 2. **API de CNPJ** (Pessoa Jurídica) ⭐

- ✅ Validação de formato (14 dígitos)
- ✅ Validação de dígitos verificadores
- ✅ **Consulta em tempo real na Receita Federal** via ReceitaWS
- ✅ Preenchimento automático de:
  - Razão Social
  - Nome Fantasia
  - Logradouro, Número, Complemento
  - Bairro, Município, UF, CEP
  - Telefone, E-mail

### 3. **API de CEP** (Endereço)

- ✅ Consulta via ViaCEP (gratuita)
- ✅ Preenchimento automático de:
  - Logradouro
  - Bairro
  - Cidade
  - Estado (UF)

## 🔌 Endpoints Disponíveis

### POST `/api/v1/externas/cpf/validar`

```json
Requisição:
{
    "cpf": "123.456.789-09"
}

Resposta:
{
    "valido": true,
    "cpf": "12345678909",
    "mensagem": "CPF válido"
}
```

### POST `/api/v1/externas/cnpj/validar`

```json
Requisição:
{
    "cnpj": "11.222.333/0001-81"
}

Resposta:
{
    "valido": true,
    "cnpj": "11222333000181",
    "nome": "EMPRESA LTDA",
    "nome_fantasia": "Empresa",
    "logradouro": "Rua tal",
    "numero": "123",
    "complemento": "Sala 10",
    "bairro": "Centro",
    "municipio": "São Paulo",
    "uf": "SP",
    "cep": "01310100",
    "telefone": "1133334444",
    "email": "contato@empresa.com.br",
    "mensagem": "Dados carregados com sucesso"
}
```

### POST `/api/v1/externas/cep/consultar`

```json
Requisição:
{
    "cep": "01310-100"
}

Resposta:
{
    "cep": "01310100",
    "logradouro": "Avenida Paulista",
    "bairro": "Bela Vista",
    "localidade": "São Paulo",
    "uf": "SP",
    "complemento": "lado par",
    "erro": false
}
```

## 🖥️ Uso no Frontend

### JavaScript - Funções Disponíveis

```javascript
// CNPJ
await window.CPFCEPApis.validarCNPJ("11.222.333/0001-81");
window.CPFCEPApis.formatarCNPJ("11222333000181"); // "11.222.333/0001-81"
window.CPFCEPApis.limparCNPJ("11.222.333/0001-81"); // "11222333000181"

// CPF
await window.CPFCEPApis.validarCPF("123.456.789-09");
window.CPFCEPApis.formatarCPF("12345678909"); // "123.456.789-09"

// CEP
await window.CPFCEPApis.consultarCEP("01310-100");

// Preencher campos
window.CPFCEPApis.preencherEmpresa(dados); // Preenche dados da empresa
window.CPFCEPApis.preencherEndereco(dados); // Preenche endereço
```

## 📄 Campos HTML Esperados

### Para CNPJ (Pessoa Jurídica):

```html
<input id="documento_empresa" name="cnpj" />
<!-- Campo do CNPJ -->
<input id="razao_social" name="razao_social" />
<input id="nome_fantasia" name="nome_fantasia" />
<input id="endereco_empresa" name="endereco_empresa" />
<input id="numero_empresa" name="numero" />
<input id="complemento_empresa" name="complemento" />
<input id="bairro_empresa" name="bairro" />
<input id="cidade_empresa" name="cidade" />
<input id="estado_empresa" name="uf" />
<input id="cep_empresa" name="cep" />
<input id="telefone_empresa" name="telefone" />
<input id="email_empresa" name="email" />
```

### Para CPF (Pessoa Física):

```html
<input id="documento" name="cpf" />
<!-- Campo do CPF -->
```

### Para CEP:

```html
<input id="cep" name="cep" />
<!-- Campo do CEP -->
<input id="logradouro" name="logradouro" />
<input id="bairro" name="bairro" />
<input id="cidade" name="cidade" />
<input id="estado" name="estado" />
<input id="numero" name="numero" />
<input id="complemento_endereco" name="complemento" />
```

## 🌐 APIs Externas Utilizadas

### ReceitaWS (CNPJ)

- **URL**: https://www.receitaws.com.br/v1/cnpj/
- **Autenticação**: Não necessária
- **Limite**: Não especificado
- **Custo**: Gratuito
- **Dados**: Nome, endereço, telefone, email

### ViaCEP (CEP)

- **URL**: https://viacep.com.br/ws/
- **Autenticação**: Não necessária
- **Limite**: 1 requisição/segundo
- **Custo**: Gratuito
- **Dados**: Logradouro, bairro, cidade, UF

## 🧪 Testando

### Via Swagger:

1. Acesse: `http://localhost:8010/docs`
2. Procure por `/api/v1/externas/`
3. Teste os endpoints

### CNPJ de Teste:

```
11.222.333/0001-81  (Empresa fantasma para testes)
```

### CPF de Teste (válido):

```
123.456.789-09
```

## 🔒 Segurança

- ✅ Validação no cliente (UX rápida)
- ✅ Validação no servidor (segurança)
- ✅ Sem armazenamento de dados sensíveis
- ✅ Tratamento de timeouts
- ✅ Tratamento de erros robusto
- ✅ HTTPS obrigatório em produção

## 📱 Responsividade

- ✅ Desktop (1024px+)
- ✅ Tablet (768px - 1023px)
- ✅ Mobile (< 768px)

## ⚠️ Tratamento de Erros

| Erro                          | Causa                            | Solução              |
| ----------------------------- | -------------------------------- | -------------------- |
| "CNPJ deve conter 14 dígitos" | Formato incorreto                | Verifique o CNPJ     |
| "CNPJ inválido"               | Dígitos verificadores incorretos | Valide o CNPJ        |
| "Não encontrado"              | CNPJ válido mas não existe na RF | Preencha manualmente |
| Timeout                       | API externa indisponível         | Tente novamente      |

## 🚀 Próximas Melhorias

- [ ] Integração com API de CPF (retornando dados da RF)
- [ ] Cache de CNPJs/CEPs consultados
- [ ] Busca de CEP por logradouro/cidade
- [ ] Validação de e-mail em tempo real
- [ ] Formatação automática de telefone
- [ ] Suporte a endereços internacionais
- [ ] Logs de auditoria de consultas
- [ ] Rate limiting por IP

## 📞 Suporte

Para integrar estas APIs nas páginas:

1. Certifique-se de incluir o script: `/static/js/M01_auth/script_cpf_cep_apis.js`
2. Use os IDs de input corretos
3. Consulte a documentação do Swagger: `/docs`

---

**Versão**: 2.0.0  
**Data**: 4 de novembro de 2025  
**Status**: ✅ Pronto para produção
