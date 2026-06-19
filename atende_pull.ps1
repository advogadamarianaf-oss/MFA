# Atende Direito - puxador COMPLETO (roda na SUA maquina).
# Chave lida do .env (MINHA_API_KEY). Baixa todos os leads (paginando)
# e testa o formato correto de include_bot para as mensagens.

$ErrorActionPreference = 'Stop'
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$base = 'https://app.atendedireito.com.br/api'
$outDir = Join-Path $root 'entrada\api'
$subDir = Join-Path $outDir 'subscribers'
New-Item -ItemType Directory -Force -Path $subDir | Out-Null

$enc = New-Object System.Text.UTF8Encoding($false)
function Save-Json($obj,$path){ [System.IO.File]::WriteAllText($path, ($obj | ConvertTo-Json -Depth 18), $enc) }
function Save-Text($txt,$path){ [System.IO.File]::WriteAllText($path, [string]$txt, $enc) }

$key=$null
foreach($line in Get-Content (Join-Path $root '.env')){ if($line -match '^\s*MINHA_API_KEY\s*=\s*(.+?)\s*$'){ $key=$Matches[1].Trim('"').Trim("'") } }
if([string]::IsNullOrWhiteSpace($key)){ Write-Host 'ERRO: MINHA_API_KEY ausente no .env'; Read-Host 'Enter'; exit 1 }
$headers=@{ Authorization="Bearer $key"; Accept='application/json' }

function Get-Api($url){
  try { return @{ ok=$true; data=(Invoke-RestMethod -Uri $url -Headers $headers -Method GET) } }
  catch {
    $body=$null; try{ $body=$_.ErrorDetails.Message }catch{}
    if(-not $body){ try{ $s=$_.Exception.Response.GetResponseStream(); $r=New-Object IO.StreamReader($s); $body=$r.ReadToEnd() }catch{} }
    return @{ ok=$false; error=$_.Exception.Message; body=$body }
  }
}

# ---- 1) Baixar TODOS os subscribers (paginando, 100 por pagina) ----
Write-Host 'Baixando subscribers (pagina 1)...'
$p1 = Get-Api "$base/subscribers?limit=100&page=1"
if(-not $p1.ok){ Write-Host "ERRO subscribers: $($p1.error)"; Read-Host 'Enter'; exit 1 }
$last = [int]$p1.data.meta.last_page
$total = [int]$p1.data.meta.total
Write-Host "  total de leads: $total  | paginas: $last"
Save-Json $p1.data.data (Join-Path $subDir ('p{0:000}.json' -f 1))
for($pg=2; $pg -le $last; $pg++){
  $r = Get-Api "$base/subscribers?limit=100&page=$pg"
  if($r.ok){ Save-Json $r.data.data (Join-Path $subDir ('p{0:000}.json' -f $pg)); Write-Host "  pagina $pg/$last OK" }
  else { Write-Host "  pagina $pg FALHOU: $($r.error)"; Start-Sleep -Milliseconds 500 }
  Start-Sleep -Milliseconds 150
}
Write-Host 'Subscribers concluido.'

# ---- 2) Descobrir o formato correto de include_bot (testa num lead com mensagens) ----
$ns = $p1.data.data[0].user_ns
Write-Host "Testando formatos de chat-messages em user_ns=$ns ..."
$tries = @(
  "$base/subscriber/chat-messages?user_ns=$ns",
  "$base/subscriber/chat-messages?user_ns=$ns&include_bot=1",
  "$base/subscriber/chat-messages?user_ns=$ns&include_bot=1&include_system=1&include_note=1",
  "$base/subscriber/chat-messages?user_ns=$ns&include_bot=1&include_system=1&include_note=1&limit=200",
  "$base/subscriber/chat-messages?user_ns=$ns&msg_type=all",
  "$base/subscriber/chat-messages?user_ns=$ns&include_bot=yes"
)
$report=@(); $best=$null; $bestCount=-1
foreach($u in $tries){
  $r = Get-Api $u
  if($r.ok){
    $cnt = 0; try{ $cnt = [int]$r.data.meta.total }catch{}
    if($cnt -eq 0){ try{ $cnt = @($r.data.data).Count }catch{} }
    $report += [pscustomobject]@{ url=$u; ok=$true; count=$cnt }
    if($cnt -gt $bestCount){ $bestCount=$cnt; $best=@{url=$u; data=$r.data} }
  } else {
    $report += [pscustomobject]@{ url=$u; ok=$false; count=-1; erro=$r.error; body=$r.body }
  }
}
Save-Json $report (Join-Path $outDir '_msg_diagnostico.json')
if($best){ Save-Json $best.data (Join-Path $outDir '_amostra_mensagens.json'); Save-Text $best.url (Join-Path $outDir '_amostra_mensagens_url.txt'); Write-Host "  melhor: $($best.url)  (mensagens: $bestCount)" }

Write-Host ''
Write-Host '== Pronto! Subscribers em entrada\api\subscribers\ e diagnostico de mensagens salvo. Avise o Claude. =='
Read-Host 'Pressione Enter para fechar'
