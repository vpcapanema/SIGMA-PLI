# SIGMA-PLI - Script de Gerenciamento Docker
# Facilita comandos comuns do Docker Compose

param(
    [Parameter(Position=0)]
    [ValidateSet('start', 'stop', 'restart', 'logs', 'build', 'clean', 'status', 'shell', 'db', 'test')]
    [string]$Command = 'status',
    
    [Parameter(Position=1)]
    [string]$Service = 'backend'
)

function Show-Header {
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host "  SIGMA-PLI - Docker Manager" -ForegroundColor Cyan
    Write-Host "=====================================" -ForegroundColor Cyan
    Write-Host ""
}

function Start-Services {
    Show-Header
    Write-Host "🚀 Iniciando serviços..." -ForegroundColor Green
    docker-compose up -d
    Write-Host ""
    Write-Host "✅ Serviços iniciados!" -ForegroundColor Green
    Write-Host "📍 Acesse: http://localhost:8010" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Ver logs:" -ForegroundColor Gray
    Write-Host "  .\docker.ps1 logs" -ForegroundColor White
}

function Stop-Services {
    Show-Header
    Write-Host "⏹️ Parando serviços..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "✅ Serviços parados!" -ForegroundColor Green
}

function Restart-Services {
    Show-Header
    Write-Host "🔄 Reiniciando $Service..." -ForegroundColor Yellow
    docker-compose restart $Service
    Write-Host "✅ $Service reiniciado!" -ForegroundColor Green
}

function Show-Logs {
    Show-Header
    Write-Host "📋 Logs do $Service (Ctrl+C para sair)..." -ForegroundColor Cyan
    Write-Host ""
    docker-compose logs -f --tail=100 $Service
}

function Build-Services {
    Show-Header
    Write-Host "🔨 Building $Service..." -ForegroundColor Yellow
    docker-compose build $Service
    Write-Host ""
    Write-Host "✅ Build concluído!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Iniciar serviço:" -ForegroundColor Gray
    Write-Host "  .\docker.ps1 start" -ForegroundColor White
}

function Clean-All {
    Show-Header
    Write-Host "🧹 ATENÇÃO: Isso vai remover TODOS os containers e volumes!" -ForegroundColor Red
    $confirm = Read-Host "Confirmar? (s/N)"
    
    if ($confirm -eq 's' -or $confirm -eq 'S') {
        Write-Host ""
        Write-Host "Removendo containers e volumes..." -ForegroundColor Yellow
        docker-compose down -v
        Write-Host ""
        Write-Host "✅ Limpeza concluída!" -ForegroundColor Green
    } else {
        Write-Host "❌ Operação cancelada" -ForegroundColor Red
    }
}

function Show-Status {
    Show-Header
    Write-Host "📊 Status dos Serviços:" -ForegroundColor Cyan
    Write-Host ""
    docker-compose ps
    Write-Host ""
    Write-Host "💾 Uso de Espaço:" -ForegroundColor Cyan
    docker system df
}

function Open-Shell {
    Show-Header
    Write-Host "🐚 Abrindo shell no $Service..." -ForegroundColor Cyan
    Write-Host "(Digite 'exit' para sair)" -ForegroundColor Gray
    Write-Host ""
    docker-compose exec $Service bash
}

function Connect-Database {
    Show-Header
    Write-Host "🗄️ Conectando ao PostgreSQL..." -ForegroundColor Cyan
    Write-Host "(Digite '\q' para sair)" -ForegroundColor Gray
    Write-Host ""
    docker-compose exec postgres psql -U sigma_user -d sigma_pli_db
}

function Test-Application {
    Show-Header
    Write-Host "🧪 Testando aplicação..." -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "1. Health Check..." -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8010/health" -TimeoutSec 5
        Write-Host "✅ Health: $($response.status)" -ForegroundColor Green
    } catch {
        Write-Host "❌ Health check falhou!" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "2. Status API..." -ForegroundColor Yellow
    try {
        $response = Invoke-RestMethod -Uri "http://localhost:8010/api/v1/status" -TimeoutSec 5
        Write-Host "✅ Status: $($response.status)" -ForegroundColor Green
        Write-Host "✅ Version: $($response.version)" -ForegroundColor Green
        Write-Host "✅ Uptime: $([int]$response.uptime) segundos" -ForegroundColor Green
    } catch {
        Write-Host "❌ Status API falhou!" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "3. PostgreSQL..." -ForegroundColor Yellow
    $pgTest = docker-compose exec -T postgres pg_isready -U sigma_user 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ PostgreSQL: OK" -ForegroundColor Green
    } else {
        Write-Host "❌ PostgreSQL: Erro" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "📊 Resumo:" -ForegroundColor Cyan
    docker-compose ps
}

function Show-Help {
    Show-Header
    Write-Host "Comandos disponíveis:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "  start      " -ForegroundColor White -NoNewline
    Write-Host "- Iniciar todos os serviços" -ForegroundColor Gray
    Write-Host "  stop       " -ForegroundColor White -NoNewline
    Write-Host "- Parar todos os serviços" -ForegroundColor Gray
    Write-Host "  restart    " -ForegroundColor White -NoNewline
    Write-Host "- Reiniciar um serviço (padrão: backend)" -ForegroundColor Gray
    Write-Host "  logs       " -ForegroundColor White -NoNewline
    Write-Host "- Ver logs em tempo real (padrão: backend)" -ForegroundColor Gray
    Write-Host "  build      " -ForegroundColor White -NoNewline
    Write-Host "- Fazer build de um serviço (padrão: backend)" -ForegroundColor Gray
    Write-Host "  clean      " -ForegroundColor White -NoNewline
    Write-Host "- Limpar containers e volumes (CUIDADO!)" -ForegroundColor Gray
    Write-Host "  status     " -ForegroundColor White -NoNewline
    Write-Host "- Mostrar status dos serviços" -ForegroundColor Gray
    Write-Host "  shell      " -ForegroundColor White -NoNewline
    Write-Host "- Abrir shell no container (padrão: backend)" -ForegroundColor Gray
    Write-Host "  db         " -ForegroundColor White -NoNewline
    Write-Host "- Conectar ao PostgreSQL" -ForegroundColor Gray
    Write-Host "  test       " -ForegroundColor White -NoNewline
    Write-Host "- Testar se tudo está funcionando" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Exemplos:" -ForegroundColor Cyan
    Write-Host "  .\docker.ps1 start" -ForegroundColor White
    Write-Host "  .\docker.ps1 logs backend" -ForegroundColor White
    Write-Host "  .\docker.ps1 restart postgres" -ForegroundColor White
    Write-Host "  .\docker.ps1 shell backend" -ForegroundColor White
    Write-Host ""
}

# Main
switch ($Command) {
    'start'   { Start-Services }
    'stop'    { Stop-Services }
    'restart' { Restart-Services }
    'logs'    { Show-Logs }
    'build'   { Build-Services }
    'clean'   { Clean-All }
    'status'  { Show-Status }
    'shell'   { Open-Shell }
    'db'      { Connect-Database }
    'test'    { Test-Application }
    default   { Show-Help }
}
