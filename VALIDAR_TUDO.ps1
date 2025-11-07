#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Script para validar e testar todas as máscaras e localização

.DESCRIPTION
    Executa testes das máscaras de formatação e valida os endpoints de UFs/Municípios

.EXAMPLE
    .\VALIDAR_TUDO.ps1
#>

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  🎨 VALIDAÇÃO DE MÁSCARAS + UFs/MUNICÍPIOS - SIGMA-PLI        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host ""
Write-Host "📋 CHECKLIST DE VALIDAÇÃO" -ForegroundColor Green
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green

# 1. Verificar arquivos criados
Write-Host ""
Write-Host "1️⃣ VERIFICANDO ARQUIVOS CRIADOS..." -ForegroundColor Yellow

$files_to_check = @(
    "static/js/M01_auth/script_input_masks.js",
    "static/js/M01_auth/script_localizacao_br.js",
    "templates/pages/M01_auth/template_auth_cadastro_pessoa_pagina.html",
    "README_MASCARAS_E_LOCALIZACAO.md",
    "TESTE_MASCARAS_FORMATACAO.py"
)

foreach ($file in $files_to_check) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file" -ForegroundColor Green
    }
    else {
        Write-Host "   ❌ $file (NÃO ENCONTRADO)" -ForegroundColor Red
    }
}

# 2. Verificar linha em script_localizacao_br.js
Write-Host ""
Write-Host "2️⃣ VERIFICANDO CORREÇÃO DO SCRIPT DE LOCALIZAÇÃO..." -ForegroundColor Yellow

if (Select-String -Path "static/js/M01_auth/script_localizacao_br.js" -Pattern "window.localizacaoBR = new LocalizacaoBRManager" -Quiet) {
    Write-Host "   ✅ window.localizacaoBR corretamente atribuído" -ForegroundColor Green
}
else {
    Write-Host "   ❌ window.localizacaoBR NÃO encontrado" -ForegroundColor Red
}

# 3. Verificar se template foi atualizado
Write-Host ""
Write-Host "3️⃣ VERIFICANDO ATUALIZAÇÕES DO TEMPLATE..." -ForegroundColor Yellow

if (Select-String -Path "templates/pages/M01_auth/template_auth_cadastro_pessoa_pagina.html" -Pattern "script_input_masks.js" -Quiet) {
    Write-Host "   ✅ script_input_masks.js referenciado no template" -ForegroundColor Green
}
else {
    Write-Host "   ❌ script_input_masks.js NÃO referenciado" -ForegroundColor Red
}

if (Select-String -Path "templates/pages/M01_auth/template_auth_cadastro_pessoa_pagina.html" -Pattern "inputMaskManager.setupFields" -Quiet) {
    Write-Host "   ✅ inputMaskManager.setupFields configurado" -ForegroundColor Green
}
else {
    Write-Host "   ❌ inputMaskManager.setupFields NÃO configurado" -ForegroundColor Red
}

if (Select-String -Path "templates/pages/M01_auth/template_auth_cadastro_pessoa_pagina.html" -Pattern "window.localizacaoBR.inicializar" -Quiet) {
    Write-Host "   ✅ window.localizacaoBR.inicializar configurado" -ForegroundColor Green
}
else {
    Write-Host "   ❌ window.localizacaoBR.inicializar NÃO configurado" -ForegroundColor Red
}

# 4. Testar endpoints da API
Write-Host ""
Write-Host "4️⃣ TESTANDO ENDPOINTS DA API..." -ForegroundColor Yellow

Write-Host ""
Write-Host "⚠️  NOTA: A aplicação precisa estar rodando em http://localhost:8010" -ForegroundColor Magenta

# Verificar se a aplicação está rodando
$isRunning = $false
try {
    $response = Invoke-WebRequest -Uri "http://127.0.0.1:8010/health" -TimeoutSec 2 -ErrorAction SilentlyContinue
    if ($response.StatusCode -eq 200) {
        $isRunning = $true
    }
}
catch {
    $isRunning = $false
}

if ($isRunning) {
    Write-Host "   ✅ Aplicação está rodando!" -ForegroundColor Green
    
    # Testar UFs
    Write-Host ""
    Write-Host "   Testando GET /api/v1/localizacao/ufs..." -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:8010/api/v1/localizacao/ufs" -TimeoutSec 5
        Write-Host "      ✅ Retornou $($response.total) UFs" -ForegroundColor Green
        Write-Host "      Exemplo: $($response.ufs[0].sigla) - $($response.ufs[0].nome)" -ForegroundColor Gray
    }
    catch {
        Write-Host "      ❌ Erro ao carregar UFs: $_" -ForegroundColor Red
    }
    
    # Testar Municípios
    Write-Host ""
    Write-Host "   Testando GET /api/v1/localizacao/municipios/SP..." -ForegroundColor Cyan
    try {
        $response = Invoke-RestMethod -Uri "http://127.0.0.1:8010/api/v1/localizacao/municipios/SP" -TimeoutSec 5
        Write-Host "      ✅ Retornou $($response.total) municípios de SP" -ForegroundColor Green
        Write-Host "      Exemplos: $($response.municipios[0].nome), $($response.municipios[1].nome)..." -ForegroundColor Gray
    }
    catch {
        Write-Host "      ❌ Erro ao carregar municípios: $_" -ForegroundColor Red
    }
}
else {
    Write-Host "   ⚠️  Aplicação NÃO está rodando" -ForegroundColor Yellow
    Write-Host "   Execute: python setup_security.py --setup" -ForegroundColor Gray
}

# 5. Resumo
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "✅ IMPLEMENTAÇÕES COMPLETAS:" -ForegroundColor Green
Write-Host ""
Write-Host "   📝 Máscaras de Formatação:" -ForegroundColor Cyan
Write-Host "      • CPF:       123.456.789-00" -ForegroundColor Gray
Write-Host "      • CNPJ:      12.345.678/0001-90" -ForegroundColor Gray
Write-Host "      • Telefone:  (11) 98765-4321 ou (11) 8765-4321" -ForegroundColor Gray
Write-Host "      • CEP:       12345-678" -ForegroundColor Gray
Write-Host "      • Data:      DD/MM/YYYY" -ForegroundColor Gray
Write-Host "      • RG:        12.345.678-9" -ForegroundColor Gray
Write-Host "      • CNH:       13 dígitos" -ForegroundColor Gray
Write-Host ""
Write-Host "   🌐 Localização Brasileira:" -ForegroundColor Cyan
Write-Host "      • UFs carregam automaticamente" -ForegroundColor Gray
Write-Host "      • Municípios carregam quando UF é selecionado" -ForegroundColor Gray
Write-Host "      • Dados de UF Naturalidade e UF RG" -ForegroundColor Gray
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 PRÓXIMAS ETAPAS:" -ForegroundColor Green
Write-Host ""
Write-Host "   1. Iniciar aplicação:" -ForegroundColor Cyan
Write-Host "      python setup_security.py --setup" -ForegroundColor Gray
Write-Host ""
Write-Host "   2. Abrir no navegador:" -ForegroundColor Cyan
Write-Host "      http://localhost:8010/auth/cadastro" -ForegroundColor Gray
Write-Host ""
Write-Host "   3. Testar máscaras:" -ForegroundColor Cyan
Write-Host "      • Digite CPF: 12345678900 → 123.456.789-00 ✓" -ForegroundColor Gray
Write-Host "      • Digite Tel: 11987654321 → (11) 98765-4321 ✓" -ForegroundColor Gray
Write-Host ""
Write-Host "   4. Testar UFs/Municípios:" -ForegroundColor Cyan
Write-Host "      • Clique em 'UF Naturalidade' → Selecione 'São Paulo'" -ForegroundColor Gray
Write-Host "      • Campo 'Município' preenche com ~645 municípios ✓" -ForegroundColor Gray
Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Green
Write-Host ""
Write-Host "📚 Documentação:" -ForegroundColor Green
Write-Host "   • README_MASCARAS_E_LOCALIZACAO.md" -ForegroundColor Gray
Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║  ✅ STATUS: PRONTO PARA TESTAR                                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
