# -*- coding: utf-8 -*-
# Pipeline diario TUDO-EM-UM (roda na maquina, sem Claude):
#   1) le as abas da planilha via Google Sheets API (gcred.json)
#   2) baixa subscribers + conversas do Atende Direito (MINHA_API_KEY no .env)
#   3) gera resumo data-driven por janela (24h/7/15/30) com CRM real (boards)
#   4) escreve as colunas RESUMO de cada aba via Sheets API
# Requisitos: pip install google-auth google-api-python-client
import os, sys, re, json, time, datetime, urllib.request, urllib.parse
ROOT = os.path.dirname(os.path.abspath(__file__))
SPREADSHEET_ID = '1BodcfEOso5pooeOSnA2Gq-OJVQtVcjleIEAfjvwM5IM'
API_BASE = 'https://app.atendedireito.com.br/api'
TODAY = datetime.date.today()
# abas a processar (CAPTACAO ATIVA e PIXEL META ficam de fora)
TABS = ['CAMPANHA META', 'CAMPANHA GOOGLE', 'ORGÂNICO', 'MANYCHAT', 'REUNIÕES & FECHAMENTOS']

_LOGF=os.path.join(ROOT,'pipeline_log.txt')
def log(*a):
    msg=' '.join(str(x) for x in a)
    print(msg, flush=True)
    try:
        with open(_LOGF,'a',encoding='utf-8') as f: f.write(msg+'\n')
    except Exception: pass
log('=== execucao %s ==='%datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S'))

# ---- credenciais ----
key=None
envf=os.path.join(ROOT,'.env')
if os.path.exists(envf):
    for line in open(envf,encoding='utf-8',errors='ignore'):
        m=re.match(r'\s*MINHA_API_KEY\s*=\s*(.+?)\s*$', line)
        if m: key=m.group(1).strip().strip('"').strip("'")
if not key: log('ERRO: MINHA_API_KEY ausente no .env'); sys.exit(1)
try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
except Exception:
    log('Faltam libs. Rode: pip install google-auth google-api-python-client'); sys.exit(1)
gp=os.path.join(ROOT,'gcred.json')
if not os.path.exists(gp): log('ERRO: gcred.json nao encontrado.'); sys.exit(1)
creds=Credentials.from_service_account_file(gp, scopes=['https://www.googleapis.com/auth/spreadsheets'])
sheets=build('sheets','v4',credentials=creds,cache_discovery=False).spreadsheets()

# ---- helpers API Atende ----
def api_get(path):
    url=API_BASE+path
    req=urllib.request.Request(url, headers={'Authorization':'Bearer '+key,'Accept':'application/json'})
    for tent in range(3):
        try:
            with urllib.request.urlopen(req, timeout=40) as r: return json.load(r)
        except Exception as e:
            if tent==2: raise
            time.sleep(1.0)

def digits(s): return re.sub(r'\D','',s or '')
def phone_key(d):
    d=digits(d)
    if d.startswith('55') and len(d)>=12: d=d[2:]
    if len(d)>=10: return d[:2]+d[2:][-8:]
    return d

# ---- 1) baixar subscribers ----
log('Baixando subscribers...')
p1=api_get('/subscribers?limit=100&page=1')
last=int(p1['meta']['last_page'])
subs=list(p1['data'])
for pg in range(2,last+1):
    subs+=api_get('/subscribers?limit=100&page=%d'%pg)['data']
    time.sleep(0.1)
by_ns={s.get('user_ns'):s for s in subs}
by_key={}
for s in subs: by_key.setdefault(phone_key(s.get('phone')), s)
log('  subscribers: %d'%len(subs))

# ---- helpers de analise ----
def uf(s,*cands):
    for f in (s.get('user_fields') or []):
        n=(f.get('name') or '').lower()
        for c in cands:
            if c.lower() in n:
                v=f.get('value')
                if isinstance(v,str) and v.strip(): return v.strip()
    return ''
def perfil(s):
    if not s: return '', ''
    cli=uf(s,'Tem clinica','dono ou gestor'); proc=uf(s,'Recebeu processos','responder a processos')
    cnpj=uf(s,'Quantas clinicas','mais de um CNPJ'); prof=uf(s,'Quantos prof','profissionais'); cid=uf(s,'Cidade/Estado','cidade')
    cli=cli.replace('_',' ').strip().lower()
    cli={'clínica médica':'clínica médica','clínica odontológica':'clínica odonto','clinica odontologica':'clínica odonto','multiespecialidades':'multiespecialidades','clínica de estética':'clínica estética','clinica de estetica':'clínica estética','sim':'clínica (saúde)'}.get(cli,cli)
    p=proc.lower()
    if 'estou respondendo' in p: px='processo ativo (defesa+prevenção)'
    elif 'já respondi' in p or 'ja respondi' in p: px='já processado (quer prevenção)'
    elif 'nunca' in p: px='nunca processado (quer prevenção)'
    elif p.startswith('sim'): px='já teve processo'
    elif p.startswith('não') or p.startswith('nao'): px='sem processos'
    else: px=''
    cx=''; cl=cnpj.lower()
    if '2 a 4' in cl: cx='2–4 CNPJ'
    elif '5 a 10' in cl: cx='5–10 CNPJ'
    elif cl.startswith('sim'): cx='+1 CNPJ'
    pf=''; m=re.search(r'(\d+\s*a\s*\d+|\d+)', prof.lower())
    if m: pf=re.sub(r'\s+',' ',m.group(1)).strip()+' prof'
    parts=[x for x in [cli,pf,cx,px] if x]
    return ', '.join(parts), (cid.title() if cid else '')
def dtf(ts):
    try: return datetime.datetime.fromtimestamp(int(ts))
    except: return None
def mcontent(m):
    c=m.get('content') or ''
    return json.dumps(c,ensure_ascii=False) if isinstance(c,(dict,list)) else c
ORIG={'lead_ads':'anúncio (Meta)','inbound_webhook':'formulário/Instagram','ig':'Instagram'}
def get_messages(ns):
    out=[]; page=1; lastp=1
    while page<=lastp:
        r=api_get('/subscriber/chat-messages?user_ns=%s&include_bot=1&include_system=1&include_note=1&limit=100&page=%d'%(ns,page))
        out+=r.get('data',[])
        try: lastp=int(r['meta']['last_page'])
        except: lastp=1
        page+=1; time.sleep(0.05)
    for m in out: m['_t']=dtf(m.get('ts'))
    out=[m for m in out if m['_t']]
    out.sort(key=lambda m:m['_t'])
    return out
def state(ms,cutoff):
    boards=[];nout=0;nin=0;errs=0;reun=False;hum=False;flux=False
    for m in ms:
        if m['_t']>cutoff: break
        c=mcontent(m); t=m.get('type') or ''
        if c.startswith('Moved to board:'):
            b=c.replace('Moved to board:','').replace('***','').strip(); boards.append(b)
            if 'Reuni' in b: reun=True
            if 'ATENDIMENTO HUMANO' in b: hum=True
            if 'FLUXOGRAMA' in b: flux=True
        if 'WhatsApp Error' in c: errs+=1
        if t=='in': nin+=1
        elif t=='out': nout+=1
    crm=boards[-1] if boards else 'LEAD ENTROU NO COMERCIAL'
    return dict(crm=crm,boards=boards,nout=nout,nin=nin,errs=errs,reun=reun,hum=hum,flux=flux)
def resumo(ns, s):
    ms=get_messages(ns)
    if not ms: return None
    t0=ms[0]['_t']
    perf,cid=perfil(s)
    orig=ORIG.get((s.get('opted_in_through') or '').lower() if s else '', (s.get('opted_in_through') if s else '') or 'lead')
    def at(d): return datetime.datetime.combine(t0.date()+datetime.timedelta(days=d), datetime.time(23,59,59))
    st1=state(ms,at(1))
    cab=f"Lead de {orig}"+(f" ({cid})" if cid else "")+(f"; {perf}." if perf else ".")
    if st1['nin']==0: acao=f"Recebeu abertura + {max(st1['nout']-1,0)} follow-up(s); nao respondeu."
    else:
        acao=f"Respondeu ({st1['nin']}x)"
        acao+=(" e teve reuniao agendada." if st1['reun'] else (" e chegou ao atendimento humano." if st1['hum'] else (" no fluxograma." if st1['flux'] else ".")))
    al=f" {st1['errs']} falha(s) de entrega." if st1['errs'] else ""
    r24=f"{cab} {acao} CRM: {st1['crm']}.{al}".strip()
    cells=[r24]; prev=st1
    for d in (7,15,30):
        stx=state(ms,at(d)); nel=at(d).date()>TODAY; ate=at(d).strftime('%d/%m/%Y')
        novos=[b for b in stx['boards'] if b not in prev['boards']]
        if novos: txt=f"Avancou para {novos[-1]} (CRM atual)."
        elif stx['nin']>prev['nin']: txt=f"Lead respondeu (+{stx['nin']-prev['nin']}); CRM: {stx['crm']}."
        else: txt=("Janela ainda nao decorrida; " if nel else f"Sem novas interacoes ate {ate}; ")+f"CRM: {stx['crm']}."
        if stx['errs']>prev['errs']: txt+=f" +{stx['errs']-prev['errs']} falha(s) de entrega."
        cells.append(txt[:250]); prev=stx
    return [c[:250] for c in cells]

def col_letter(i):
    s=''; i+=1
    while i: i,r=divmod(i-1,26); s=chr(65+r)+s
    return s

# ---- 2/3/4) por aba: ler, casar, resumir, escrever ----
cache={}  # ns -> cells
total_cells=0
for tab in TABS:
    try:
        vals=sheets.values().get(spreadsheetId=SPREADSHEET_ID, range="'%s'!A1:AZ"%tab).execute().get('values',[])
    except Exception as e:
        log('[%s] erro ao ler: %s'%(tab,e)); continue
    if not vals: log('[%s] vazia'%tab); continue
    header=[h.strip().upper() for h in vals[0]]
    def find(*names):
        for i,h in enumerate(header):
            for nm in names:
                if nm in h: return i
        return None
    id_col=find('ATENDE DIREITO ID'); tel_col=find('TELEFONE'); res_col=find('RESUMO APÓS 24H','RESUMO APOS 24H')
    if res_col is None: log('[%s] sem coluna RESUMO; pulando'%tab); continue
    out_rows=[]
    for r in vals[1:]:
        ns=None
        if id_col is not None and id_col<len(r) and str(r[id_col]).startswith('f175863u'): ns=r[id_col].strip()
        elif tel_col is not None and tel_col<len(r):
            s=by_key.get(phone_key(r[tel_col])); ns=s.get('user_ns') if s else None
        if not ns: out_rows.append(['','','','']); continue
        if ns in cache: out_rows.append(cache[ns]); continue
        try:
            cells=resumo(ns, by_ns.get(ns))
        except Exception as e:
            cells=None; log('   aviso ns %s: %s'%(ns,e))
        if not cells: cells=['Lead sem conversa baixada / nao localizado na API.','—','—','—']
        cache[ns]=cells; out_rows.append(cells)
    rng="'%s'!%s2"%(tab, col_letter(res_col))
    try:
        rsp=sheets.values().update(spreadsheetId=SPREADSHEET_ID, range=rng, valueInputOption='RAW', body={'values':out_rows}).execute()
        upd=rsp.get('updatedCells',0); total_cells+=upd
        log('[%s] %d linhas escritas em %s (%d celulas).'%(tab,len(out_rows),col_letter(res_col)+'2',upd))
    except Exception as e:
        log('[%s] ERRO ao escrever: %s'%(tab,e))
log('\nConcluido em %s. Total de celulas: %d. Leads analisados: %d.'%(datetime.datetime.now().strftime('%d/%m %H:%M'), total_cells, len(cache)))
