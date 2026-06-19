# Atende Direito - puxa as MENSAGENS (transcripts) de cada lead via API.
# Retomavel: pula leads cujo arquivo de mensagens ja existe. Pode cancelar e rodar de novo.
# Pre-requisito: rodar antes o atende_pull.ps1 (baixa os subscribers).

$ErrorActionPreference = 'Stop'
try { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12 } catch {}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root
$base = 'https://app.atendedireito.com.br/api'
$subDir = Join-Path $root 'entrada\api\subscribers'
$msgDir = Join-Path $root 'entrada\api\messages'
New-Item -ItemType Directory -Force -Path $msgDir | Out-Null

# >>> ESCOPO: se existir entrada\api\alvos_planilha.txt, baixa SO os leads dessa lista
#     (os 130 leads da planilha CAMPANHA META ja casados). Para baixar TODOS, apague
#     ou renomeie esse arquivo. (a opcao por etiqueta META abaixo so vale se nao houver alvos.)
$somentePlanilha = $false

$enc = New-Object System.Text.UTF8Encoding($false)
function Save-Json($obj,$path){ [System.IO.File]::WriteAllText($path, ($obj | ConvertTo-Json -Depth 18), $enc) }

$key=$null
foreach($line in Get-Content (Join-Path $root '.env')){ if($line -match '^\s*MINHA_API_KEY\s*=\s*(.+?)\s*$'){ $key=$Matches[1].Trim('"').Trim("'") } }
if([string]::IsNullOrWhiteSpace($key)){ Write-Host 'ERRO: MINHA_API_KEY ausente'; Read-Host 'Enter'; exit 1 }
$headers=@{ Authorization="Bearer $key"; Accept='application/json' }

function Get-Api($url){
  try { return @{ ok=$true; data=(Invoke-RestMethod -Uri $url -Headers $headers -Method GET) } }
  catch { return @{ ok=$false; error=$_.Exception.Message } }
}

# Carregar lista de subscribers
if(-not (Test-Path $subDir)){ Write-Host "ERRO: rode antes o atende_pull.ps1 (pasta subscribers nao existe)"; Read-Host 'Enter'; exit 1 }
$subs = @()
foreach($f in Get-ChildItem $subDir -Filter 'p*.json'){ $subs += (Get-Content $f.FullName -Raw | ConvertFrom-Json) }
# Lista de alvos (planilha) tem prioridade
$alvosFile = Join-Path $root 'entrada\api\alvos_planilha.txt'
$alvosSet = $null
if (Test-Path $alvosFile) {
  $alvosSet = New-Object System.Collections.Generic.HashSet[string]
  foreach($a in Get-Content $alvosFile){ if($a.Trim()){ [void]$alvosSet.Add($a.Trim()) } }
  Write-Host "Lista de alvos da planilha encontrada: $($alvosSet.Count) leads"
}
if ($alvosSet -ne $null) {
  $alvo = $subs | Where-Object { $_.user_ns -and $alvosSet.Contains([string]$_.user_ns) }
} elseif ($somentePlanilha) {
  $alvo = $subs | Where-Object { $_.user_ns -and (($_.labels | ForEach-Object { $_.name }) -contains 'META') }
} else {
  $alvo = $subs | Where-Object { $_.user_ns }
}
Write-Host "Leads a processar: $($alvo.Count)"

$i=0; $baixados=0; $pulados=0; $erros=0
foreach($s in $alvo){
  $i++
  $ns = $s.user_ns
  $out = Join-Path $msgDir ("$ns.json")
  if(Test-Path $out){ $pulados++; continue }
  # paginar mensagens (limit max = 100)
  $all = New-Object System.Collections.ArrayList
  $page=1; $lastPage=1
  do {
    $u = "$base/subscriber/chat-messages?user_ns=$ns&include_bot=1&include_system=1&include_note=1&limit=100&page=$page"
    $r = Get-Api $u
    if(-not $r.ok){ $erros++; break }
    foreach($m in @($r.data.data)){ [void]$all.Add($m) }
    try { $lastPage=[int]$r.data.meta.last_page } catch { $lastPage=1 }
    $page++
    Start-Sleep -Milliseconds 80
  } while($page -le $lastPage)
  $rec = [pscustomobject]@{ user_ns=$ns; user_id=$s.user_id; name=$s.name; phone=$s.phone; labels=$s.labels; messages=$all }
  Save-Json $rec $out
  $baixados++
  if($i % 25 -eq 0){ Write-Host ("  {0}/{1}  (baixados {2}, pulados {3}, erros {4})" -f $i,$alvo.Count,$baixados,$pulados,$erros) }
}
Write-Host ''
Write-Host ("== Concluido. Baixados: {0} | Pulados (ja existiam): {1} | Erros: {2} ==" -f $baixados,$pulados,$erros)
Write-Host "Arquivos em entrada\api\messages\<user_ns>.json"
Read-Host 'Pressione Enter para fechar'
