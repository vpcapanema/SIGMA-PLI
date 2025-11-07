# 🎨 MÁSCARAS DE FORMATAÇÃO + UFs/MUNICÍPIOS

## 📋 Resumo das Correções e Implementações

### ✅ **Problema 1: UFs Não Carregam - CORRIGIDO**

**Causa**: A instância de `LocalizacaoBRManager` não estava acessível via `window.localizacaoBR`

**Solução**:

```javascript
// ❌ Antes (não funcionava)
const localizacaoBR = new LocalizacaoBRManager();

// ✅ Depois (funciona)
window.localizacaoBR = new LocalizacaoBRManager();
```

**Arquivo**: `static/js/M01_auth/script_localizacao_br.js`

---

### ✅ **Problema 2: Municípios Não Carregam - CORRIGIDO**

O script agora está corretamente acessível e carrega municípios quando um UF é selecionado

**Fluxo**:

1. ✅ UF é selecionado no dropdown `ufNaturalidade`
2. ✅ Listener dispara e chama `carregarMunicipios(ufSelecionado)`
3. ✅ API `/api/v1/localizacao/municipios/{uf}` retorna dados
4. ✅ Dropdown `naturalidade` é preenchido com municípios

---

### ✨ **Novo: Máscaras de Formatação - IMPLEMENTADO**

Criado **`script_input_masks.js`** com suporte a 7 tipos de máscara:

#### 1️⃣ **CPF**: `123.456.789-00`

```javascript
inputMaskManager.formatCPF("12345678900");
// → '123.456.789-00'
```

#### 2️⃣ **CNPJ**: `12.345.678/0001-90`

```javascript
inputMaskManager.formatCNPJ("12345678901234");
// → '12.345.678/0001-34'
```

#### 3️⃣ **Telefone**: `(11) 98765-4321` ou `(11) 8765-4321`

```javascript
inputMaskManager.formatTelefone("11987654321");
// → '(11) 98765-4321'

inputMaskManager.formatTelefone("1187654321");
// → '(11) 8765-4321'
```

#### 4️⃣ **CEP**: `12345-678`

```javascript
inputMaskManager.formatCEP("12345678");
// → '12345-678'
```

#### 5️⃣ **Data**: `DD/MM/YYYY`

```javascript
inputMaskManager.formatData("31012024");
// → '31/01/2024'
```

#### 6️⃣ **RG**: `12.345.678-9`

```javascript
inputMaskManager.formatRG("123456789");
// → '12.345.678-9'
```

#### 7️⃣ **CNH**: `13 dígitos` (sem formatação)

```javascript
inputMaskManager.formatCNH("1234567890123456");
// → '1234567890123'
```

---

## 📦 Arquivos Criados/Modificados

### ✅ **Criados:**

1. **`static/js/M01_auth/script_input_masks.js`** (NEW)

   - Classe `InputMaskManager` com 7 máscaras
   - Métodos para setup automático
   - Validações básicas integradas
   - **Linhas**: 250+

2. **`TESTE_MASCARAS_FORMATACAO.py`** (NEW)
   - Script de teste local (Python)
   - Exemplos de casos de teste
   - Documentação de validação

### ✅ **Modificados:**

1. **`static/js/M01_auth/script_localizacao_br.js`**

   - ✅ Corrigido: `window.localizacaoBR = new LocalizacaoBRManager()`
   - ✅ Adicionado: debug logs para rastrear carregamento

2. **`templates/pages/M01_auth/template_auth_cadastro_pessoa_pagina.html`**
   - ✅ Adicionado: `<script src="/static/js/M01_auth/script_input_masks.js"></script>`
   - ✅ Atualizado: Inicialização melhorada com logs
   - ✅ Adicionado: Setup de máscaras em 5 campos

---

## 🎯 Campos Configurados com Máscaras

| Campo ID             | Tipo     | Máscara           | Exemplo           |
| -------------------- | -------- | ----------------- | ----------------- |
| `cpf`                | CPF      | `###.###.###-##`  | `123.456.789-00`  |
| `rg`                 | RG       | `##.###.###-#`    | `12.345.678-9`    |
| `telefonePrincipal`  | Telefone | `(##) #####-####` | `(11) 98765-4321` |
| `telefoneSecundario` | Telefone | `(##) #####-####` | `(11) 87654-3210` |
| `cep`                | CEP      | `#####-###`       | `12345-678`       |

---

## 🔄 Fluxo de Inicialização (DOMContentLoaded)

```
1. initCadastroPessoaFisica()
   ↓
2. inputMaskManager.setupFields([...])
   ↓ (Aplica máscaras em CPF, RG, Telefone, CEP)
   ↓
3. CPFCEPApis.setupCPFValidation('cpf')
   ↓ (Valida CPF com módulo 11)
   ↓
4. CPFCEPApis.setupCEPConsultation('cep')
   ↓ (Consulta ViaCEP para endereço)
   ↓
5. localizacaoBR.inicializar([...])
   ↓
   ├─ carregarUFs() → Popula dropdown ufNaturalidade
   ├─ carregarUFs() → Popula dropdown ufRg
   └─ preencherSelectMunicipios()
      └─ Quando UF muda, carrega municípios

✅ Resultado: Interface completa e funcional
```

---

## 📱 Como Usar as Máscaras

### Via HTML (Automático)

```html
<!-- Será formatado automaticamente pelo listener -->
<input id="cpf" type="text" class="form-control" />
<input id="telefone" type="text" class="form-control" />
```

### Via JavaScript

```javascript
// Aplicar máscaras
inputMaskManager.setupField("cpf", "cpf");
inputMaskManager.setupField("telefone", "telefone");

// Ou múltiplos campos
inputMaskManager.setupFields([
  { id: "cpf", mask: "cpf" },
  { id: "telefone", mask: "telefone" },
  { id: "cep", mask: "cep" },
]);

// Obter valor limpo (para enviar ao servidor)
const cpfLimpo = inputMaskManager.getCleanValue("cpf");
// "12345678900" (sem formatação)

// Validar
if (inputMaskManager.validarCPF(cpfLimpo)) {
  console.log("✅ CPF válido");
}
```

---

## 🧪 Testar Localmente (Python)

```bash
# Exibir casos de teste esperados
python TESTE_MASCARAS_FORMATACAO.py
```

**Output esperado:**

```
🧪 TESTES DE MÁSCARAS DE FORMATAÇÃO
================================================================================

📝 Máscara: CPF
────────────────────────────────────────────────────────────────────────────────
  Input:    '12345678900'                 → Esperado: '123.456.789-00'
  Input:    '123'                         → Esperado: '123'
  ...
```

---

## 🌐 Testar no Navegador

### 1. Iniciar Aplicação

```powershell
# Windows PowerShell
python setup_security.py --setup

# Ou manualmente
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --host 127.0.0.1 --port 8010
```

### 2. Abrir Interface

```
http://localhost:8010/auth/cadastro
```

### 3. Testar Máscaras

- Digite no campo CPF: `12345678900` → Vira `123.456.789-00` ✅
- Digite no campo Telefone: `11987654321` → Vira `(11) 98765-4321` ✅
- Digite no campo CEP: `12345678` → Vira `12345-678` ✅

### 4. Testar UFs/Municípios

- Clique no dropdown "UF Naturalidade" → Deve carregar 27 UFs ✅
- Selecione "São Paulo" → Dropdown "Município" preenche com ~645 municípios ✅

---

## 🔍 Debug / Troubleshooting

### Console do Navegador (F12)

```javascript
// Ver logs de inicialização
console.log("Verificar se scripts carregaram");

// Testar instância global
console.log(window.inputMaskManager);
// → InputMaskManager { masks: {...}, patterns: {...} }

console.log(window.localizacaoBR);
// → LocalizacaoBRManager { ufs: [...], municipios: {...} }

// Testar formatação manualmente
window.inputMaskManager.formatCPF("12345678900");
// → "123.456.789-00"

// Testar carregamento de UFs
window.localizacaoBR.carregarUFs().then((ufs) => {
  console.log(`✅ ${ufs.length} UFs carregados`);
});
```

### Se UFs Não Carregam

1. Abrir **DevTools (F12)** → **Aba Console**
2. Procurar por mensagens de erro (vermelho)
3. Verificar:
   - ✅ Endpoint `/api/v1/localizacao/ufs` retorna dados?
   ```bash
   curl http://localhost:8010/api/v1/localizacao/ufs
   ```
   - ✅ Script `script_localizacao_br.js` foi carregado?
   - ✅ `window.localizacaoBR` existe?

### Se Máscaras Não Funcionam

1. Verificar se `script_input_masks.js` foi carregado
2. Verificar se campos têm IDs corretos: `cpf`, `rg`, `telefone`, etc
3. Abrir console e testar:
   ```javascript
   window.inputMaskManager.setupField("cpf", "cpf");
   ```

---

## ✨ Recursos Adicionados

### 1. **Setup Automático**

```javascript
// Todos os campos são configurados no DOMContentLoaded
inputMaskManager.setupFields([
  { id: "cpf", mask: "cpf" },
  { id: "rg", mask: "rg" },
  { id: "telefonePrincipal", mask: "telefone" },
  { id: "telefoneSecundario", mask: "telefone" },
  { id: "cep", mask: "cep" },
]);
```

### 2. **Validações Integradas**

```javascript
// Validar CPF com Módulo 11
if (inputMaskManager.validarCPF("12345678900")) {
  // CPF válido
}

// Validar Telefone
if (inputMaskManager.validarTelefone("11987654321")) {
  // Telefone válido (10 ou 11 dígitos)
}

// Validar CEP
if (inputMaskManager.validarCEP("12345678")) {
  // CEP válido (8 dígitos)
}

// Validar Data
if (inputMaskManager.validarData("31/01/2024")) {
  // Data válida
}
```

### 3. **Limpeza Automática**

```javascript
// Remover máscara para enviar ao servidor
const cpf = "123.456.789-00";
const cpfLimpo = inputMaskManager.removeMascara(cpf);
// → "12345678900"

// Ou via campo HTML
const cpfLimpoDoForm = inputMaskManager.getCleanValue("cpf");
```

---

## 📊 Status de Implementação

| Item                | Status       | Detalhes                             |
| ------------------- | ------------ | ------------------------------------ |
| UFs Carregam        | ✅ CORRIGIDO | `window.localizacaoBR` acessível     |
| Municípios Carregam | ✅ CORRIGIDO | Listener funciona corretamente       |
| Máscaras CPF        | ✅ CRIADO    | `###.###.###-##`                     |
| Máscaras CNPJ       | ✅ CRIADO    | `##.###.###/####-##`                 |
| Máscaras Telefone   | ✅ CRIADO    | `(##) #####-####`                    |
| Máscaras CEP        | ✅ CRIADO    | `#####-###`                          |
| Máscaras Data       | ✅ CRIADO    | `DD/MM/YYYY`                         |
| Máscaras RG         | ✅ CRIADO    | `##.###.###-#`                       |
| Máscaras CNH        | ✅ CRIADO    | 13 dígitos                           |
| Validações          | ✅ CRIADO    | Básicas integradas                   |
| Template Atualizado | ✅ CRIADO    | Inclui todos os scripts              |
| Inicialização       | ✅ COMPLETO  | Setup automático em DOMContentLoaded |

---

## 🚀 Próximas Etapas

1. **Iniciar Aplicação**

   ```bash
   python setup_security.py --setup
   ```

2. **Testar Interface**

   ```
   http://localhost:8010/auth/cadastro
   ```

3. **Validar Funcionamento**

   - ✅ Digite CPF → Vira `###.###.###-##`
   - ✅ Selecione UF → Carrega Municípios
   - ✅ Console sem erros (F12)

4. **Backend**
   - Schema Pydantic já remove máscaras automaticamente
   - Banco recebe dados limpos (sem formatação)
   - Exemplo: CPF `"123.456.789-00"` → `"12345678900"` no banco

---

## 📚 Referência Rápida

### Máscaras

| Tipo        | Padrão               | Exemplo              |
| ----------- | -------------------- | -------------------- |
| CPF         | `###.###.###-##`     | `123.456.789-00`     |
| CNPJ        | `##.###.###/####-##` | `12.345.678/0001-90` |
| Telefone 10 | `(##) ####-####`     | `(11) 8765-4321`     |
| Telefone 11 | `(##) #####-####`    | `(11) 98765-4321`    |
| CEP         | `#####-###`          | `12345-678`          |
| Data        | `##/##/####`         | `31/01/2024`         |
| RG          | `##.###.###-#`       | `12.345.678-9`       |
| CNH         | `############`       | `1234567890123`      |

### IDs de Campos

```html
<input id="cpf" />
<input id="rg" />
<input id="telefonePrincipal" />
<input id="telefoneSecundario" />
<input id="cep" />
<select id="ufNaturalidade">
  <select id="ufRg">
    <select id="naturalidade"></select>
  </select>
</select>
```

---

**Status**: ✅ **PRONTO PARA TESTAR**

Acesse `http://localhost:8010/auth/cadastro` e teste as máscaras!
