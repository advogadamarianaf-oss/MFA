/**
 * Pipeline diario Atende Direito -> Planilha (Google Apps Script)
 * Roda nos servidores do Google (sem a sua maquina). Colado a esta planilha.
 *
 * CONFIG (uma vez):
 *  1) Projeto > Configuracoes do projeto > Propriedades do script:
 *       adicione  ATENDE_API_KEY  = (sua chave da API do Atende Direito)
 *  2) Rode a funcao  instalarGatilho()  uma vez (cria o agendamento diario 13h).
 *  3) Para testar agora, rode  atualizarPlanilha().
 *
 * Atualiza as colunas RESUMO APOS 24H/7/15/30 das abas abaixo. Incremental:
 * so reprocessa leads cujo last_message_at mudou (cache na aba _estado_pipeline).
 */

var API = 'https://app.atendedireito.com.br/api';
var TABS = ['CAMPANHA META', 'CAMPANHA GOOGLE', 'ORGÂNICO', 'MANYCHAT', 'REUNIÕES & FECHAMENTOS'];
var BUDGET_MS = 280000; // ~4.6 min (limite do Google e 6 min)
var ORIG = {lead_ads:'anúncio (Meta)', inbound_webhook:'formulário/Instagram', ig:'Instagram'};

function key_() {
  var k = PropertiesService.getScriptProperties().getProperty('ATENDE_API_KEY');
  if (!k) throw new Error('Falta a propriedade ATENDE_API_KEY (Configuracoes do projeto > Propriedades do script).');
  return k;
}
function apiGet_(path) {
  var r = UrlFetchApp.fetch(API + path, {headers:{Authorization:'Bearer '+key_(), Accept:'application/json'}, muteHttpExceptions:true});
  var c = r.getResponseCode();
  if (c >= 300) throw new Error('API ' + c + ' em ' + path);
  return JSON.parse(r.getContentText());
}
function digits_(s){ return (s==null?'':String(s)).replace(/\D/g,''); }
function phoneKey_(s){ var d=digits_(s); if(d.indexOf('55')===0 && d.length>=12) d=d.substring(2); if(d.length>=10) return d.substring(0,2)+d.substring(2).slice(-8); return d; }
function clip_(s){ s=(s==null?'':String(s)).replace(/\s+/g,' ').trim(); return s.length>250?s.substring(0,250):s; }

function instalarGatilho() {
  var t = ScriptApp.getProjectTriggers();
  for (var i=0;i<t.length;i++) if (t[i].getHandlerFunction()==='atualizarPlanilha') ScriptApp.deleteTrigger(t[i]);
  ScriptApp.newTrigger('atualizarPlanilha').timeBased().everyDays(1).atHour(13).create();
  return 'Gatilho diario criado para ~13h.';
}

function uf_(s, cands){
  var fs = (s && s.user_fields) || [];
  for (var i=0;i<fs.length;i++){ var n=(fs[i].name||'').toLowerCase();
    for (var j=0;j<cands.length;j++){ if(n.indexOf(cands[j].toLowerCase())>=0){ var v=fs[i].value; if(typeof v==='string' && v.trim()) return v.trim(); } } }
  return '';
}
function perfil_(s){
  if(!s) return ['',''];
  var cli=uf_(s,['Tem clinica','dono ou gestor']), proc=uf_(s,['Recebeu processos','responder a processos']);
  var cnpj=uf_(s,['Quantas clinicas','mais de um CNPJ']), prof=uf_(s,['Quantos prof','profissionais']), cid=uf_(s,['Cidade/Estado','cidade']);
  cli=cli.replace(/_/g,' ').trim().toLowerCase();
  var map={'clínica médica':'clínica médica','clínica odontológica':'clínica odonto','clinica odontologica':'clínica odonto','multiespecialidades':'multiespecialidades','clínica de estética':'clínica estética','clinica de estetica':'clínica estética','sim':'clínica (saúde)'};
  if(map[cli]) cli=map[cli];
  var p=proc.toLowerCase(), px='';
  if(p.indexOf('estou respondendo')>=0) px='processo ativo (defesa+prevenção)';
  else if(p.indexOf('já respondi')>=0||p.indexOf('ja respondi')>=0) px='já processado (quer prevenção)';
  else if(p.indexOf('nunca')>=0) px='nunca processado (quer prevenção)';
  else if(p.indexOf('sim')===0) px='já teve processo';
  else if(p.indexOf('não')===0||p.indexOf('nao')===0) px='sem processos';
  var cx='', cl=cnpj.toLowerCase();
  if(cl.indexOf('2 a 4')>=0) cx='2–4 CNPJ'; else if(cl.indexOf('5 a 10')>=0) cx='5–10 CNPJ'; else if(cl.indexOf('sim')===0) cx='+1 CNPJ';
  var pf='', m=prof.toLowerCase().match(/(\d+\s*a\s*\d+|\d+)/); if(m) pf=m[1].replace(/\s+/g,' ').trim()+' prof';
  var parts=[cli,pf,cx,px].filter(function(x){return x;});
  return [parts.join(', '), cid?cid.replace(/\b\w/g,function(c){return c.toUpperCase();}):''];
}
function content_(m){ var c=m.content||''; return (typeof c==='object')?JSON.stringify(c):String(c); }
function getMsgs_(ns){
  var out=[], page=1, last=1;
  do { var r=apiGet_('/subscriber/chat-messages?user_ns='+ns+'&include_bot=1&include_system=1&include_note=1&limit=100&page='+page);
    out=out.concat(r.data||[]); last=(r.meta&&r.meta.last_page)?r.meta.last_page:1; page++;
  } while(page<=last && page<=10);
  out.forEach(function(m){ m._t = m.ts? new Date(parseInt(m.ts,10)*1000):null; });
  out=out.filter(function(m){return m._t;});
  out.sort(function(a,b){return a._t-b._t;});
  return out;
}
function state_(ms, cutoff){
  var boards=[],nin=0,nout=0,errs=0,reun=false,hum=false,flux=false;
  for(var i=0;i<ms.length;i++){ var m=ms[i]; if(m._t>cutoff) break; var c=content_(m), t=m.type||'';
    if(c.indexOf('Moved to board:')===0){ var b=c.replace('Moved to board:','').replace(/\*\*\*/g,'').trim(); boards.push(b);
      if(b.indexOf('Reuni')>=0)reun=true; if(b.indexOf('ATENDIMENTO HUMANO')>=0)hum=true; if(b.indexOf('FLUXOGRAMA')>=0)flux=true; }
    if(c.indexOf('WhatsApp Error')>=0)errs++;
    if(t==='in')nin++; else if(t==='out')nout++; }
  return {crm:boards.length?boards[boards.length-1]:'LEAD ENTROU NO COMERCIAL',boards:boards,nin:nin,nout:nout,errs:errs,reun:reun,hum:hum,flux:flux};
}
function dayEnd_(d, plus){ var x=new Date(d.getFullYear(),d.getMonth(),d.getDate()+plus,23,59,59); return x; }
function fmt_(d){ return ('0'+d.getDate()).slice(-2)+'/'+('0'+(d.getMonth()+1)).slice(-2)+'/'+d.getFullYear(); }
function resumo_(ns, sub){
  var ms=getMsgs_(ns); if(!ms.length) return null;
  var t0=ms[0]._t, today=new Date();
  var pf=perfil_(sub), perf=pf[0], cid=pf[1];
  var orig=ORIG[((sub&&sub.opted_in_through)||'').toLowerCase()] || ((sub&&sub.opted_in_through)||'lead');
  var st1=state_(ms, dayEnd_(t0,1));
  var cab='Lead de '+orig+(cid?' ('+cid+')':'')+(perf?'; '+perf+'.':'.');
  var acao;
  if(st1.nin===0) acao='Recebeu abertura + '+Math.max(st1.nout-1,0)+' follow-up(s); nao respondeu.';
  else { acao='Respondeu ('+st1.nin+'x)'+(st1.reun?' e teve reuniao agendada.':(st1.hum?' e chegou ao atendimento humano.':(st1.flux?' no fluxograma.':'.'))); }
  var al=st1.errs?(' '+st1.errs+' falha(s) de entrega.'):'';
  var cells=[clip_(cab+' '+acao+' CRM: '+st1.crm+'.'+al)];
  var prev=st1, ds=[7,15,30];
  for(var k=0;k<ds.length;k++){ var d=ds[k], cut=dayEnd_(t0,d), nel=cut>today, ate=fmt_(cut), stx=state_(ms,cut), txt;
    var novos=stx.boards.filter(function(b){return prev.boards.indexOf(b)<0;});
    if(novos.length) txt='Avancou para '+novos[novos.length-1]+' (CRM atual).';
    else if(stx.nin>prev.nin) txt='Lead respondeu (+'+(stx.nin-prev.nin)+'); CRM: '+stx.crm+'.';
    else txt=(nel?'Janela ainda nao decorrida; ':('Sem novas interacoes ate '+ate+'; '))+'CRM: '+stx.crm+'.';
    if(stx.errs>prev.errs) txt+=' +'+(stx.errs-prev.errs)+' falha(s) de entrega.';
    cells.push(clip_(txt)); prev=stx; }
  return cells;
}

function loadSubs_(){
  var p1=apiGet_('/subscribers?limit=100&page=1'), last=p1.meta.last_page, subs=p1.data.slice();
  for(var pg=2;pg<=last;pg++){ subs=subs.concat(apiGet_('/subscribers?limit=100&page='+pg).data); }
  var byNs={}, byKey={};
  subs.forEach(function(s){ byNs[s.user_ns]=s; var k=phoneKey_(s.phone); if(!(k in byKey)) byKey[k]=s; });
  return {byNs:byNs, byKey:byKey};
}
function loadEstado_(){
  var sh=SpreadsheetApp.getActiveSpreadsheet().getSheetByName('_estado_pipeline');
  var map={};
  if(!sh){ sh=SpreadsheetApp.getActiveSpreadsheet().insertSheet('_estado_pipeline'); sh.appendRow(['user_ns','lmt','r24','r7','r15','r30']); sh.hideSheet(); return {sh:sh,map:map}; }
  var v=sh.getDataRange().getValues();
  for(var i=1;i<v.length;i++){ map[v[i][0]]={lmt:String(v[i][1]||''), cells:[v[i][2],v[i][3],v[i][4],v[i][5]]}; }
  return {sh:sh, map:map};
}
function saveEstado_(sh, map){
  var rows=[['user_ns','lmt','r24','r7','r15','r30']];
  for(var ns in map){ var e=map[ns]; rows.push([ns, e.lmt, e.cells[0], e.cells[1], e.cells[2], e.cells[3]]); }
  sh.clearContents(); sh.getRange(1,1,rows.length,6).setValues(rows);
}

function atualizarPlanilha(){
  var start=Date.now();
  var data=loadSubs_(); var byNs=data.byNs, byKey=data.byKey;
  var est=loadEstado_(); var cache=est.map;
  var ss=SpreadsheetApp.getActiveSpreadsheet();
  var totalLeads=0, reproc=0;
  for(var ti=0; ti<TABS.length; ti++){
    var sh=ss.getSheetByName(TABS[ti]); if(!sh) continue;
    var vals=sh.getDataRange().getValues(); if(vals.length<2) continue;
    var H=vals[0].map(function(x){return String(x).toUpperCase();});
    function find(names){ for(var i=0;i<H.length;i++) for(var j=0;j<names.length;j++) if(H[i].indexOf(names[j])>=0) return i; return -1; }
    var idCol=find(['ATENDE DIREITO ID']), telCol=find(['TELEFONE']), resCol=find(['RESUMO APÓS 24H','RESUMO APOS 24H']);
    if(resCol<0) continue;
    var out=[];
    for(var r=1;r<vals.length;r++){
      var row=vals[r], ns=null;
      if(idCol>=0 && String(row[idCol]).indexOf('f175863u')===0) ns=String(row[idCol]).trim();
      else if(telCol>=0){ var s=byKey[phoneKey_(row[telCol])]; if(s) ns=s.user_ns; }
      if(!ns){ out.push(['','','','']); continue; }
      totalLeads++;
      var sub=byNs[ns]; var lmt=sub?String(sub.last_message_at||''):'';
      var c=cache[ns];
      var precisa = !c || (lmt && c.lmt!==lmt) || (!c && true);
      if(precisa && (Date.now()-start) < BUDGET_MS){
        var cells=null; try{ cells=resumo_(ns, sub); }catch(e){ cells=null; }
        if(!cells) cells=['Lead sem conversa baixada / nao localizado.','—','—','—'];
        cache[ns]={lmt:lmt, cells:cells}; reproc++;
        out.push(cells);
      } else if(c){ out.push(c.cells); }
      else { // sem cache e sem tempo: PRESERVA o que ja esta na planilha (proxima execucao reprocessa)
        out.push([row[resCol]||'', row[resCol+1]||'', row[resCol+2]||'', row[resCol+3]||'']);
      }
    }
    sh.getRange(2, resCol+1, out.length, 4).setValues(out);
  }
  saveEstado_(est.sh, cache);
  var msg='Atualizado '+fmt_(new Date())+' '+new Date().toLocaleTimeString()+' | leads='+totalLeads+' | reprocessados='+reproc+' | tempo='+Math.round((Date.now()-start)/1000)+'s';
  PropertiesService.getScriptProperties().setProperty('ULTIMA_EXECUCAO', msg);
  return msg;
}
