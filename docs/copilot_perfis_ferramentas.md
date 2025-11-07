# Perfis de Ferramentas do Copilot (MCP)

Este documento define três perfis práticos de ferramentas para o projeto SIGMA‑PLI. Use como checklist no painel Copilot → Tools (Ferramentas) ou copie o JSONC do template para o arquivo do usuário.

Observação: os nomes/IDs exatos das ferramentas no Copilot podem variar. Use como referência e selecione as equivalentes que você tem instaladas.

## Perfil 1 — SIGMA‑Core (uso diário)
- Filesystem / Path utils
- PowerShell (Shell)
- Git
- HTTP / Fetch (ou cURL)
- JSON / YAML
- CSV / XLSX
- Regex / Text utils
- PostgreSQL (psql/driver)
- Neo4j (bolt/driver)
- Docker / Docker Compose
- Compressão (zip/tar)
- Hash (SHA256)

Meta: até ~20–35 ferramentas. Deixe apenas o essencial sempre ativo.

## Perfil 2 — SIGMA‑Dados (ETL, integrações)
Inclui tudo do SIGMA‑Core + adicionais:
- Client OpenAPI / API Explorer
- Armazenamento de Objetos (S3/Blob; habilite somente se usar)
- Agendador simples (jobs)
- Conversores (parquet/geojson, se disponível)
- Ferramentas de importação/exportação em lote

Meta: ~35–60 ferramentas. Ative apenas quando for trabalhar com ETL/import.

## Perfil 3 — SIGMA‑DevOps (colaboração e release)
Pode ser combinado com Core ou habilitado temporariamente:
- GitHub Issues / Pull Requests / Actions (Workflows)
- GitHub Releases / Notifications
- Uma nuvem (somente a que você usa: OCI ou Azure; evite múltiplas)
- Auditoria/Qualidade (linters de API, segurança; habilite apenas quando necessário)

Meta: manter abaixo de ~90 somando com os demais. Alvos acima de 100 aumentam latência.

## Evite/Desligue quando não usar
- Ferramentas de clouds que você não usa
- Duplicatas (duas de HTTP, dois clients de Git)
- Web scraping pesado
- Vetores/ML (se não forem parte do fluxo)

## Template JSONC (copiar/ajustar)
Veja `docs/copilot_toolsets_perfis.jsonc`. Copie o conteúdo para o arquivo do usuário do VS Code Insiders:

Caminho: `C:\\Users\\<SEU_USUARIO>\\AppData\\Roaming\\Code - Insiders\\User\\prompts\\t1.toolsets.jsonc`

Dica: faça backup antes de sobrescrever.

## Como aplicar pelo VS Code
1. Abrir Copilot → Tools e habilitar somente as ferramentas do perfil atual.
2. Alternar perfis do VS Code: Engrenagem → Perfis → Criar perfis “SIGMA‑Core”, “SIGMA‑Dados”, “SIGMA‑DevOps”.
3. Em cada perfil, ajuste o conjunto de ferramentas conforme as listas acima.
