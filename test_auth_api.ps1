# Script de teste para autenticação
# Testa registro, login, verificação de usuário, logout

$BASE_URL = "http://127.0.0.1:8010"
$SUCCESS_COLOR = "Green"
$FAILURE_COLOR = "Red"
$INFO_COLOR = "Cyan"

Write-Host "=== TESTE DE AUTENTICAÇÃO ===" -ForegroundColor $INFO_COLOR
Write-Host ""

# Dados de teste
$randomSuffix = Get-Random -Minimum 1000 -Maximum 9999
$testUsername = "user_test_$randomSuffix"
$testEmail = "test_$randomSuffix@example.com"
$testPassword = "Senha123@Forte"

# Variáveis globais
$global:sessionToken = $null
$global:refreshToken = $null

# ===== TESTE 1: REGISTRO DE USUÁRIO =====
Write-Host "1️⃣  Testando REGISTRO de usuário..." -ForegroundColor $INFO_COLOR

$registerBody = @{
    username = $testUsername
    email    = $testEmail
    password = $testPassword
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/auth/register" `
        -Method POST `
        -Headers @{"Content-Type" = "application/json" } `
        -Body $registerBody
    
    if ($response.success) {
        Write-Host "   ✅ Registro bem-sucedido: $($response.message)" -ForegroundColor $SUCCESS_COLOR
    }
    else {
        Write-Host "   ❌ Registro falhou: $($response.message)" -ForegroundColor $FAILURE_COLOR
    }
}
catch {
    Write-Host "   ❌ Erro no registro: $($_.Exception.Message)" -ForegroundColor $FAILURE_COLOR
}

Write-Host ""

# ===== TESTE 2: LOGIN COM CREDENCIAIS CORRETAS =====
Write-Host "2️⃣  Testando LOGIN com credenciais corretas..." -ForegroundColor $INFO_COLOR

$loginBody = @{
    identifier = $testUsername
    password   = $testPassword
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/auth/login" `
        -Method POST `
        -Headers @{"Content-Type" = "application/json" } `
        -Body $loginBody
    
    if ($response.success) {
        $global:sessionToken = $response.session_token
        $global:refreshToken = $response.refresh_token
        Write-Host "   ✅ Login bem-sucedido!" -ForegroundColor $SUCCESS_COLOR
        Write-Host "   👤 Usuário: $($response.user.username)" -ForegroundColor $INFO_COLOR
        Write-Host "   📧 Email: $($response.user.email)" -ForegroundColor $INFO_COLOR
        Write-Host "   🔑 Session token: $($global:sessionToken.Substring(0, 20))..." -ForegroundColor $INFO_COLOR
    }
    else {
        Write-Host "   ❌ Login falhou" -ForegroundColor $FAILURE_COLOR
    }
}
catch {
    Write-Host "   ❌ Erro no login: $($_.Exception.Message)" -ForegroundColor $FAILURE_COLOR
}

Write-Host ""

# ===== TESTE 3: OBTER DADOS DO USUÁRIO AUTENTICADO =====
if ($global:sessionToken) {
    Write-Host "3️⃣  Testando endpoint /me (usuário autenticado)..." -ForegroundColor $INFO_COLOR
    
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/auth/me" `
            -Method GET `
            -Headers @{"Authorization" = "Bearer $global:sessionToken" }
        
        Write-Host "   ✅ Dados obtidos com sucesso!" -ForegroundColor $SUCCESS_COLOR
        Write-Host "   👤 Username: $($response.username)" -ForegroundColor $INFO_COLOR
        Write-Host "   📧 Email: $($response.email)" -ForegroundColor $INFO_COLOR
    }
    catch {
        Write-Host "   ❌ Erro ao obter dados: $($_.Exception.Message)" -ForegroundColor $FAILURE_COLOR
    }
    
    Write-Host ""
}

# ===== TESTE 4: LOGIN COM SENHA ERRADA =====
Write-Host "4️⃣  Testando LOGIN com senha ERRADA..." -ForegroundColor $INFO_COLOR

$wrongLoginBody = @{
    identifier = $testUsername
    password   = "SenhaErrada123"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/auth/login" `
        -Method POST `
        -Headers @{"Content-Type" = "application/json" } `
        -Body $wrongLoginBody
    
    Write-Host "   ❌ Login deveria ter falhado mas passou!" -ForegroundColor $FAILURE_COLOR
}
catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "   ✅ Login bloqueado corretamente (401 Unauthorized)" -ForegroundColor $SUCCESS_COLOR
    }
    else {
        Write-Host "   ⚠️  Erro inesperado: $($_.Exception.Message)" -ForegroundColor "Yellow"
    }
}

Write-Host ""

# ===== TESTE 5: REFRESH DE SESSÃO =====
if ($global:refreshToken) {
    Write-Host "5️⃣  Testando REFRESH de sessão..." -ForegroundColor $INFO_COLOR
    
    $refreshBody = @{
        refresh_token = $global:refreshToken
    } | ConvertTo-Json
    
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/auth/refresh" `
            -Method POST `
            -Headers @{"Content-Type" = "application/json" } `
            -Body $refreshBody
        
        if ($response.success) {
            Write-Host "   ✅ Sessão renovada com sucesso!" -ForegroundColor $SUCCESS_COLOR
            Write-Host "   🔑 Novo session token: $($response.session_token.Substring(0, 20))..." -ForegroundColor $INFO_COLOR
            
            # Atualizar token para logout
            $global:sessionToken = $response.session_token
        }
    }
    catch {
        Write-Host "   ❌ Erro no refresh: $($_.Exception.Message)" -ForegroundColor $FAILURE_COLOR
    }
    
    Write-Host ""
}

# ===== TESTE 6: LOGOUT =====
if ($global:sessionToken) {
    Write-Host "6️⃣  Testando LOGOUT..." -ForegroundColor $INFO_COLOR
    
    try {
        $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/auth/logout" `
            -Method POST `
            -Headers @{"Authorization" = "Bearer $global:sessionToken" }
        
        if ($response.success) {
            Write-Host "   ✅ Logout realizado com sucesso!" -ForegroundColor $SUCCESS_COLOR
        }
    }
    catch {
        Write-Host "   ❌ Erro no logout: $($_.Exception.Message)" -ForegroundColor $FAILURE_COLOR
    }
    
    Write-Host ""
}

# ===== TESTE 7: VERIFICAR QUE SESSÃO FOI REVOGADA =====
Write-Host "7️⃣  Testando acesso COM SESSÃO REVOGADA (deve falhar)..." -ForegroundColor $INFO_COLOR

try {
    $response = Invoke-RestMethod -Uri "$BASE_URL/api/v1/auth/me" `
        -Method GET `
        -Headers @{"Authorization" = "Bearer $global:sessionToken" }
    
    Write-Host "   ❌ Acesso deveria ter sido bloqueado mas passou!" -ForegroundColor $FAILURE_COLOR
}
catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "   ✅ Acesso bloqueado corretamente após logout (401)" -ForegroundColor $SUCCESS_COLOR
    }
    else {
        Write-Host "   ⚠️  Erro inesperado: $($_.Exception.Message)" -ForegroundColor "Yellow"
    }
}

Write-Host ""
Write-Host "=== FIM DOS TESTES ===" -ForegroundColor $INFO_COLOR
