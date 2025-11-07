// =============================================================================
// QUERIES NEO4J AURA - SIGMA PLI - Para usar na extensão VS Code
// =============================================================================

// 1. CONECTIVIDADE - Teste básico
// Execute esta query primeiro para testar a conexão
RETURN "Hello Neo4j Aura!" AS message, datetime() AS timestamp;

// =============================================================================
// 2. LIMPEZA E PREPARAÇÃO
// =============================================================================

// Limpar todos os dados (CUIDADO: Remove tudo!)
MATCH (n) 
DETACH DELETE n;

// Verificar se banco está vazio
MATCH (n) 
RETURN count(n) AS total_nodes;

// =============================================================================
// 3. CRIAÇÃO DE DADOS - SIGMA PLI
// =============================================================================

// Criar estrutura básica do SIGMA PLI
CREATE 
  // Pessoas
  (joao:Pessoa {
    nome: "João Silva",
    cpf: "123.456.789-00",
    cargo: "Gerente de TI",
    email: "joao.silva@sigma.com",
    telefone: "(11) 99999-1111",
    dataAdmissao: date("2023-01-15")
  }),
  
  (maria:Pessoa {
    nome: "Maria Santos", 
    cpf: "987.654.321-00",
    cargo: "Analista de Sistemas",
    email: "maria.santos@sigma.com",
    telefone: "(11) 99999-2222",
    dataAdmissao: date("2023-03-10")
  }),
  
  (carlos:Pessoa {
    nome: "Carlos Oliveira",
    cpf: "456.789.123-00", 
    cargo: "Desenvolvedor Senior",
    email: "carlos.oliveira@sigma.com",
    telefone: "(11) 99999-3333",
    dataAdmissao: date("2022-11-20")
  }),
  
  // Empresas
  (sigma:Empresa {
    nome: "SIGMA Tecnologia Ltda",
    cnpj: "12.345.678/0001-90",
    setor: "Tecnologia da Informação",
    endereco: "Av. Paulista, 1000 - São Paulo/SP",
    telefone: "(11) 3333-4444",
    email: "contato@sigma.com",
    fundacao: date("2020-01-01")
  }),
  
  (cliente1:Empresa {
    nome: "Tech Solutions Corp",
    cnpj: "98.765.432/0001-10",
    setor: "Consultoria",
    endereco: "Rua das Flores, 500 - Rio de Janeiro/RJ",
    telefone: "(21) 2222-3333",
    email: "contato@techsolutions.com",
    fundacao: date("2018-05-15")
  }),
  
  // Documentos
  (contrato1:Documento {
    tipo: "Contrato de Trabalho",
    numero: "CONT-TRB-001",
    status: "Ativo",
    dataEmissao: date("2023-01-15"),
    dataVencimento: date("2024-01-15"),
    valor: 8500.00
  }),
  
  (contrato2:Documento {
    tipo: "Contrato de Prestação de Serviços",
    numero: "CONT-PS-001", 
    status: "Ativo",
    dataEmissao: date("2024-01-10"),
    dataVencimento: date("2024-12-31"),
    valor: 150000.00
  }),
  
  (relatorio1:Documento {
    tipo: "Relatório Mensal",
    numero: "REL-001-2024",
    status: "Finalizado",
    dataEmissao: date("2024-02-01"),
    responsavel: "Maria Santos"
  }),
  
  (projeto1:Projeto {
    nome: "Sistema de Gestão Integrada",
    codigo: "PROJ-SGI-001",
    status: "Em Andamento",
    dataInicio: date("2024-01-15"),
    dataPrevisaoFim: date("2024-12-15"),
    orcamento: 200000.00,
    descricao: "Desenvolvimento de sistema de gestão para cliente"
  }),
  
  // Relacionamentos
  (joao)-[:TRABALHA_EM {desde: date("2023-01-15"), salario: 12000.00}]->(sigma),
  (maria)-[:TRABALHA_EM {desde: date("2023-03-10"), salario: 8500.00}]->(sigma),
  (carlos)-[:TRABALHA_EM {desde: date("2022-11-20"), salario: 10000.00}]->(sigma),
  
  (joao)-[:ASSINOU {data: date("2023-01-15"), cargo: "Gerente"}]->(contrato1),
  (maria)-[:ASSINOU {data: date("2023-03-10"), cargo: "Analista"}]->(contrato1),
  
  (sigma)-[:POSSUI]->(contrato1),
  (sigma)-[:POSSUI]->(contrato2),
  (sigma)-[:POSSUI]->(relatorio1),
  
  (sigma)-[:CLIENTE_DE]->(cliente1),
  (sigma)-[:PRESTOU_SERVICO {dataInicio: date("2024-01-10")}]->(cliente1),
  
  (maria)-[:CRIOU {data: date("2024-02-01")}]->(relatorio1),
  (joao)-[:SUPERVISIONOU]->(relatorio1),
  
  (joao)-[:GERENCIA]->(projeto1),
  (maria)-[:PARTICIPA_DE {papel: "Analista de Requisitos"}]->(projeto1),
  (carlos)-[:PARTICIPA_DE {papel: "Desenvolvedor Lead"}]->(projeto1),
  
  (projeto1)-[:RELACIONADO_A]->(contrato2),
  (projeto1)-[:PARA_CLIENTE]->(cliente1);

// =============================================================================
// 4. VERIFICAÇÃO DOS DADOS CRIADOS
// =============================================================================

// Contar nós por tipo
MATCH (n)
RETURN labels(n) AS tipo, count(n) AS quantidade
ORDER BY quantidade DESC;

// Contar relacionamentos por tipo  
MATCH ()-[r]->()
RETURN type(r) AS tipo_relacionamento, count(r) AS quantidade
ORDER BY quantidade DESC;

// =============================================================================
// 5. CONSULTAS DE EXEMPLO - SIGMA PLI
// =============================================================================

// 5.1 - Listar todas as pessoas e suas empresas
MATCH (p:Pessoa)-[t:TRABALHA_EM]->(e:Empresa)
RETURN p.nome AS pessoa, 
       p.cargo AS cargo,
       e.nome AS empresa,
       t.desde AS data_admissao,
       t.salario AS salario
ORDER BY p.nome;

// 5.2 - Documentos por empresa
MATCH (e:Empresa)-[:POSSUI]->(d:Documento)
RETURN e.nome AS empresa,
       collect({
         tipo: d.tipo,
         numero: d.numero, 
         status: d.status,
         valor: d.valor
       }) AS documentos;

// 5.3 - Projetos e seus participantes
MATCH (proj:Projeto)<-[part:PARTICIPA_DE]-(p:Pessoa)
OPTIONAL MATCH (proj)<-[:GERENCIA]-(gerente:Pessoa)
RETURN proj.nome AS projeto,
       proj.status AS status,
       gerente.nome AS gerente,
       collect({
         nome: p.nome,
         papel: part.papel
       }) AS participantes;

// 5.4 - Rede de relacionamentos de uma pessoa específica
MATCH (p:Pessoa {nome: "João Silva"})-[r]-(conectado)
RETURN p.nome AS pessoa,
       type(r) AS tipo_relacao,
       labels(conectado) AS tipo_entidade,
       CASE 
         WHEN 'Pessoa' IN labels(conectado) THEN conectado.nome
         WHEN 'Empresa' IN labels(conectado) THEN conectado.nome
         WHEN 'Documento' IN labels(conectado) THEN conectado.tipo + ' - ' + conectado.numero
         WHEN 'Projeto' IN labels(conectado) THEN conectado.nome
         ELSE 'Outro'
       END AS nome_entidade
ORDER BY tipo_relacao;

// 5.5 - Análise de contratos ativos
MATCH (d:Documento)
WHERE d.tipo CONTAINS "Contrato" AND d.status = "Ativo"
RETURN d.numero AS contrato,
       d.tipo AS tipo,
       d.dataEmissao AS emissao,
       d.dataVencimento AS vencimento,
       d.valor AS valor,
       duration.between(date(), d.dataVencimento).days AS dias_para_vencer
ORDER BY dias_para_vencer;

// =============================================================================
// 6. CONSULTAS AVANÇADAS
// =============================================================================

// 6.1 - Encontrar caminhos entre pessoas e projetos
MATCH path = (p:Pessoa)-[*1..3]-(proj:Projeto)
WHERE p.nome = "Maria Santos"
RETURN path
LIMIT 5;

// 6.2 - Análise de conectividade - Quem trabalha em que
MATCH (p:Pessoa)-[:TRABALHA_EM]->(e:Empresa)-[:CLIENTE_DE]->(cliente:Empresa)
RETURN p.nome AS funcionario,
       e.nome AS empresa,
       cliente.nome AS cliente,
       "Funcionário -> Empresa -> Cliente" AS caminho;

// 6.3 - Documentos relacionados a projetos
MATCH (proj:Projeto)-[:RELACIONADO_A]->(doc:Documento)
OPTIONAL MATCH (doc)<-[:CRIOU]-(criador:Pessoa)
RETURN proj.nome AS projeto,
       doc.tipo AS documento,
       doc.numero AS numero,
       criador.nome AS criado_por;

// =============================================================================
// 7. ANÁLISES ESTATÍSTICAS
// =============================================================================

// 7.1 - Estatísticas gerais
MATCH (n)
WITH labels(n) AS tipos, count(n) AS total
UNWIND tipos AS tipo
RETURN tipo, sum(total) AS quantidade
ORDER BY quantidade DESC;

// 7.2 - Análise salarial por cargo
MATCH (p:Pessoa)-[t:TRABALHA_EM]->(e:Empresa)
WHERE t.salario IS NOT NULL
RETURN p.cargo AS cargo,
       count(p) AS quantidade_pessoas,
       avg(t.salario) AS salario_medio,
       min(t.salario) AS salario_minimo,
       max(t.salario) AS salario_maximo
ORDER BY salario_medio DESC;

// 7.3 - Projetos por status
MATCH (proj:Projeto)
RETURN proj.status AS status,
       count(proj) AS quantidade,
       collect(proj.nome) AS projetos
ORDER BY quantidade DESC;

// =============================================================================
// 8. VISUALIZAÇÕES RECOMENDADAS
// =============================================================================

// 8.1 - Visualização completa (limitada)
MATCH (n)-[r]-(m)
RETURN n, r, m
LIMIT 50;

// 8.2 - Visualização de pessoas e empresas apenas
MATCH (p:Pessoa)-[r]-(e:Empresa)
RETURN p, r, e;

// 8.3 - Visualização de projetos e participantes
MATCH (proj:Projeto)-[r]-(entity)
RETURN proj, r, entity;

// =============================================================================
// 9. COMANDOS ÚTEIS PARA MANUTENÇÃO
// =============================================================================

// Verificar schema do banco
CALL db.schema.visualization();

// Listar todos os labels
CALL db.labels();

// Listar todos os tipos de relacionamentos
CALL db.relationshipTypes();

// Verificar índices
CALL db.indexes();

// Estatísticas do banco
CALL db.stats.retrieve('GRAPH COUNTS');

// =============================================================================
// 10. QUERIES DE EXEMPLO PARA TESTE NA EXTENSÃO
// =============================================================================

// Query simples para testar
MATCH (n) RETURN count(n) AS total_nos;

// Query com parâmetros (teste na extensão)
MATCH (p:Pessoa {nome: $nome})
RETURN p.nome, p.cargo, p.email;
// Use: {"nome": "João Silva"}

// Query com múltiplos parâmetros
MATCH (p:Pessoa)-[t:TRABALHA_EM]->(e:Empresa)
WHERE t.salario >= $salario_minimo AND p.cargo = $cargo
RETURN p.nome, p.cargo, t.salario, e.nome;
// Use: {"salario_minimo": 10000, "cargo": "Gerente de TI"}