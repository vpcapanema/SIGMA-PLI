# Relatório: Análise de Campos das Páginas vs Colunas do Banco

**Data:** 03/11/2025  
**Objetivo:** Verificar se os campos das páginas de cadastro mapeiam corretamente para as colunas das tabelas do PostgreSQL

---

## 🔍 Descoberta Crítica

⚠️ **PROBLEMA ARQUITETURAL IDENTIFICADO:**

O banco possui **DUAS tabelas de pessoa**:

1. `cadastro.pessoa` (10 colunas) - Tabela correta segundo a arquitetura
2. `usuarios.pessoa` (17 colunas) - Tabela que existe no banco mas **NÃO deveria ser usada para cadastro público**

**Consequência:** A implementação atual está usando `usuarios.pessoa` ao invés de `cadastro.pessoa`!

---

## 📊 TABELA 1: cadastro.pessoa (CORRETO)

### Colunas no Banco (10 colunas):

| #   | Coluna            | Tipo      | Obrigatório | Default            | Observação                    |
| --- | ----------------- | --------- | ----------- | ------------------ | ----------------------------- |
| 1   | `id`              | UUID      | NOT NULL    | uuid_generate_v4() | PK                            |
| 2   | `nome_completo`   | TEXT      | NOT NULL    | -                  | ✓                             |
| 3   | `cpf`             | TEXT      | NULL        | -                  | ✓                             |
| 4   | `email`           | TEXT      | NULL        | -                  | ✓                             |
| 5   | `telefone`        | TEXT      | NULL        | -                  | ✓                             |
| 6   | `cargo`           | TEXT      | NULL        | -                  | ✓                             |
| 7   | `instituicao_id`  | UUID      | NULL        | -                  | FK para cadastro.instituicao  |
| 8   | `departamento_id` | UUID      | NULL        | -                  | FK para cadastro.departamento |
| 9   | `ativa`           | BOOLEAN   | NULL        | TRUE               | -                             |
| 10  | `created_at`      | TIMESTAMP | NULL        | CURRENT_TIMESTAMP  | -                             |

### Campos na Página HTML (Pessoa Física):

**PROBLEMA:** A página tem **36+ campos**, mas a tabela `cadastro.pessoa` tem apenas **10 colunas**!

#### Campos Mapeados (presentes na tabela):

1. ✅ `nome_completo` → cadastro.pessoa.nome_completo
2. ✅ `cpf` → cadastro.pessoa.cpf
3. ✅ `email` → cadastro.pessoa.email
4. ✅ `telefone_principal` → cadastro.pessoa.telefone
5. ✅ `cargo` → cadastro.pessoa.cargo (falta criar campo no HTML!)
6. ✅ `instituicao_id` → cadastro.pessoa.instituicao_id (falta criar campo no HTML!)
7. ✅ `departamento_id` → cadastro.pessoa.departamento_id (falta criar campo no HTML!)

#### Campos SEM Coluna Correspondente (página tem, banco não):

1. ❌ `nome_social` - **SEM COLUNA**
2. ❌ `data_nascimento` - **SEM COLUNA**
3. ❌ `sexo` - **SEM COLUNA**
4. ❌ `nacionalidade` - **SEM COLUNA**
5. ❌ `naturalidade` - **SEM COLUNA**
6. ❌ `nome_pai` - **SEM COLUNA**
7. ❌ `nome_mae` - **SEM COLUNA**
8. ❌ `rg` - **SEM COLUNA**
9. ❌ `orgao_expeditor` - **SEM COLUNA**
10. ❌ `uf_rg` - **SEM COLUNA**
11. ❌ `data_expedicao_rg` - **SEM COLUNA**
12. ❌ `titulo_eleitor` - **SEM COLUNA**
13. ❌ `zona_eleitoral` - **SEM COLUNA**
14. ❌ `secao_eleitoral` - **SEM COLUNA**
15. ❌ `pis_pasep` - **SEM COLUNA**
16. ❌ `email_secundario` - **SEM COLUNA**
17. ❌ `telefone_secundario` - **SEM COLUNA**
18. ❌ `cep` - **SEM COLUNA**
19. ❌ `logradouro` - **SEM COLUNA**
20. ❌ `numero` - **SEM COLUNA**
21. ❌ `complemento` - **SEM COLUNA**
22. ❌ `bairro` - **SEM COLUNA**
23. ❌ `cidade` - **SEM COLUNA**
24. ❌ `uf` - **SEM COLUNA**

**Total:** 24 campos extras na página que **NÃO TÊM COLUNAS** em `cadastro.pessoa`!

---

## 📊 TABELA 2: usuarios.pessoa (EXISTE MAS NÃO DEVERIA SER USADA)

### Colunas no Banco (17 colunas):

| #   | Coluna            | Tipo      | Obrigatório | Default            |
| --- | ----------------- | --------- | ----------- | ------------------ |
| 1   | `id`              | UUID      | NOT NULL    | uuid_generate_v4() |
| 2   | `nome_completo`   | TEXT      | NOT NULL    | -                  |
| 3   | `primeiro_nome`   | TEXT      | NULL        | -                  |
| 4   | `ultimo_nome`     | TEXT      | NULL        | -                  |
| 5   | `email`           | TEXT      | NULL        | -                  |
| 6   | `telefone`        | TEXT      | NULL        | -                  |
| 7   | `cpf`             | TEXT      | NULL        | -                  |
| 8   | `data_nascimento` | DATE      | NULL        | -                  |
| 9   | `genero`          | TEXT      | NULL        | -                  |
| 10  | `foto_url`        | TEXT      | NULL        | -                  |
| 11  | `instituicao_id`  | UUID      | NULL        | -                  |
| 12  | `departamento_id` | UUID      | NULL        | -                  |
| 13  | `cargo`           | TEXT      | NULL        | -                  |
| 14  | `matricula`       | TEXT      | NULL        | -                  |
| 15  | `ativo`           | BOOLEAN   | NULL        | TRUE               |
| 16  | `criado_em`       | TIMESTAMP | NULL        | CURRENT_TIMESTAMP  |
| 17  | `atualizado_em`   | TIMESTAMP | NULL        | CURRENT_TIMESTAMP  |

**Observação:** Esta tabela tem mais colunas (data_nascimento, genero, etc.) mas **NÃO deveria ser usada para cadastro público**. É uma tabela do schema `usuarios` que provavelmente serve para outra finalidade.

---

## 📊 TABELA 3: cadastro.instituicao

### Colunas no Banco (11 colunas):

| #   | Coluna       | Tipo      | Obrigatório | Default            | Observação                                  |
| --- | ------------ | --------- | ----------- | ------------------ | ------------------------------------------- |
| 1   | `id`         | UUID      | NOT NULL    | uuid_generate_v4() | PK                                          |
| 2   | `nome`       | TEXT      | NOT NULL    | -                  | ✓                                           |
| 3   | `sigla`      | TEXT      | NULL        | -                  | ✓                                           |
| 4   | `cnpj`       | TEXT      | NULL        | -                  | ✓                                           |
| 5   | `tipo`       | TEXT      | NULL        | -                  | Valores: federal/estadual/municipal/privada |
| 6   | `endereco`   | TEXT      | NULL        | -                  | **CAMPO ÚNICO** para endereço completo      |
| 7   | `telefone`   | TEXT      | NULL        | -                  | ✓                                           |
| 8   | `email`      | TEXT      | NULL        | -                  | ✓                                           |
| 9   | `site`       | TEXT      | NULL        | -                  | ✓                                           |
| 10  | `ativa`      | BOOLEAN   | NULL        | TRUE               | -                                           |
| 11  | `created_at` | TIMESTAMP | NULL        | CURRENT_TIMESTAMP  | -                                           |

### Campos na Página HTML (Instituição):

**Precisa verificar:** A página de instituição pode ter campos de endereço separados (CEP, logradouro, número, etc.) mas a tabela tem apenas **um campo `endereco` TEXT**.

---

## 📊 TABELA 4: usuarios.conta_usuario

### Colunas no Banco (17 colunas):

| #   | Coluna                    | Tipo      | Obrigatório | Default            | Observação                                      |
| --- | ------------------------- | --------- | ----------- | ------------------ | ----------------------------------------------- |
| 1   | `id`                      | UUID      | NOT NULL    | uuid_generate_v4() | PK                                              |
| 2   | `pessoa_id`               | UUID      | NULL        | -                  | **FK → usuarios.pessoa** (não cadastro.pessoa!) |
| 3   | `username`                | TEXT      | NOT NULL    | -                  | ✓                                               |
| 4   | `email`                   | TEXT      | NOT NULL    | -                  | ✓                                               |
| 5   | `password_hash`           | TEXT      | NOT NULL    | -                  | ✓                                               |
| 6   | `salt`                    | TEXT      | NULL        | -                  | Para hashing                                    |
| 7   | `email_verificado`        | BOOLEAN   | NULL        | FALSE              | -                                               |
| 8   | `telefone_verificado`     | BOOLEAN   | NULL        | FALSE              | -                                               |
| 9   | `dois_fatores_habilitado` | BOOLEAN   | NULL        | FALSE              | -                                               |
| 10  | `secreto_2fa`             | TEXT      | NULL        | -                  | -                                               |
| 11  | `ultimo_login`            | TIMESTAMP | NULL        | -                  | -                                               |
| 12  | `ultimo_ip`               | INET      | NULL        | -                  | -                                               |
| 13  | `tentativas_falha`        | INTEGER   | NULL        | 0                  | -                                               |
| 14  | `bloqueado_ate`           | TIMESTAMP | NULL        | -                  | -                                               |
| 15  | `ativo`                   | BOOLEAN   | NULL        | TRUE               | -                                               |
| 16  | `criado_em`               | TIMESTAMP | NULL        | CURRENT_TIMESTAMP  | -                                               |
| 17  | `atualizado_em`           | TIMESTAMP | NULL        | CURRENT_TIMESTAMP  | -                                               |

⚠️ **PROBLEMA CRÍTICO:**

- A FK `pessoa_id` aponta para `usuarios.pessoa`, **NÃO** para `cadastro.pessoa`!
- Isso significa que o sistema atual espera que pessoa seja cadastrada primeiro em `usuarios.pessoa`, depois vinculada em `conta_usuario`.

---

## 🔴 Problemas Identificados

### 1. Excesso de Campos na Página de Pessoa Física

A página de cadastro de pessoa física tem **24 campos extras** que não existem em `cadastro.pessoa`:

**Documentos:**

- nome_social, rg, orgao_expeditor, uf_rg, data_expedicao_rg
- titulo_eleitor, zona_eleitoral, secao_eleitoral, pis_pasep

**Dados Pessoais:**

- data_nascimento, sexo, nacionalidade, naturalidade
- nome_pai, nome_mae

**Contatos:**

- email_secundario, telefone_secundario

**Endereço (8 campos):**

- cep, logradouro, numero, complemento, bairro, cidade, uf, pais

### 2. Campos Faltantes na Página

A página **NÃO** tem campos para:

- `cargo` (existe na tabela cadastro.pessoa)
- `instituicao_id` (existe na tabela cadastro.pessoa)
- `departamento_id` (existe na tabela cadastro.pessoa)

### 3. Inconsistência Arquitetural

A implementação atual usa `usuarios.pessoa` (service_pessoa.py), mas deveria usar `cadastro.pessoa`.

### 4. FK Incorreta

`usuarios.conta_usuario.pessoa_id` aponta para `usuarios.pessoa`, não para `cadastro.pessoa`.

---

## ✅ Soluções Propostas

### Opção 1: Expandir cadastro.pessoa (Recomendado)

Adicionar colunas em `cadastro.pessoa` para acomodar todos os campos da página:

```sql
ALTER TABLE cadastro.pessoa ADD COLUMN nome_social TEXT;
ALTER TABLE cadastro.pessoa ADD COLUMN data_nascimento DATE;
ALTER TABLE cadastro.pessoa ADD COLUMN sexo TEXT;
ALTER TABLE cadastro.pessoa ADD COLUMN nacionalidade TEXT;
ALTER TABLE cadastro.pessoa ADD COLUMN naturalidade TEXT;
ALTER TABLE cadastro.pessoa ADD COLUMN nome_pai TEXT;
ALTER TABLE cadastro.pessoa ADD COLUMN nome_mae TEXT;
ALTER TABLE cadastro.pessoa ADD COLUMN rg TEXT;
ALTER TABLE cadastro.pessoa ADD COLUMN orgao_expeditor TEXT;
ALTER TABLE cadastro.pessoa ADD COLUMN uf_rg TEXT;
ALTER TABLE cadastro.pessoa ADD COLUMN data_expedicao_rg DATE;
ALTER TABLE cadastro.pessoa ADD COLUMN titulo_eleitor TEXT;
ALTER TABLE cadastro.pessoa ADD COLUMN zona_eleitoral TEXT;
ALTER TABLE cadastro.pessoa ADD COLUMN secao_eleitoral TEXT;
ALTER TABLE cadastro.pessoa ADD COLUMN pis_pasep TEXT;
ALTER TABLE cadastro.pessoa ADD COLUMN email_secundario TEXT;
ALTER TABLE cadastro.pessoa ADD COLUMN telefone_secundario TEXT;

-- Criar tabela de endereços (normalizado)
CREATE TABLE cadastro.endereco (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    pessoa_id UUID REFERENCES cadastro.pessoa(id),
    cep TEXT,
    logradouro TEXT,
    numero TEXT,
    complemento TEXT,
    bairro TEXT,
    cidade TEXT,
    uf TEXT,
    pais TEXT DEFAULT 'Brasil',
    tipo TEXT, -- 'residencial', 'comercial', etc.
    principal BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Opção 2: Remover Campos Extras da Página

Simplificar a página para ter apenas os 10 campos de `cadastro.pessoa`:

- nome_completo
- cpf
- email
- telefone
- cargo
- instituicao_id
- departamento_id

**Desvantagem:** Perda de dados importantes (documentos, filiação, endereço).

### Opção 3: Usar usuarios.pessoa (NÃO Recomendado)

Continuar usando `usuarios.pessoa` e ignorar `cadastro.pessoa`.

**Desvantagem:** Viola a arquitetura documentada e cria confusão entre schemas.

---

## 📋 Ações Necessárias (Recomendação: Opção 1)

### 1. Expandir Tabela cadastro.pessoa

- [ ] Executar DDL para adicionar colunas de documentos
- [ ] Executar DDL para adicionar colunas de dados pessoais
- [ ] Executar DDL para adicionar colunas de contatos secundários

### 2. Criar Tabela cadastro.endereco

- [ ] Executar DDL para criar tabela normalizada de endereços
- [ ] Permitir múltiplos endereços por pessoa

### 3. Adicionar Campos Faltantes na Página

- [ ] Adicionar campo `cargo` no formulário
- [ ] Adicionar campo `instituicao_id` (select box)
- [ ] Adicionar campo `departamento_id` (select box)

### 4. Refatorar Backend

- [ ] Criar `app/services/M02_cadastro/service_pessoa.py` usando `cadastro.pessoa`
- [ ] Criar `app/services/M02_cadastro/service_instituicao.py` usando `cadastro.instituicao`
- [ ] Criar `app/services/M02_cadastro/service_endereco.py`
- [ ] Criar `app/routers/M02_cadastro/router_cadastro_api.py`
- [ ] Atualizar JavaScript handlers para novos endpoints

### 5. Resolver Problema de FK

- [ ] Decidir: usuarios.conta_usuario.pessoa_id deve apontar para cadastro.pessoa ou usuarios.pessoa?
- [ ] Se cadastro.pessoa: alterar FK no banco
- [ ] Se usuarios.pessoa: criar trigger para replicar cadastro.pessoa → usuarios.pessoa

### 6. Testar Fluxo Completo

- [ ] Cadastro PF → inserir em cadastro.pessoa + cadastro.endereco
- [ ] Cadastro Instituição → inserir em cadastro.instituicao
- [ ] Cadastro Usuário → inserir em usuarios.conta_usuario (resolver FK)

---

## 📊 Resumo Estatístico

| Item                                | Quantidade          |
| ----------------------------------- | ------------------- |
| **Pessoa Física**                   |                     |
| Colunas em cadastro.pessoa          | 10                  |
| Campos na página                    | 36+                 |
| Campos extras (sem coluna)          | 24                  |
| Campos faltantes (coluna sem campo) | 3                   |
| **Instituição**                     |                     |
| Colunas em cadastro.instituicao     | 11                  |
| Campos na página                    | (precisa verificar) |
| **Usuário**                         |                     |
| Colunas em usuarios.conta_usuario   | 17                  |
| Campos na página                    | (precisa verificar) |

---

## 🎯 Próximo Passo

**Decisão necessária:** Escolher entre Opção 1 (expandir tabela) ou Opção 2 (simplificar página).

**Recomendação:** Opção 1 - Expandir `cadastro.pessoa` e criar `cadastro.endereco`, pois os campos extras são importantes para o domínio de PLI (dados de filiação, documentos, endereços são relevantes).
