# Baixa as MENSAGENS direto por user_ns, lendo entrada\api\alvos_planilha.txt.
# Nao depende do snapshot de subscribers (pega ate quem nao esta nele).
# Retomavel: pula quem ja tem arquivo. Pode cancelar e rodar de novo.
$ErrorActionPreference = 'Stop'
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$base = 'https://app.atendedireito.com.br/api'
$msgDir = Join-Path $root 'entrada\api\messages'
New-Item -ItemType Directory -Force -Path $msgDir | Out-Null
$enc = New-Object System.Text.UTF8Encoding($false)

$key=$null
foreach($line in Get-Content (Join-Path $root '.env')){ if($line -match '^\s*MINHA_API_KEY\s*=\s*(.+?)\s*$'){ $key=$Matches[1].Trim('"').Trim("'") } }
if([string]::IsNullOrWhiteSpace($key)){ Write-Host 'ERRO: MINHA_API_KEY ausente'; Read-Host 'Enter'; exit 1 }
$headers=@{ Authorization="Bearer $key"; Accept='application/json' }

$alvosFile = Join-Path $root 'entrada\api\alvos_planilha.txt'
if(-not (Test-Path $alvosFile)){ Write-Host "ERRO: alvos_planilha.txt nao encontrado"; Read-Host 'Enter'; exit 1 }
$alvos = @(Get-Content $alvosFile | ForEach-Object { $_.Trim() } | Where-Object { $_ })
Write-Host "Alvos na lista: $($alvos.Count)"

$i=0; $baixados=0; $pulados=0; $erros=0; $vazios=0
foreach($ns in $alvos){
  $i++
  $out = Join-Path $msgDir ("$ns.json")
  if(Test-Path $out){ $pulados++; continue }
  $all = New-Object System.Collections.ArrayList
  $page=1; $lastPage=1; $ok=$true
  do {
    $u = "$base/subscriber/chat-messages?user_ns=$ns&include_bot=1&include_system=1&include_note=1&limit=100&page=$page"
    try { $r = Invoke-RestMethod -Uri $u -Headers $headers -Method GET }
    catch { $erros++; $ok=$false; Write-Host ("  ERRO ns {0}: {1}" -f $ns, $_.Exception.Message); break }
    foreach($m in @($r.data)){ [void]$all.Add($m) }
    try { $lastPage=[int]$r.meta.last_page } catch { $lastPage=1 }
    $page++
    Start-Sleep -Milliseconds 80
  } while($page -le $lastPage)
  if(-not $ok){ continue }
  if($all.Count -eq 0){ $vazios++ }
  $rec = [pscustomobject]@{ user_ns=$ns; messages=$all }
  [System.IO.File]::WriteAllText($out, ($rec | ConvertTo-Json -Depth 18), $enc)
  $baixados++
  if($i % 10 -eq 0){ Write-Host ("  {0}/{1} (baixados {2}, pulados {3}, erros {4})" -f $i,$alvos.Count,$baixados,$pulados,$erros) }
}
Write-Host ''
Write-Host ("== Concluido. Baixados: {0} | Pulados: {1} | Vazios: {2} | Erros: {3} ==" -f $baixados,$pulados,$vazios,$erros)
Read-Host 'Pressione Enter para fechar'
