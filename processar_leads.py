import os, re, json, time, requests, urllib3, openpyxl
from datetime import datetime
urllib3.disable_warnings()

# Config
BASE = 'https://app.atendedireito.com.br/api'
SPREADSHEET = r'C:\Users\Thiag\Downloads\RECLASSIFICAÇÃO DE LEADS.xlsx'
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), 'leads_processados.json')
TAG_NAME = 'CRM ALTERADO PELA IA'
LABEL_NAME = 'CRM ALTERADO PELA IA'

# CRM -> board_column_ns mapping
CRM_MAP = {
    'LEAD ENTROU NO COMERCIAL': 'f175863bd70851bn1499219',
    "LEAD NÃO DEU A 1ª RESPOSTA APÓS FOLLOW UP'S": 'f175863bd70851bn1202717',
    'LEAD EM ATENDIMENTO PELA IA LUISA': 'f175863bd70851bn1202719',
    'LEAD CHEGOU ATÉ O AGENDAMENTO PELA IA': 'f175863bd70851bn1499221',
    'REUNIÃO AGENDADA CLIENTES': 'f175863bd70851bn787133',
    'Reunião Agendada - ASSESSORIA': 'f175863bd70851bn1368945',
    'Reunião Agendada - DEFESA': 'f175863bd70851bn1369937',
    'LEAD NÃO Compareceu à REUNIÃO': 'f175863bd70851bn833693',
    'Aguardando Fechamento': 'f175863bd70851bn1542297',
    'FECHAMENTO': 'f175863bd70851bn1542299',
    'Contrato Assinado': 'f175863bd70851bn871983',
    'Contrato Assinado - ASSESSORIA': 'f175863bd70851bn1369051',
    'Contrato Assinado - DEFESA': 'f175863bd70851bn1369149',
    'Contrato Assinado - DOCUMENTOS': 'f175863bd70851bn1369215',
    'Lead Desqualificado': 'f175863bd70851bn551149',
    'Contato Encerrado - Lead recusou': 'f175863bd70851bn781291',
}

# Load API key
with open(os.path.join(os.path.dirname(__file__), '.env'), 'r') as f:
    for line in f:
        line = line.strip()
        if line.startswith('MINHA_API_KEY') and not line.startswith('MINHA_API_KEY2'):
            API_KEY = line.split('=', 1)[1].strip()
            break

HEADERS = {'Authorization': f'Bearer {API_KEY}'}

def clean_phone(phone_str):
    """Extract clean phone numbers from spreadsheet format."""
    if not phone_str:
        return []
    phones = []
    for part in phone_str.split(';'):
        digits = re.sub(r'[^\d+]', '', part.strip())
        if not digits.startswith('+'):
            digits = '+' + digits
        if len(digits) >= 12:
            phones.append(digits)
    return phones

def search_subscriber(phones, name):
    """Search subscriber by phone numbers, fallback to name."""
    for phone in phones:
        try:
            r = requests.get(f'{BASE}/subscribers', params={'phone': phone, 'limit': 5},
                           headers=HEADERS, verify=False, timeout=15)
            if r.status_code == 200:
                data = r.json().get('data', [])
                if data:
                    return data[0].get('user_ns'), data[0].get('first_name', '') + ' ' + (data[0].get('last_name', '') or '')
        except Exception as e:
            pass
        time.sleep(0.3)

    # Fallback: search by name
    if name:
        first_word = name.split()[0] if name else ''
        if len(first_word) > 2:
            try:
                r = requests.get(f'{BASE}/subscribers', params={'name': first_word, 'limit': 10},
                               headers=HEADERS, verify=False, timeout=15)
                if r.status_code == 200:
                    data = r.json().get('data', [])
                    for sub in data:
                        sub_name = (sub.get('first_name', '') + ' ' + (sub.get('last_name', '') or '')).strip().lower()
                        if name.lower() in sub_name or sub_name in name.lower():
                            return sub.get('user_ns'), sub_name
            except:
                pass
    return None, None

def add_tag(user_ns):
    """Add tag by name."""
    try:
        r = requests.post(f'{BASE}/subscriber/add-tag-by-name',
                         json={'user_ns': user_ns, 'tag_name': TAG_NAME},
                         headers=HEADERS, verify=False, timeout=15)
        return r.status_code
    except Exception as e:
        return str(e)

def add_label(user_ns):
    """Add label by name."""
    try:
        r = requests.post(f'{BASE}/subscriber/add-labels-by-name',
                         json={'user_ns': user_ns, 'data': [{'label_name': LABEL_NAME}]},
                         headers=HEADERS, verify=False, timeout=15)
        return r.status_code
    except Exception as e:
        return str(e)

def resolve_crm_column(crm_verdadeiro):
    """Find the board_column_ns for a CRM value."""
    if not crm_verdadeiro:
        return None
    cv = crm_verdadeiro.strip()
    if cv in CRM_MAP:
        return CRM_MAP[cv]
    for key, val in CRM_MAP.items():
        if key.lower() == cv.lower():
            return val
        if cv.lower() in key.lower() or key.lower() in cv.lower():
            return val
    return None

def main():
    wb = openpyxl.load_workbook(SPREADSHEET, read_only=True)
    ws = wb.active

    leads = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        num, nome, tel, canal, crm_atual, crm_verdadeiro, grupo, prioridade, confianca = row
        if num is not None and nome is not None and int(num) >= 21:
            leads.append({
                'num': int(num),
                'nome': nome.strip(),
                'tel': tel or '',
                'canal': canal or '',
                'crm_atual': crm_atual or '',
                'crm_verdadeiro': (crm_verdadeiro or '').strip(),
            })
    wb.close()

    print(f'=== Processando {len(leads)} leads ===')
    now = datetime.now().strftime('%d/%m/%Y às %H:%M')

    results = []
    found = 0
    not_found = 0
    tag_ok = 0
    label_ok = 0
    crm_pending = []

    for i, lead in enumerate(leads):
        num = lead['num']
        nome = lead['nome']
        phones = clean_phone(lead['tel'])
        crm_v = lead['crm_verdadeiro']
        board_col = resolve_crm_column(crm_v)

        # Search subscriber
        user_ns, found_name = search_subscriber(phones, nome)

        result = {
            'num': num,
            'nome': nome,
            'tel': lead['tel'],
            'crm_verdadeiro': crm_v,
            'board_column_ns': board_col,
            'user_ns': user_ns,
            'found_name': found_name,
            'tag_status': None,
            'label_status': None,
            'crm_status': 'pending' if board_col else 'no_column',
        }

        if user_ns:
            found += 1

            # Add tag
            ts = add_tag(user_ns)
            result['tag_status'] = ts
            if ts == 200:
                tag_ok += 1
            time.sleep(0.2)

            # Add label
            ls = add_label(user_ns)
            result['label_status'] = ls
            if ls == 200:
                label_ok += 1
            time.sleep(0.2)

            # Queue CRM change for browser
            if board_col:
                crm_pending.append({
                    'user_ns': user_ns,
                    'board_column_ns': board_col,
                    'note': f'Alterado pela IA em {now}',
                    'nome': nome,
                    'num': num
                })
        else:
            not_found += 1
            result['tag_status'] = 'not_found'
            result['label_status'] = 'not_found'
            result['crm_status'] = 'not_found'

        results.append(result)

        if (i + 1) % 10 == 0:
            print(f'[{i+1}/{len(leads)}] Encontrados: {found} | Não encontrados: {not_found} | Tags OK: {tag_ok} | Labels OK: {label_ok}')

        time.sleep(0.3)

    # Save results
    output = {
        'timestamp': now,
        'total': len(leads),
        'found': found,
        'not_found': not_found,
        'tag_ok': tag_ok,
        'label_ok': label_ok,
        'crm_pending': crm_pending,
        'results': results
    }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f'\n=== RESUMO ===')
    print(f'Total: {len(leads)}')
    print(f'Encontrados: {found}')
    print(f'Não encontrados: {not_found}')
    print(f'Tags aplicadas: {tag_ok}')
    print(f'Labels aplicadas: {label_ok}')
    print(f'CRM pendente (browser): {len(crm_pending)}')
    print(f'CRM sem coluna: {sum(1 for r in results if r["crm_status"] == "no_column")}')
    print(f'\nResultados salvos em: {OUTPUT_FILE}')

    # Print not found leads
    nf = [r for r in results if not r['user_ns']]
    if nf:
        print(f'\n=== Leads NÃO encontrados ({len(nf)}) ===')
        for r in nf:
            print(f'  #{r["num"]} {r["nome"]} | Tel: {r["tel"]}')

if __name__ == '__main__':
    main()
