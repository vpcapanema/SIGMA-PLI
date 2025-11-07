# Script de Teste Completo - Autenticação End-to-End
# Testa todos os endpoints implementados

$BASE_URL = "http://127.0.0.1:8010"
$SUCCESS_COLOR = "Green"
$FAILURE_COLOR = "Red"
$INFO_COLOR = "Cyan"
$WARNING_COLOR = "Yellow"

Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor $INFO_COLOR
Write-Host "║     SIGMA-PLI - TESTE COMPLETO DE AUTENTICAÇÃO E2E            ║" -ForegroundColor $INFO_COLOR
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor $INFO_COLOR
Write-Host ""

# Gerar dados únicos para teste
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$testUsername = "user_e2e_$timestamp"
$testEmail = "e2e_$timestamp@test.com"
$testPassword = "Senha@Forte123"
$testPasswordNew = "NovaSenha@Forte456"

# Variáveis globais
$global:sessionToken = $null
$global:refreshToken = $null
$global:resetToken = $null
$global:verificationToken = $null
$global:testsPassed = 0
$global:testsFailed = 0

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Method,
        [string]$Url,
        [string]$Body = $null,
        [hashtable]$Headers = @{},
        [int]$ExpectedStatus = 200
    )
    
    Write-Host "🧪 $Name" -ForegroundColor $INFO_COLOR
    
    try {
        $requestParams = @{
            Uri     = $Url
            Method  = $Method
            Headers = $Headers
        }
        
        if ($Body) {
            $requestParams.Body = $Body
            $requestParams.ContentType = "application/json"
        }
        
        $response = Invoke-WebRequest @requestParams -ErrorAction Stop
        
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host "   ✅ Sucesso ($($response.StatusCode))" -ForegroundColor $SUCCESS_COLOR
            $global:testsPassed++
            return $response.Content | ConvertFrom-Json
        }
        else {
            Write-Host "   ❌ Status inesperado: $($response.StatusCode) (esperado: $ExpectedStatus)" -ForegroundColor $FAILURE_COLOR
            $global:testsFailed++
            return $null
        }
    }
    catch {
        $statusCode = $_.Exception.Response.StatusCode.value__
        
        if ($statusCode -eq $ExpectedStatus) {
            Write-Host "   ✅ Erro esperado ($statusCode)" -ForegroundColor $SUCCESS_COLOR
            $global:testsPassed++
            return $null
        }
        else {
            Write-Host "   ❌ Erro: $($_.Exception.Message)" -ForegroundColor $FAILURE_COLOR
            $global:testsFailed++
            return $null
        }
    }
    
    Write-Host ""
}

# ═══════════════════════════════════════════════════════════════
Write-Host "┌─────────────────────────────────────────────────────────────┐" -ForegroundColor $INFO_COLOR
Write-Host "│  FASE 1: REGISTRO DE USUÁRIO                               │" -ForegroundColor $INFO_COLOR
Write-Host "└─────────────────────────────────────────────────────────────┘" -ForegroundColor $INFO_COLOR
Write-Host ""

$registerBody = @{
    username = $testUsername
    email    = $testEmail
    password = $testPassword
} | ConvertTo-Json

$result = Test-Endpoint `
    -Name "POST /api/v1/auth/register" `
    -Method "POST" `
    -Url "$BASE_URL/api/v1/auth/register" `
    -Body $registerBody

if ($result -and $result.success) {
    Write-Host "   📝 Usuário criado: $testUsername" -ForegroundColor $INFO_COLOR
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════
Write-Host "┌─────────────────────────────────────────────────────────────┐" -ForegroundColor $INFO_COLOR
Write-Host "│  FASE 2: LOGIN                                              │" -ForegroundColor $INFO_COLOR
Write-Host "└─────────────────────────────────────────────────────────────┘" -ForegroundColor $INFO_COLOR
Write-Host ""

$loginBody = @{
    identifier = $testUsername
    password   = $testPassword
} | ConvertTo-Json

$result = Test-Endpoint `
    -Name "POST /api/v1/auth/login (credenciais corretas)" `
    -Method "POST" `
    -Url "$BASE_URL/api/v1/auth/login" `
    -Body $loginBody

if ($result -and $result.success) {
    $global:sessionToken = $result.session_token
    $global:refreshToken = $result.refresh_token
    Write-Host "   🔑 Token: $($global:sessionToken.Substring(0, 20))..." -ForegroundColor $INFO_COLOR
    Write-Host "   👤 Usuário: $($result.user.username)" -ForegroundColor $INFO_COLOR
}

Write-Host ""

# Login com senha errada
$wrongLoginBody = @{
    identifier = $testUsername
    password   = "SenhaErrada123"
} | ConvertTo-Json

Test-Endpoint `
    -Name "POST /api/v1/auth/login (senha errada)" `
    -Method "POST" `
    -Url "$BASE_URL/api/v1/auth/login" `
    -Body $wrongLoginBody `
    -ExpectedStatus 401

Write-Host ""

# ═══════════════════════════════════════════════════════════════
Write-Host "┌─────────────────────────────────────────────────────────────┐" -ForegroundColor $INFO_COLOR
Write-Host "│  FASE 3: VERIFICAÇÃO DE SESSÃO                             │" -ForegroundColor $INFO_COLOR
Write-Host "└─────────────────────────────────────────────────────────────┘" -ForegroundColor $INFO_COLOR
Write-Host ""

if ($global:sessionToken) {
    $result = Test-Endpoint `
        -Name "GET /api/v1/auth/me (com token válido)" `
        -Method "GET" `
        -Url "$BASE_URL/api/v1/auth/me" `
        -Headers @{ "Authorization" = "Bearer $global:sessionToken" }
    
    if ($result) {
        Write-Host "   👤 Email: $($result.email)" -ForegroundColor $INFO_COLOR
    }
}

Write-Host ""

# Sem token
Test-Endpoint `
    -Name "GET /api/v1/auth/me (sem token)" `
    -Method "GET" `
    -Url "$BASE_URL/api/v1/auth/me" `
    -ExpectedStatus 401

Write-Host ""

# ═══════════════════════════════════════════════════════════════
Write-Host "┌─────────────────────────────────────────────────────────────┐" -ForegroundColor $INFO_COLOR
Write-Host "│  FASE 4: REFRESH DE SESSÃO                                 │" -ForegroundColor $INFO_COLOR
Write-Host "└─────────────────────────────────────────────────────────────┘" -ForegroundColor $INFO_COLOR
Write-Host ""

if ($global:refreshToken) {
    $refreshBody = @{
        refresh_token = $global:refreshToken
    } | ConvertTo-Json
    
    $result = Test-Endpoint `
        -Name "POST /api/v1/auth/refresh" `
        -Method "POST" `
        -Url "$BASE_URL/api/v1/auth/refresh" `
        -Body $refreshBody
    
    if ($result -and $result.success) {
        Write-Host "   🔄 Sessão renovada" -ForegroundColor $INFO_COLOR
        $global:sessionToken = $result.session_token
        $global:refreshToken = $result.refresh_token
    }
}

Write-Host ""

# ═══════════════════════════════════════════════════════════════
Write-Host "┌─────────────────────────────────────────────────────────────┐" -ForegroundColor $INFO_COLOR
Write-Host "│  FASE 5: RECUPERAÇÃO DE SENHA                              │" -ForegroundColor $INFO_COLOR
Write-Host "└─────────────────────────────────────────────────────────────┘" -ForegroundColor $INFO_COLOR
Write-Host ""

$resetRequestBody = @{
    email = $testEmail
} | ConvertTo-Json

$result = Test-Endpoint `
    -Name "POST /api/v1/auth/request-password-reset" `
    -Method "POST" `
    -Url "$BASE_URL/api/v1/auth/request-password-reset" `
    -Body $resetRequestBody

if ($result -and $result.success) {
    Write-Host "   📧 Instruções enviadas para: $testEmail" -ForegroundColor $INFO_COLOR
    Write-Host "   ℹ️  Em produção, o token seria enviado por email" -ForegroundColor $WARNING_COLOR
}

Write-Host ""

# Simular token de reset (em produção viria do email)
# Aqui vamos testar com token inválido
$invalidResetBody = @{
    token        = "token_invalido_123"
    new_password = $testPasswordNew
} | ConvertTo-Json

Test-Endpoint `
    -Name "POST /api/v1/auth/reset-password (token inválido)" `
    -Method "POST" `
    -Url "$BASE_URL/api/v1/auth/reset-password" `
    -Body $invalidResetBody `
    -ExpectedStatus 400

Write-Host ""

# ═══════════════════════════════════════════════════════════════
Write-Host "┌─────────────────────────────────────────────────────────────┐" -ForegroundColor $INFO_COLOR
Write-Host "│  FASE 6: VERIFICAÇÃO DE EMAIL                              │" -ForegroundColor $INFO_COLOR
Write-Host "└─────────────────────────────────────────────────────────────┘" -ForegroundColor $INFO_COLOR
Write-Host ""

# Token inválido
Test-Endpoint `
    -Name "GET /api/v1/auth/verify-email (token inválido)" `
    -Method "GET" `
    -Url "$BASE_URL/api/v1/auth/verify-email?token=token_invalido_123" `
    -ExpectedStatus 400

Write-Host ""

# ═══════════════════════════════════════════════════════════════
Write-Host "┌─────────────────────────────────────────────────────────────┐" -ForegroundColor $INFO_COLOR
Write-Host "│  FASE 7: LOGOUT                                             │" -ForegroundColor $INFO_COLOR
Write-Host "└─────────────────────────────────────────────────────────────┘" -ForegroundColor $INFO_COLOR
Write-Host ""

if ($global:sessionToken) {
    $result = Test-Endpoint `
        -Name "POST /api/v1/auth/logout" `
        -Method "POST" `
        -Url "$BASE_URL/api/v1/auth/logout" `
        -Headers @{ "Authorization" = "Bearer $global:sessionToken" }
    
    if ($result -and $result.success) {
        Write-Host "   👋 Logout realizado" -ForegroundColor $INFO_COLOR
    }
}

Write-Host ""

# Verificar que sessão foi revogada
Test-Endpoint `
    -Name "GET /api/v1/auth/me (após logout)" `
    -Method "GET" `
    -Url "$BASE_URL/api/v1/auth/me" `
    -Headers @{ "Authorization" = "Bearer $global:sessionToken" } `
    -ExpectedStatus 401

Write-Host ""

# ═══════════════════════════════════════════════════════════════
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor $INFO_COLOR
Write-Host "║                     RESUMO DOS TESTES                          ║" -ForegroundColor $INFO_COLOR
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor $INFO_COLOR
Write-Host ""

$totalTests = $global:testsPassed + $global:testsFailed
$successRate = if ($totalTests -gt 0) { [math]::Round(($global:testsPassed / $totalTests) * 100, 2) } else { 0 }

Write-Host "Total de testes: $totalTests" -ForegroundColor $INFO_COLOR
Write-Host "✅ Passou: $global:testsPassed" -ForegroundColor $SUCCESS_COLOR
Write-Host "❌ Falhou: $global:testsFailed" -ForegroundColor $(if ($global:testsFailed -gt 0) { $FAILURE_COLOR } else { $SUCCESS_COLOR })
Write-Host "Taxa de sucesso: $successRate%" -ForegroundColor $(if ($successRate -ge 90) { $SUCCESS_COLOR } elseif ($successRate -ge 70) { $WARNING_COLOR } else { $FAILURE_COLOR })

Write-Host ""

if ($global:testsFailed -eq 0) {
    Write-Host "🎉 TODOS OS TESTES PASSARAM!" -ForegroundColor $SUCCESS_COLOR
}
else {
    Write-Host "⚠️  ALGUNS TESTES FALHARAM" -ForegroundColor $WARNING_COLOR
}

Write-Host ""
