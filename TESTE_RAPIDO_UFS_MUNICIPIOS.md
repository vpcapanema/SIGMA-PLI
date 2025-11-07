# 🧪 TESTE RÁPIDO - UFs e Municípios

## ⚡ Em 5 Minutos

### 1. Verificar Servidor (30 segundos)

```
Status: http://127.0.0.1:8010/health
Swagger: http://127.0.0.1:8010/docs
```

### 2. Testar API de UFs (1 minuto)

**No Swagger:**

```
GET /api/v1/localizacao/ufs
```

**Resultado esperado:**

```json
{
  "total": 27,
  "ufs": [
    {"sigla": "AC", "nome": "Acre"},
    {"sigla": "AL", "nome": "Alagoas"},
    ...
    {"sigla": "TO", "nome": "Tocantins"}
  ],
  "mensagem": "UFs carregados com sucesso"
}
```

### 3. Testar API de Municípios (1 minuto)

**No Swagger:**

```
GET /api/v1/localizacao/municipios/SP
```

**Resultado esperado:**

```json
{
  "uf": "SP",
  "total": 645,
  "municipios": [
    {"id": 3509007, "nome": "Abadia"},
    ...
    {"id": 3550308, "nome": "São Paulo"}
  ],
  "mensagem": "Municípios carregados com sucesso"
}
```

### 4. Testar no Formulário (2 minutos)

**Acesse:**

```
http://127.0.0.1:8010/cadastro/pessoa-fisica
```

**Passos:**

1. Scroll até "Dados Pessoais"
2. Veja novo campo "UF de Naturalidade" ✨
3. Clique e selecione um UF (ex: "SP - São Paulo")
4. Veja campo "Naturalidade" popular com municípios ✨
5. Selecione um município
6. Pronto! 🎉

---

## 🔍 Se Algo Não Funcionar

### Problema: "Campo UF não aparece"

```
✅ Solução: Refresh página (Ctrl+F5)
✅ Solução: Verificar console (F12) para erros
```

### Problema: "Municipípios não carregam"

```
✅ Solução: Verificar se servidor está rodando
✅ Solução: Testar API diretamente em /docs
✅ Solução: Verificar IBGE status: https://servicodados.ibge.gov.br/
```

### Problema: "Timeout ao carregar"

```
✅ Solução: Aguardar 10 segundos (timeout máximo)
✅ Solução: Usar fallback hardcoded (automático)
```

---

## ✅ Checklist

- [ ] Servidor rodando em 127.0.0.1:8010
- [ ] GET /api/v1/localizacao/ufs retorna 27 UFs
- [ ] GET /api/v1/localizacao/municipios/SP retorna 645 municípios
- [ ] Campo "UF de Naturalidade" aparece no formulário
- [ ] Select de UF está preenchido com 27 opções
- [ ] Ao selecionar UF, municipípios carregam dinamicamente
- [ ] Nenhum erro no console (F12)

---

## 🎯 Resultado Final

```
ANTES: Naturalidade era um campo de texto livre
DEPOIS: Naturalidade é um dropdown com ~5.500 municípios
        Todos validados e de fonte oficial (IBGE)
```

---

**Quando funcionar:** ✅ Tudo pronto para usar! 🚀
