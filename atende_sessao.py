"""Sessão logada no Atende Direito SEM navegador (substitui o Claude in Chrome).

Faz login com ATENDE_EMAIL / ATENDE_SENHA do .env e chama as mesmas rotas internas
que o window.axios do site usa. Serve para o que a API pública (Bearer) não faz:
ler/mover a coluna do board "CRM - Comercial" (f175863) e tirar o snapshot do dashboard.

Uso:
  python atende_sessao.py testar                  -> login + lista as colunas do board (não altera nada)
  python atende_sessao.py snapshot                -> grava docs/dashboard/crm_snapshot.json
                                                     (colunas + todos os leads com origem e data de entrada)
  python atende_sessao.py planilha                -> baixa a aba REUNIÕES & FECHAMENTOS -> planilha_reunioes.json
  python atende_sessao.py telefone <numero>       -> resolve telefone -> user_ns (f175863)
  python atende_sessao.py coluna <user_ns>        -> mostra a coluna atual do lead
  python atende_sessao.py mover <arquivo.json>    -> move leads de coluna (só AVANÇA; nunca rebaixa)

Formato do arquivo de "mover": lista de objetos
  [{"user_ns": "f175863u...", "coluna": "<board_column_ns OU nome da coluna>", "nome": "...", "nota": "..."}]
("board_column_ns" também é aceito no lugar de "coluna"; "nome" e "nota" são opcionais.)
O resultado vai para mover_resultado.json e um resumo é impresso no fim.
"""
import requests, os, json, time, sys, re, csv, io
from datetime import datetime, timezone
from urllib.parse import unquote
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

SITE = 'https://app.atendedireito.com.br'
SD = os.path.dirname(os.path.abspath(__file__))
TEAM_ID, FLOW_NS, BOARD_ID, BOARD_NAME = 183919, 'f175863', 2568, 'CRM - Comercial'
PLANILHA_ID, PLANILHA_GID = '1BodcfEOso5pooeOSnA2Gq-OJVQtVcjleIEAfjvwM5IM', '1366528886'
PAUSA = 0.3

keys = {}
for line in open(os.path.join(SD, '.env'), encoding='utf-8-sig'):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        keys[k.strip()] = v.strip().strip('"').strip("'")

# --- Ordem do funil (sufixo do board_column_ns -> rank). Maior = mais avançado. ---
# CL = Clientes (protegida: quem está lá não sai), X = terminal negativo, ERR = mensagens com erro.
PREFIXO = 'f175863bd70851bn'
RANK = {
    '1202717': 10,     # LEAD NÃO RESPONDEU PRIMEIRO CONTATO
    '1202719': 20,     # LEAD EM ATENDIMENTO
    '1499221': 30,     # LEAD QUALIFICADO
    '1368945': 40,     # Reunião Agendada - ASSESSORIA
    '1369937': 40,     # Reunião Agendada - DEFESA
    '833693':  45,     # LEAD NÃO Compareceu à REUNIÃO
    '1542297': 50,     # LEAD compareceu a reunião aguardando fechamento
    '1803675': 'CL',   # Clientes
    '871983':  60,     # Contrato Assinado
    '1369051': 60,     # Contrato Assinado - ASSESSORIA
    '1369149': 60,     # Contrato Assinado - DEFESA
    '551149':  'X',    # Lead Desqualificado
    '781291':  'X',    # Contato Encerrado - Lead recusou
    '1797409': 'ERR',  # MENSAGENS COM ERRO
}
RANK_CLIENTES_COMO_DESTINO = 55


def sufixo(ns):
    return ns[len(PREFIXO):] if ns and ns.startswith(PREFIXO) else None


def rank(ns):
    return RANK.get(sufixo(ns))


def chave_nome(nome):
    """Nome de coluna comparável: ignora maiúsculas, espaços extras e os ' ***' do board."""
    return re.sub(r'[\s*]+', ' ', nome or '').strip().lower()


# --------------------------------------------------------------------------- sessão

class Sessao:
    def __init__(self):
        self.s = requests.Session()
        self.s.headers['User-Agent'] = ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                        '(KHTML, like Gecko) Chrome/130.0 Safari/537.36')
        self.login()

    def login(self):
        email, senha = keys.get('ATENDE_EMAIL'), keys.get('ATENDE_SENHA')
        if not email or not senha:
            sys.exit('ERRO: faltam ATENDE_EMAIL e/ou ATENDE_SENHA no .env (pasta Analise de Mensagens).')
        r = self.s.get(f'{SITE}/login', timeout=30)
        m = re.search(r'name="_token"\s+value="([^"]+)"', r.text)
        if not m:
            sys.exit(f'ERRO: página de login mudou (sem _token). HTTP {r.status_code}.')
        r = self.s.post(f'{SITE}/login', timeout=30, allow_redirects=True,
                        data={'_token': m.group(1), 'email': email, 'password': senha, 'remember': 'on'})
        final = r.url.lower()
        if any(p in final for p in ('two-factor', '2fa', 'otp', 'verify', 'confirm')):
            sys.exit(f'ERRO: o login pediu verificação extra ({r.url}). O login automático não consegue passar disso.')
        if final.rstrip('/').endswith('/login'):
            sys.exit('ERRO: login recusado (e-mail/senha errados, ou a conta só entra pelo Google).')

    def _headers(self):
        return {'X-XSRF-TOKEN': unquote(self.s.cookies.get('XSRF-TOKEN', '')),
                'X-Requested-With': 'XMLHttpRequest', 'Accept': 'application/json',
                'x-sub-flow-ns': 'main', 'x-flow-ns': FLOW_NS, 'x-team-id': str(TEAM_ID)}

    def req(self, metodo, rota, **kw):
        """Chamada autenticada. 419 (CSRF) ou 401 -> refaz o login uma vez; erro de rede -> 1 retry."""
        for tentativa in range(2):
            try:
                r = self.s.request(metodo, SITE + rota, headers=self._headers(), timeout=30, **kw)
            except requests.RequestException:
                if tentativa:
                    raise
                time.sleep(2)
                continue
            if r.status_code in (401, 419) and not tentativa:
                self.login()
                continue
            if 'text/html' in r.headers.get('content-type', '') and '/login' in r.url:
                if tentativa:
                    sys.exit('ERRO: sessão caiu e o novo login não resolveu.')
                self.login()
                continue
            time.sleep(PAUSA)
            return r
        return r

    def json(self, metodo, rota, **kw):
        r = self.req(metodo, rota, **kw)
        r.raise_for_status()
        j = r.json()
        return j.get('data', j) if isinstance(j, dict) else j

    # --- leituras / escrita do board ---

    def colunas_vivas(self):
        d = self.json('GET', '/flowbuilder/flow-detail-live-chat')
        b = next(b for b in d['flow_boards'] if (b.get('board_name') or b.get('name')) == BOARD_NAME)
        return [{'nome': c.get('board_column_name') or c.get('name'), 'ns': c.get('board_column_ns') or c.get('ns')}
                for c in b['board_columns']]

    def coluna_atual(self, user_ns):
        d = self.json('GET', '/flowbuilder/bot-user', params={'user_ns': user_ns})
        return (d.get('board_column') or {}).get('board_column_ns')

    def patch_coluna(self, user_ns, coluna_ns, nota):
        # note_action PRECISA ser 'update' ('no_change' devolve 204 e não aplica).
        return self.req('PATCH', '/flowbuilder/edit-item', json={
            'type': 'user_board_column',
            'obj': {'user_ns': user_ns, 'board_column_ns': coluna_ns,
                    'note': nota, 'note_action': 'update', 'note_type': 'success'}})

    def buscar_telefone(self, numero):
        d = re.sub(r'\D', '', numero)
        if d.startswith('55') and len(d) >= 12:
            d = d[2:]
        variantes = [d]
        if len(d) == 10:
            variantes.append(d[:2] + '9' + d[2:])
        elif len(d) == 11 and d[2] == '9':
            variantes.append(d[:2] + d[3:])
        for v in variantes:
            payload = {'page': 1, 'limit': 10, 'search': v, 'sort': '-last_message_at', 'status': '',
                       'filter': 'all', 'channel': '', 'channel_id': '', 'conditions': [], 'agent_group_id': 0,
                       'label_id': 0, 'board_column_ns': '', 'lead_source': '', 'lead_status': '',
                       'department': '', 'interest': '', 'market': '', 'is_unreplied': 0, 'include_stats': 1}
            d2 = self.json('POST', '/flowbuilder/chat-rooms', json=payload)
            rooms = d2.get('rooms') if isinstance(d2, dict) else None
            if rooms:
                return rooms[0].get('roomId'), v
        return None, None


# --------------------------------------------------------------------------- regra "nunca rebaixar"

def decidir(atual, nova):
    """Retorna (mover?, motivo)."""
    ra, rn = rank(atual), rank(nova)
    if rn is None:
        return False, 'coluna destino fora do mapa'
    if rn == 'ERR':
        return False, 'destino MENSAGENS COM ERRO não é permitido'
    if atual == nova:
        return False, 'já está nessa coluna'
    if atual and ra is None:
        return False, 'coluna atual fora do mapa (conferência humana)'
    if ra in ('CL', 'ERR'):
        return False, 'coluna atual protegida (Clientes / Mensagens com erro)'
    if rn == 'X':
        if ra in (50, 60):
            return False, 'destino negativo sobre lead avançado (conferência humana)'
        if ra == 'X':
            return False, 'já está em coluna terminal'
        return True, 'saída do funil'
    alvo = RANK_CLIENTES_COMO_DESTINO if rn == 'CL' else rn
    base = 0 if (ra is None or ra == 'X') else ra
    if alvo > base:
        return True, 'avança no funil'
    return False, 'já em etapa igual ou mais avançada (não rebaixa)'


# --------------------------------------------------------------------------- comandos

def cmd_testar(ses):
    cols = ses.colunas_vivas()
    print(f'LOGIN OK. Board "{BOARD_NAME}": {len(cols)} colunas')
    for c in cols:
        r = rank(c['ns'])
        print(f'  {str(r) if r is not None else "?? fora do mapa":>15}  {c["nome"]}')
    vivas = {sufixo(c['ns']) for c in cols}
    sumidas = [s for s in RANK if s not in vivas]
    if sumidas:
        print('ATENÇÃO: colunas do mapa que não existem mais no board:', ', '.join(sumidas))


# --------------------------------------------------------------------------- snapshot (board + origem + leads)

ORIGENS = {'meta': 'Meta Ads', 'google': 'Google Ads', 'organico': 'WhatsApp orgânico', 'site': 'Site',
           'instagram': 'Instagram', 'manual': 'Cadastro manual'}
REGRA_ORIGEM = ('google: campanha com "GOOGLE" | meta: rótulo META, opt-in lead_ads, traffic_type=ad ou campanha preenchida | '
                'site: rótulo SITE | instagram: canal Instagram ou rótulo CONTATO/CAMPANHA INSTAGRAM | '
                'manual: opt-in manual | organico: o resto (WhatsApp direto / webhook sem rótulo de mídia)')
LABELS_INSTAGRAM = {'CONTATO INSTAGRAM', 'CAMPANHA - CAPTAÇÃO - INSTAGRAM'}


def classificar_origem(u, labels, extra):
    nomes = {labels.get(l.get('label_id'), '') for l in (u.get('bot_user_labels') or [])}
    camp = (extra.get('campanha') or '').upper()
    opt = u.get('opt_in_through') or ''
    if 'GOOGLE' in camp:
        return 'google'
    if 'META' in nomes or opt == 'lead_ads' or extra.get('traffic_type') == 'ad' or camp:
        return 'meta'
    if 'SITE' in nomes:
        return 'site'
    if u.get('channel') == 'instagram' or nomes & LABELS_INSTAGRAM:
        return 'instagram'
    if opt == 'manual':
        return 'manual'
    return 'organico'


def mascarar_nome(u):
    partes = (u.get('user_name') or u.get('first_name') or '').split()
    if not partes:
        return '(sem nome)'
    return partes[0] + (f' {partes[-1][0]}.' if len(partes) > 1 else '')


def mascarar_telefone(tel):
    d = re.sub(r'\D', '', tel or '')
    if d.startswith('55') and len(d) >= 12:
        d = d[2:]
    return f'({d[:2]}) •••••-{d[-4:]}' if len(d) >= 8 else ''


def colunas_completas(ses):
    """Board com TODOS os leads de cada coluna (a view só traz os 50 primeiros; o resto vem paginado)."""
    d = ses.json('GET', f'/flowbuilder/bot-boards/view/{BOARD_ID}')
    cols = d if isinstance(d, list) else list(d.values())
    for c in cols:
        users = list(c.get('bot_users') or [])
        vistos = {u['user_ns'] for u in users}
        page = 1
        while c.get('has_more') and len(users) < c['bot_user_board_columns_count']:
            page += 1
            r = ses.req('POST', '/flowbuilder/bot-boards/load-column-bot-users',
                        json={'board_column_ns': c['board_column_ns'], 'page': page})
            r.raise_for_status()
            j = r.json()
            lote = j.get('data', j) if isinstance(j, dict) else j
            meta = j.get('meta') if isinstance(j, dict) else None
            if not lote:
                break
            for u in lote:
                if u['user_ns'] not in vistos:
                    vistos.add(u['user_ns'])
                    users.append(u)
            if (meta and meta.get('last_page') and page >= meta['last_page']) or (not meta and len(lote) < 50):
                break
        c['bot_users'] = users
    return cols


def campos_rest():
    """user_ns -> campos de campanha (campanha, traffic_type, criativo, conjunto) via API pública. Opcional."""
    key = keys.get('MINHA_API_KEY')
    if not key:
        print('AVISO: sem MINHA_API_KEY no .env; origem sem os campos de campanha.')
        return {}
    out, page = {}, 1
    try:
        while True:
            r = requests.get(f'{SITE}/api/subscribers', params={'limit': 100, 'page': page},
                             headers={'Authorization': 'Bearer ' + key}, timeout=60)
            r.raise_for_status()
            j = r.json()
            for u in j.get('data', []):
                f = {x.get('name'): (x.get('value') or '') for x in (u.get('user_fields') or [])}
                out[u['user_ns']] = {'campanha': f.get('campanha', ''), 'traffic_type': f.get('traffic_type', ''),
                                     'criativo': f.get('Criativo', ''), 'conjunto': f.get('Conjunto', '')}
            if page >= (j.get('meta') or {}).get('last_page', page):
                break
            page += 1
            time.sleep(0.2)
    except Exception as e:
        print(f'AVISO: API pública falhou na página {page} ({e}); origem sem os campos de campanha.')
    return out


def cmd_snapshot(ses):
    fd = ses.json('GET', '/flowbuilder/flow-detail-live-chat')
    labels = {l['id']: l['name'] for l in fd.get('team_labels', [])}
    cols = colunas_completas(ses)
    extras = campos_rest()
    arr, leads = [], []
    for c in sorted(cols, key=lambda c: c['display_order']):
        arr.append({'order': c['display_order'], 'name': c['name'], 'ns': c['board_column_ns'],
                    'total': c['bot_user_board_columns_count']})
        for u in c['bot_users']:
            ex = extras.get(u['user_ns'], {})
            leads.append({'ns': u['user_ns'], 'nome': mascarar_nome(u), 'tel': mascarar_telefone(u.get('phone')),
                          'origem': classificar_origem(u, labels, ex),
                          'criado': (u.get('created_at') or u.get('subscribed_at') or '')[:16],
                          'ultima': (u.get('last_message_at') or '')[:16],
                          'ult_tipo': u.get('last_message_type') or '',
                          'col': c['display_order'], 'campanha': (ex.get('campanha') or '')[:80]})
    # Um lead movido de coluna durante a coleta pode aparecer duas vezes: fica a ultima ocorrencia.
    leads = list({l['ns']: l for l in leads}.values())
    leads.sort(key=lambda l: l['criado'], reverse=True)
    total = sum(c['total'] for c in arr)
    por_origem = {k: sum(1 for l in leads if l['origem'] == k) for k in ORIGENS}
    snap = {'updated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.000Z'), 'board_id': BOARD_ID,
            'board_name': BOARD_NAME, 'flow_ns': FLOW_NS, 'total': total, 'columns': arr,
            'origens': ORIGENS, 'regra_origem': REGRA_ORIGEM, 'por_origem': por_origem,
            'leads_total': len(leads), 'leads': leads}
    destino = os.path.join(SD, 'docs', 'dashboard', 'crm_snapshot.json')
    with open(destino, 'w', encoding='utf-8') as f:
        json.dump(snap, f, ensure_ascii=False, separators=(',', ':'))
    if abs(len(leads) - total) > 5:
        print(f'AVISO: board soma {total} leads, mas foram listados {len(leads)} (paginação incompleta?).')
    elif len(leads) != total:
        print(f'(board soma {total}, listados {len(leads)}: algum lead mudou de coluna durante a coleta)')
    resumo = ', '.join(f'{ORIGENS[k]} {v}' for k, v in sorted(por_origem.items(), key=lambda x: -x[1]) if v)
    print(f'SNAPSHOT OK: {total} leads em {len(arr)} colunas ({len(leads)} detalhados; {resumo}) -> {destino}')

def cmd_planilha():
    url = (f'https://docs.google.com/spreadsheets/d/{PLANILHA_ID}/gviz/tq'
           f'?gid={PLANILHA_GID}&tqx=out:csv')
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    linhas = list(csv.reader(io.StringIO(r.content.decode('utf-8'))))
    cab = [h.strip().rstrip(':').strip().upper() for h in linhas[0]]

    def idx(nome):
        if nome not in cab:
            sys.exit(f'ERRO: coluna {nome} não encontrada no cabeçalho: {cab}')
        return cab.index(nome)
    i_nome, i_tel = idx('NOME'), idx('TELEFONE')
    i_comp, i_fech, i_orig = idx('COMPARECEU?'), idx('FECHOU?'), idx('ORIGEM')
    saida = []
    for l in linhas[1:]:
        l += [''] * (len(cab) - len(l))
        if not (l[i_nome].strip() or l[i_tel].strip()):
            continue
        saida.append({'nome': l[i_nome].strip(), 'telefone': l[i_tel].strip(), 'compareceu': l[i_comp].strip(),
                      'fechou': l[i_fech].strip(), 'origem': l[i_orig].strip()})
    destino = os.path.join(SD, 'planilha_reunioes.json')
    with open(destino, 'w', encoding='utf-8') as f:
        json.dump(saida, f, ensure_ascii=False, indent=1)
    print(f'PLANILHA OK: {len(saida)} linhas -> {destino}')


def cmd_telefone(ses, numero):
    user_ns, variante = ses.buscar_telefone(numero)
    print(json.dumps({'telefone': numero, 'user_ns': user_ns, 'achado_como': variante}, ensure_ascii=False))


def cmd_coluna(ses, user_ns):
    ns = ses.coluna_atual(user_ns)
    nomes = {c['ns']: c['nome'] for c in ses.colunas_vivas()}
    print(json.dumps({'user_ns': user_ns, 'coluna': nomes.get(ns, ns), 'rank': rank(ns)}, ensure_ascii=False))


def cmd_mover(ses, arquivo):
    itens = json.load(open(arquivo, encoding='utf-8-sig'))
    cols = ses.colunas_vivas()
    por_nome = {chave_nome(c['nome']): c['ns'] for c in cols}
    nomes = {c['ns']: c['nome'] for c in cols}
    agora = datetime.now().strftime('%d/%m/%Y %H:%M')
    resultado = []
    for it in itens:
        user_ns = it['user_ns']
        alvo = it.get('coluna') or it.get('board_column_ns') or ''
        nova = alvo if alvo in nomes else por_nome.get(chave_nome(alvo))
        reg = {'user_ns': user_ns, 'nome': it.get('nome', ''), 'de': None, 'para': nomes.get(nova, alvo)}
        if not nova:
            reg.update(acao='erro', motivo=f'coluna "{alvo}" não existe no board')
            resultado.append(reg)
            continue
        try:
            atual = ses.coluna_atual(user_ns)
        except Exception as e:
            reg.update(acao='erro', motivo=f'não consegui ler o lead: {e}')
            resultado.append(reg)
            continue
        reg['de'] = nomes.get(atual, atual)
        mover, motivo = decidir(atual, nova)
        if not mover:
            reg.update(acao='mantido', motivo=motivo)
        else:
            r = ses.patch_coluna(user_ns, nova, it.get('nota') or f'Classificado pela IA em {agora}')
            # 204 não prova nada: confirma relendo.
            confirmado = r.status_code < 300 and ses.coluna_atual(user_ns) == nova
            reg.update(acao='movido' if confirmado else 'erro',
                       motivo=motivo if confirmado else f'PATCH HTTP {r.status_code}, coluna não mudou')
        resultado.append(reg)
        print(f'{reg["acao"]:8} {reg["nome"] or user_ns}: {reg["de"]} -> {reg["para"]} ({reg["motivo"]})')
    with open(os.path.join(SD, 'mover_resultado.json'), 'w', encoding='utf-8') as f:
        json.dump(resultado, f, ensure_ascii=False, indent=1)
    cont = {a: sum(1 for x in resultado if x['acao'] == a) for a in ('movido', 'mantido', 'erro')}
    print(f'RESUMO: {cont["movido"]} movidos, {cont["mantido"]} mantidos, {cont["erro"]} erros -> mover_resultado.json')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd, args = sys.argv[1], sys.argv[2:]
    if cmd == 'planilha':
        cmd_planilha()
        sys.exit()
    comandos = {'testar': cmd_testar, 'snapshot': cmd_snapshot, 'telefone': cmd_telefone,
                'coluna': cmd_coluna, 'mover': cmd_mover}
    if cmd not in comandos:
        sys.exit(__doc__)
    comandos[cmd](Sessao(), *args)
