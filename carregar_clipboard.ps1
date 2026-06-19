# Carrega o bloco de resumos (paste_M2_Pn.tsv) na area de transferencia.
# Depois o Claude cola em M2 na planilha (ou voce: clique em M2 e Ctrl+V).
$ErrorActionPreference='Stop'
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$f = Join-Path $root 'entrada\api\paste_M2_Pn.tsv'
if(-not (Test-Path $f)){ Write-Host "ERRO: nao achei $f"; Read-Host 'Enter'; exit 1 }
$txt = Get-Content $f -Raw -Encoding UTF8
Set-Clipboard -Value $txt
$n = ($txt -split "`n").Count
Write-Host "OK! Bloco de resumos carregado na area de transferencia ($n linhas)."
Write-Host "Agora volte ao Claude e diga 'colei'. (Nao copie mais nada antes de colar.)"
Read-Host 'Pressione Enter para fechar'
