# Script PowerShell para testar rotas do SIGMA-PLI
# Execute em um terminal SEPARADO enquanto o servidor FastAPI roda

$baseUrl = "http://127.0.0.1:8010"

Write-Host "`n🚀 SIGMA-PLI - Teste de Rotas" -ForegroundColor Cyan
Write-Host "Servidor: $baseUrl" -ForegroundColor Blue
Write-Host "Hora: $(Get-Date -Format 'HH:mm:ss')`n" -ForegroundColor Blue

# Testar se servidor está rodando
try {
    $response = Invoke-WebRequest -Uri "$baseUrl/health" -Method Get -TimeoutSec 5 -UseBasicParsing
    Write-Host "✅ Servidor rodando!`n" -ForegroundColor Green
}
catch {
    Write-Host "❌ SERVIDOR NÃO ESTÁ RODANDO!" -ForegroundColor Red
    Write-Host "Execute em outro terminal:" -ForegroundColor Yellow
    Write-Host "  .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8010 --reload`n" -ForegroundColor Yellow
    exit
}

# Definir rotas para testar
$routes = @{
    "🏠 HOME"                     = @("/", "/health", "/api/status")
    "📄 PÚBLICAS"                 = @("/login", "/auth/login", "/recursos", "/acesso-negado", "/email-verificado", "/selecionar-perfil")
    "📝 CADASTROS"                = @("/auth/cadastro-pessoa-fisica", "/auth/cadastro-pessoa-juridica", "/auth/cadastro-usuario")
    "🧪 TESTE (sem auth)"         = @("/teste/dashboard", "/teste/pessoa-fisica", "/teste/pessoa-juridica", "/teste/usuarios")
    "🔒 PROTEGIDAS (requer auth)" = @("/dashboard", "/pessoa-fisica", "/pessoa-juridica", "/usuarios")
}

$total = 0
$ok = 0
$auth = 0
$erros = 0

foreach ($category in $routes.Keys | Sort-Object) {
    Write-Host $category -ForegroundColor Cyan
    
    foreach ($route in $routes[$category]) {
        $total++
        try {
            $response = Invoke-WebRequest -Uri "$baseUrl$route" -Method Get -TimeoutSec 5 -UseBasicParsing -MaximumRedirection 5
            
            if ($response.StatusCode -eq 200) {
                Write-Host "  ✅ $route" -ForegroundColor Green -NoNewline
                Write-Host " [200 OK]" -ForegroundColor DarkGreen
                $ok++
            }
        }
        catch {
            $statusCode = $_.Exception.Response.StatusCode.value__
            
            if ($statusCode -eq 403) {
                Write-Host "  🔒 $route" -ForegroundColor Yellow -NoNewline
                Write-Host " [403 AUTH]" -ForegroundColor DarkYellow
                $auth++
            }
            elseif ($statusCode -eq 404) {
                Write-Host "  ❌ $route" -ForegroundColor Red -NoNewline
                Write-Host " [404 NÃO ENCONTRADO]" -ForegroundColor DarkRed
                $erros++
            }
            else {
                Write-Host "  ❌ $route" -ForegroundColor Red -NoNewline
                Write-Host " [$statusCode ERRO]" -ForegroundColor DarkRed
                $erros++
            }
        }
    }
    Write-Host ""
}

# Resumo
Write-Host "📊 RESUMO" -ForegroundColor Cyan
Write-Host "  Total de rotas testadas: $total"
Write-Host "  ✅ OK (200): $ok" -ForegroundColor Green
Write-Host "  🔒 Autenticação (403): $auth" -ForegroundColor Yellow
Write-Host "  ❌ Erros: $erros" -ForegroundColor Red

$sucesso = if ($total -gt 0) { [math]::Round((($ok + $auth) / $total) * 100, 1) } else { 0 }
Write-Host "  Taxa de sucesso: $sucesso%" -ForegroundColor Cyan

Write-Host ""

if ($erros -eq 0) {
    Write-Host "🎉 Todas as rotas estão funcionando corretamente!" -ForegroundColor Green
}
else {
    Write-Host "⚠️ Algumas rotas com problemas. Verifique os erros acima." -ForegroundColor Yellow
}

Write-Host "`n💡 Dicas:" -ForegroundColor Cyan
Write-Host "  • Rotas públicas devem retornar 200 OK" -ForegroundColor White
Write-Host "  • Rotas protegidas retornam 403 Forbidden sem autenticação" -ForegroundColor White
Write-Host "  • Use as rotas /teste/* para testar páginas sem login" -ForegroundColor White
Write-Host "  • Acesse http://127.0.0.1:8010/ no navegador para a home" -ForegroundColor White
Write-Host "  • Acesse http://127.0.0.1:8010/recursos para ver funcionalidades`n" -ForegroundColor White
