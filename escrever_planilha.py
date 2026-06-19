# Escreve os resumos nas abas da planilha via Google Sheets API (conta de servico).
# Pre-requisitos:
#   - gcred.json (chave da conta de servico) na MESMA pasta deste script.
#   - planilha compartilhada (Editor) com o e-mail da conta de servico.
#   - blocos gerados pelo Claude em entrada/api/: paste_M2_Pn.tsv, paste_GOOGLE.tsv,
#     paste_ORGANICO.tsv, paste_REUNIOES.tsv, paste_MANYCHAT.tsv
# Instale uma vez: pip install google-auth google-api-python-client

import os, sys, csv
ROOT = os.path.dirname(os.path.abspath(__file__))
API = os.path.join(ROOT, 'entrada', 'api')
SPREADSHEET_ID = '1BodcfEOso5pooeOSnA2Gq-OJVQtVcjleIEAfjvwM5IM'

# aba -> (arquivo do bloco, celula inicial). Nomes EXATOS das abas (com acento).
ALVOS = {
    'CAMPANHA META':            ('paste_M2_Pn.tsv', 'M2'),
    'CAMPANHA GOOGLE':          ('paste_GOOGLE.tsv', 'G2'),
    'ORGÂNICO':                 ('paste_ORGANICO.tsv', 'G2'),
    'REUNIÕES & FECHAMENTOS':   ('paste_REUNIOES.tsv', 'V2'),
    'MANYCHAT':                 ('paste_MANYCHAT.tsv', 'F2'),
}

try:
    from google.oauth2.service_account import Credentials
    from googleapiclient.discovery import build
except Exception:
    print("Faltam bibliotecas. Rode uma vez:")
    print("   pip install google-auth google-api-python-client")
    input("Enter para sair..."); sys.exit(1)

cred_path = os.path.join(ROOT, 'gcred.json')
if not os.path.exists(cred_path):
    print("ERRO: nao encontrei gcred.json nesta pasta.")
    print("Crie a conta de servico e salve a chave como gcred.json aqui.")
    input("Enter para sair..."); sys.exit(1)

creds = Credentials.from_service_account_file(cred_path, scopes=['https://www.googleapis.com/auth/spreadsheets'])
svc = build('sheets', 'v4', credentials=creds, cache_discovery=False)
values_api = svc.spreadsheets().values()

def col_to_idx(c):
    i=0
    for ch in c: i=i*26+(ord(ch.upper())-64)
    return i-1

total=0
for aba,(arq,cel) in ALVOS.items():
    p=os.path.join(API,arq)
    if not os.path.exists(p):
        print(f"[pular] {aba}: bloco {arq} nao encontrado."); continue
    rows=[]
    with open(p,encoding='utf-8') as f:
        for line in f.read().split('\n'):
            rows.append(line.split('\t'))
    # range: 'ABA'!CEL  (a API expande conforme o tamanho dos valores)
    rng = f"'{aba}'!{cel}"
    body={'values':rows}
    try:
        r=values_api.update(spreadsheetId=SPREADSHEET_ID, range=rng,
                            valueInputOption='RAW', body=body).execute()
        upd=r.get('updatedCells',0); total+=upd
        print(f"[ok] {aba}: {len(rows)} linhas escritas a partir de {cel} ({upd} celulas).")
    except Exception as e:
        print(f"[ERRO] {aba}: {e}")

print(f"\nConcluido. Total de celulas atualizadas: {total}")
input("Enter para fechar...")
