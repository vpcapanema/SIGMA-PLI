# 🚀 Guia da Extensão Neo4j for VS Code - SIGMA PLI

## 📋 Configuração Inicial

### 1. **Conexão com Neo4j Aura**
```
Host: 3f74966e.databases.neo4j.io
Port: 7687
Username: 3f74966e
Password: 77N9B2nQd_maiqyGxD5aE9LadT396gwj7NaKSilpBzU
Database: 3f74966e
```

### 2. **Testando a Conexão**
```cypher
RETURN "Hello Neo4j Aura!" AS message, datetime() AS timestamp;
```

---

## 🛠️ Como Usar a Extensão

### **1. Painel Neo4j**
- **Localização**: Sidebar esquerda (ícone Neo4j)
- **Conexões**: Gerenciar múltiplas conexões
- **Explorer**: Navegar por labels e relacionamentos

### **2. Executar Queries**
- **Arquivo .cypher**: Criar arquivos com extensão `.cypher`
- **Command Palette**: `Ctrl+Shift+P` → "Neo4j: Run Query"
- **Shortcut**: `Ctrl+Enter` para executar query selecionada

### **3. Visualizar Resultados**
- **Tabela**: Resultados em formato tabular
- **Graph**: Visualização de grafo interativa
- **JSON**: Dados em formato JSON

---

## 🎯 Funcionalidades Principais

### **1. Autocompletar**
- Labels de nós (`:Pessoa`, `:Empresa`, etc.)
- Propriedades (`nome`, `cpf`, etc.)
- Funções Cypher (`MATCH`, `CREATE`, etc.)

### **2. Syntax Highlighting**
- Destaque de sintaxe Cypher
- Validação de queries
- Detecção de erros

### **3. Exploração do Schema**
- Visualizar labels existentes
- Explorar relacionamentos
- Estatísticas do banco

### **4. Resultados Interativos**
- Gráficos navegáveis
- Exportação de dados
- Filtros e ordenação

---

## 📊 Queries de Teste Rápido

### **Teste 1: Conectividade**
```cypher
RETURN "Conexão OK!" AS status;
```

### **Teste 2: Contar Dados**
```cypher
MATCH (n) RETURN count(n) AS total_nodes;
```

### **Teste 3: Visualizar Schema**
```cypher
CALL db.schema.visualization();
```

---

## 🔥 Workflows Recomendados

### **1. Desenvolvimento de Queries**
1. Criar arquivo `.cypher`
2. Escrever query com autocompletar
3. Executar com `Ctrl+Enter`
4. Visualizar resultados
5. Refinar e salvar

### **2. Exploração de Dados**
1. Usar painel Explorer
2. Navegar por labels
3. Criar queries baseadas na estrutura
4. Visualizar relacionamentos

### **3. Debug e Análise**
1. Executar queries de diagnóstico
2. Analisar performance
3. Usar `EXPLAIN` e `PROFILE`
4. Otimizar queries

---

## 🎨 Visualizações Úteis

### **1. Rede Completa (Limitada)**
```cypher
MATCH (n)-[r]-(m) 
RETURN n, r, m 
LIMIT 25;
```

### **2. Pessoas e Empresas**
```cypher
MATCH (p:Pessoa)-[r]-(e:Empresa) 
RETURN p, r, e;
```

### **3. Projetos e Participantes**
```cypher
MATCH (proj:Projeto)-[r]-(entity) 
RETURN proj, r, entity;
```

---

## ⚡ Shortcuts Úteis

| Ação | Shortcut |
|------|----------|
| Executar Query | `Ctrl+Enter` |
| Command Palette | `Ctrl+Shift+P` |
| Novo arquivo .cypher | `Ctrl+N` |
| Salvar | `Ctrl+S` |
| Buscar | `Ctrl+F` |
| Comentar linha | `Ctrl+/` |

---

## 🔧 Configurações Recomendadas

### **1. Settings.json**
```json
{
  "neo4j.connect": true,
  "neo4j.autoComplete": true,
  "neo4j.linting": true,
  "files.associations": {
    "*.cypher": "cypher"
  }
}
```

### **2. Tema para Cypher**
- Instalar tema que suporte Cypher
- Ajustar cores para melhor legibilidade

---

## 📚 Comandos da Extensão

### **Via Command Palette (`Ctrl+Shift+P`)**
- `Neo4j: Connect` - Conectar ao banco
- `Neo4j: Disconnect` - Desconectar
- `Neo4j: Run Query` - Executar query
- `Neo4j: Run Query (Selection)` - Executar seleção
- `Neo4j: Show Schema` - Mostrar schema
- `Neo4j: Refresh` - Atualizar conexão

---

## 🎯 Dicas Pro

### **1. Organização de Queries**
```
/queries
  ├── setup/
  │   ├── create_data.cypher
  │   └── constraints.cypher
  ├── analysis/
  │   ├── pessoas_empresas.cypher
  │   └── projetos.cypher
  └── maintenance/
      ├── cleanup.cypher
      └── stats.cypher
```

### **2. Uso de Parâmetros**
```cypher
// Query com parâmetros
MATCH (p:Pessoa {nome: $nome})
RETURN p;

// Definir parâmetros no painel
{"nome": "João Silva"}
```

### **3. Performance**
```cypher
// Use EXPLAIN para ver plano de execução
EXPLAIN MATCH (p:Pessoa)-[:TRABALHA_EM]-(e:Empresa) 
RETURN p.nome, e.nome;

// Use PROFILE para métricas detalhadas  
PROFILE MATCH (p:Pessoa)-[:TRABALHA_EM]-(e:Empresa) 
RETURN p.nome, e.nome;
```

---

## 🚨 Troubleshooting

### **Problema: Conexão não funciona**
- Verificar credenciais
- Testar conectividade de rede
- Verificar status da instância Aura

### **Problema: Queries lentas**
- Usar `PROFILE` para análise
- Criar índices apropriados
- Limitar resultados com `LIMIT`

### **Problema: Autocompletar não funciona**
- Verificar conexão ativa
- Recarregar window (`Ctrl+Shift+P` → "Reload Window")
- Verificar configurações da extensão

---

## 🎉 Próximos Passos

1. **Teste as queries do arquivo `queries_neo4j_extension.cypher`**
2. **Explore o painel de schema da extensão**
3. **Crie suas próprias queries personalizadas**
4. **Use visualizações para entender os dados**
5. **Experimente com parâmetros e filtros**

---

## 📞 Recursos de Ajuda

- **Documentação Neo4j**: https://neo4j.com/docs/
- **Cypher Manual**: https://neo4j.com/docs/cypher-manual/
- **Extensão GitHub**: https://github.com/neo4j/neo4j-vscode
- **Community Forum**: https://community.neo4j.com/