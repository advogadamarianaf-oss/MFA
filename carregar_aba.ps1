param([string]$arquivo)
$ErrorActionPreference='Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$f = Join-Path $root "entrada\api\$arquivo"
if(-not (Test-Path $f)){ Write-Host "ERRO: nao achei $f"; Read-Host 'Enter'; exit 1 }
$txt = Get-Content $f -Raw -Encoding UTF8
Set-Clipboard -Value $txt
$n = ($txt -split "`n").Count
Write-Host "OK! Bloco '$arquivo' carregado na area de transferencia ($n linhas)."
Write-Host "Agora va na aba certa, clique na celula inicial e tecle Ctrl+V."
Read-Host 'Pressione Enter para fechar'
