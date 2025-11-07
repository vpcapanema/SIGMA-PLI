# SIGMA-PLI - GUIA COMPLETO DE IMPLEMENTAÇÃO

## 📋 Visão Geral

Este guia documenta a implementação completa do **SIGMA-PLI** conforme especificação do documento teórico-conceitual. A implementação inclui DDL completo, sistema de auditoria avançado e migração de dados legados.

## 🗂️ Arquivos Criados

### 1. **ddl_sigma_pli_completo.sql**
- **Descrição**: DDL completo do sistema
- **Conteúdo**: 
  - 4 esquemas (dicionario, usuarios, cadastro, auditoria)
  - Tabelas estruturadas por perfil de arquivo
  - Índices otimizados para performance
  - Views para catálogo público
  - Dados iniciais obrigatórios

### 2. **triggers_auditoria_completos.sql**
- **Descrição**: Sistema avançado de auditoria
- **Conteúdo**:
  - Triggers automáticos para todas operações críticas
  - Log de downloads de arquivos
  - Detecção de atividade suspeita
  - Relatórios de auditoria
  - Limpeza automática de logs antigos

### 3. **migração_dados_csv_legado.sql**
- **Descrição**: Migração de dados existentes
- **Conteúdo**:
  - Funções para importar CSVs legados
  - Validação de dados antes da migração
  - Mapeamento automático para nova estrutura
  - Relatórios de status da migração

### 4. **implementacao_sigma_pli_completa.sql**
- **Descrição**: Script principal de execução
- **Conteúdo**:
  - Ordem correta de execução
  - Verificações de integridade
  - Criação de usuário administrativo
  - Configurações de segurança

## 🚀 Processo de Implementação

### Pré-requisitos
- PostgreSQL 12+ com extensões uuid-ossp e pg_trgm
- Usuário com privilégios administrativos
- Dados CSV legados (opcional)

### Passo 1: Execução Principal
```sql
psql -h localhost -U postgres -d sigma_pli -f implementacao_sigma_pli_completa.sql
```

### Passo 2: Migração de Dados (Opcional)
```sql
-- 1. Carregar CSV legado
COPY dicionario.temp_csv_import FROM 'caminho/dados_legados.csv' 
WITH (FORMAT CSV, HEADER TRUE);

-- 2. Validar dados
SELECT dicionario.validar_csv_legado();

-- 3. Executar migração
SELECT dicionario.migrar_dados_csv_legado();
```

### Passo 3: Configuração Inicial
```sql
-- Verificar status do sistema
SELECT * FROM public.sigma_pli_status();

-- Alterar senha do admin (OBRIGATÓRIO!)
UPDATE usuarios.usuario 
SET password_hash = 'NOVO_HASH_SENHA' 
WHERE username = 'admin';
```

## 📊 Estrutura de Dados

### Esquema `dicionario` (Principal)
- **perfil**: Categorias semânticas (tabular, geoespacial, etc.)
- **extensao**: Extensões de arquivo suportadas
- **produtor**: Responsáveis pelos arquivos
- **arquivo**: Tabela principal de metadados
- **estrutura__[perfil]**: Metadados técnicos por tipo
- **conteudo__[perfil]**: Metadados descritivos por tipo

### Esquema `usuarios` (Provisório)
- **usuario**: Dados de usuários
- **papel**: Papéis do sistema (admin, gestor, etc.)
- **permissao**: Permissões granulares
- **tarefa**: Tarefas pessoais
- **evento**: Calendário pessoal

### Esquema `cadastro` (Provisório)
- **instituicao**: Órgãos e entidades
- **pessoa**: Cadastro de pessoas
- **produto**: Produtos/projetos
- **entrega**: Entregas de produtos

### Esquema `auditoria`
- **log_operacao**: Log de todas operações
- **operacao_sensivel**: Operações críticas
- **download_arquivo**: Histórico de downloads
- **sessao_usuario**: Controle de sessões

## 🔍 Perfis de Arquivo Suportados

1. **documentos_texto**: PDF, DOC, DOCX, TXT
2. **midia**: JPG, PNG, MP4, MP3
3. **tabular**: CSV, XLS, XLSX
4. **geoespacial_vetor**: SHP, KML, GeoJSON
5. **geoespacial_raster**: GeoTIFF, IMG
6. **nuvem_pontos**: LAS, LAZ, PLY
7. **desenho_2d3d**: DWG, DXF, SKP
8. **database**: SQL, DB, MDB
9. **geodatabase**: GDB, SDE
10. **pacote**: ZIP, RAR, 7Z

## 🛡️ Sistema de Auditoria

### Funcionalidades
- **Log automático**: Todas operações INSERT/UPDATE/DELETE
- **Controle de sessão**: Rastreamento de login/logout
- **Downloads**: Log completo de acesso a arquivos
- **Detecção de anomalias**: Atividade suspeita automática
- **Relatórios**: Views prontas para análise

### Configuração de Contexto
```sql
-- Configurar usuário na sessão
SELECT auditoria.set_user_context(
    'uuid-do-usuario',
    '192.168.1.100',
    'Mozilla/5.0...'
);

-- Registrar download
SELECT auditoria.registrar_download('uuid-do-arquivo', 'api', true);
```

## 📈 Views de Catálogo

### `view_catalogo_base`
- Catálogo público de todos arquivos aprovados
- Inclui metadados básicos e informações do produtor

### `view_catalogo_tabular`
- Específica para dados tabulares
- Inclui número de linhas/colunas e metadados específicos

### `view_catalogo_geoespacial_vetor`
- Específica para dados geoespaciais
- Inclui informações de geometria e coordenadas

## 🔧 Manutenção

### Limpeza de Logs
```sql
-- Remover logs com mais de 1 ano
SELECT auditoria.limpar_logs_antigos(365);
```

### Monitoramento
```sql
-- Status geral do sistema
SELECT * FROM public.sigma_pli_status();

-- Atividade suspeita
SELECT * FROM auditoria.detectar_atividade_suspeita();

-- Downloads recentes
SELECT * FROM auditoria.view_downloads_arquivo;
```

## 🔐 Segurança

### Configurações Aplicadas
- Row Level Security preparado (comentado)
- Permissões granulares por esquema
- Auditoria completa de operações sensíveis
- Controle de acesso por papéis

### Usuário Padrão
- **Username**: admin
- **Senha**: admin123 (**ALTERE IMEDIATAMENTE!**)
- **Papel**: Administrador completo

## 📋 Checklist de Implementação

- [ ] PostgreSQL configurado com extensões
- [ ] Scripts executados sem erro
- [ ] Senha do admin alterada
- [ ] Dados de teste inseridos
- [ ] Sistema de auditoria funcionando
- [ ] Catálogo público acessível
- [ ] Migração de dados legados (se aplicável)
- [ ] Configuração da aplicação backend
- [ ] Testes de upload de arquivos
- [ ] Testes de download e auditoria

## 🆘 Troubleshooting

### Erro: Extensão não encontrada
```sql
-- Instalar extensões manualmente
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
```

### Erro: Permissão negada
```sql
-- Executar como superusuário
SET ROLE postgres;
```

### Migração CSV falha
```sql
-- Verificar formato do CSV
SELECT dicionario.validar_csv_legado();

-- Limpar dados temporários
SELECT dicionario.limpar_dados_temporarios();
```

## 📞 Próximos Passos

1. **Configurar aplicação backend**: Connection strings e autenticação
2. **Implementar upload**: Interface para envio de arquivos
3. **Configurar processamento**: Extração de metadados automática
4. **Testes de integração**: Validar funcionamento completo
5. **Deploy em produção**: Configurações de ambiente produtivo

---

**Documento gerado em**: {data_atual}  
**Versão**: SIGMA-PLI v1.2  
**Status**: Implementação completa conforme especificação