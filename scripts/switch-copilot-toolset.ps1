param(
  [ValidateSet('sigma-core','sigma-dados','sigma-devops')]
  [string]$Toolset = 'sigma-core'
)

$UserPrompts = Join-Path $env:APPDATA 'Code - Insiders\User\prompts'
$Target = Join-Path $UserPrompts 't1.toolsets.jsonc'
$Backup = "$Target.bak-$(Get-Date -Format yyyyMMdd-HHmmss)"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$ToolsetsDir = Join-Path $RepoRoot 'docs\toolsets'
$Map = @{
  'sigma-core'  = Join-Path $ToolsetsDir 't1.toolsets.sigma-core.jsonc'
  'sigma-dados' = Join-Path $ToolsetsDir 't1.toolsets.sigma-dados.jsonc'
  'sigma-devops'= Join-Path $ToolsetsDir 't1.toolsets.sigma-devops.jsonc'
}

if (-not (Test-Path $Map[$Toolset])) { throw "Toolset file not found: $($Map[$Toolset])" }

New-Item -ItemType Directory -Path $UserPrompts -Force | Out-Null
if (Test-Path $Target) { Copy-Item $Target $Backup }
Copy-Item $Map[$Toolset] $Target -Force

Write-Host "Applied toolset: $Toolset" -ForegroundColor Green
Write-Host "File: $Target"
