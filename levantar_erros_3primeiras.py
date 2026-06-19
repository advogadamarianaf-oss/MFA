# -*- coding: utf-8 -*-
# Levanta TODOS os leads cujo erro de envio ocorreu nas 3 PRIMEIRAS mensagens enviadas.
# Roda na maquina (precisa de MINHA_API_KEY no .env). Reaproveita conversas ja baixadas
# em entrada\api\messages e salva as novas (retomavel). Gera CSV em ErrorLeads\.
# Versao robusta: registra qualquer erro em ErrorLeads\erro_log.txt e nao fecha sozinho.
import os, sys, re, json, time, csv, datetime, traceback, urllib.request, urllib.error

ROOT = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(ROOT, "ErrorLeads"); os.makedirs(OUTDIR, exist_ok=True)
LOG = os.path.join(OUTDIR, "erro_log.txt")
MSGDIR = os.path.join(ROOT, "entrada", "api", "messages"); os.makedirs(MSGDIR, exist_ok=True)
OUT = os.path.join(OUTDIR, "leads_erro_3primeiras_COMPLETO.csv")
BASE = "https://app.atendedireito.com.br/api"

def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    try:
        with open(LOG, "a", encoding="utf-8") as f: f.write(msg + "\n")
    except Exception: pass

def main():
    # ---- chave do .env ----
    key = None
    envf = os.path.join(ROOT, ".env")
    if os.path.exists(envf):
        for line in open(envf, encoding="utf-8", errors="ignore"):
            m = re.match(r"\s*MINHA_API_KEY\s*=\s*(.+?)\s*$", line)
            if m: key = m.group(1).strip().strip('"').strip("'")
    if not key:
        log("ERRO: MINHA_API_KEY ausente no .env"); return

    HDRS = {
        "Authorization": "Bearer " + key,
        "Accept": "application/json",
        "Accept-Language": "pt-BR,pt;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    }
    def api(path):
        req = urllib.request.Request(BASE + path, headers=HDRS)
        for t in range(4):
            try:
                with urllib.request.urlopen(req, timeout=40) as r: return json.load(r)
            except urllib.error.HTTPError as e:
                if e.code in (403, 429) and t < 3:
                    time.sleep(3.0 * (t + 1))  # backoff em caso de Cloudflare/rate-limit
                    continue
                raise
            except Exception:
                if t == 3: raise
                time.sleep(1.5)

    def parse_err(c):
        code = re.search(r'"code":(\d+)', c or ""); title = re.search(r'"title":"([^"]+)"', c or "")
        return (code.group(1) if code else ""), (title.group(1) if title else (c or "")[:60])
    def is_err(m):
        c = m.get("content") or ""
        return m.get("msg_type") == "error" or (isinstance(c, str) and "WhatsApp Error" in c)

    def fetch_msgs(ns):
        p = os.path.join(MSGDIR, ns + ".json")
        if os.path.exists(p):
            try: return json.load(open(p, encoding="utf-8")).get("messages", [])
            except Exception: pass
        out = []; page = 1; last = 1
        while page <= last:
            try:
                r = api("/subscriber/chat-messages?user_ns=%s&include_bot=1&include_system=1&include_note=1&limit=100&page=%d" % (ns, page))
            except Exception:
                return None
            out += r.get("data", [])
            try: last = int(r["meta"]["last_page"])
            except Exception: last = 1
            page += 1; time.sleep(0.05)
        try: json.dump({"user_ns": ns, "messages": out}, open(p, "w", encoding="utf-8"), ensure_ascii=False)
        except Exception: pass
        return out

    def qualifica(ms):
        ms = [m for m in ms if m.get("ts")]; ms.sort(key=lambda m: int(m["ts"]))
        oc = 0
        for m in ms:
            if m.get("type") == "out":
                oc += 1
                if oc > 3: break
            if is_err(m) and 1 <= oc <= 3:
                code, motivo = parse_err(m.get("content") or "")
                return {"EnvioQueFalhou": oc, "CodigoErro": code, "Motivo": motivo,
                        "DataDoErro": datetime.datetime.fromtimestamp(int(m["ts"])).strftime("%d/%m/%Y %H:%M")}
        return None

    cols = ["Nome", "Telefone", "user_ns", "Canal", "EnvioQueFalhou", "CodigoErro", "Motivo", "DataDoErro"]
    def flush(rows):
        with open(OUT, "w", encoding="utf-8-sig", newline="") as fp:
            w = csv.DictWriter(fp, fieldnames=cols); w.writeheader()
            w.writerows(sorted(rows, key=lambda r: (r["EnvioQueFalhou"], r["Nome"])))

    log("=== inicio %s ===" % datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
    log("Baixando lista de subscribers (todos os leads)...")
    p1 = api("/subscribers?limit=100&page=1")
    last = int(p1["meta"]["last_page"]); subs = list(p1["data"])
    for pg in range(2, last + 1):
        subs += api("/subscribers?limit=100&page=%d" % pg)["data"]; time.sleep(0.05)
        if pg % 10 == 0: log("  subscribers %d/%d" % (pg, last))
    log("Total de leads: %d" % len(subs))

    rows = []; n = 0
    for s in subs:
        ns = s.get("user_ns")
        if not ns: continue
        n += 1
        try:
            ms = fetch_msgs(ns)
        except Exception as e:
            ms = None; log("  aviso ns %s: %s" % (ns, e))
        if ms:
            q = qualifica(ms)
            if q:
                rows.append({"Nome": s.get("name") or s.get("first_name") or "", "Telefone": s.get("phone") or "",
                             "user_ns": ns, "Canal": s.get("channel") or "", **q})
        if n % 50 == 0:
            log("  %d/%d (encontrados: %d)" % (n, len(subs), len(rows)))
            flush(rows)
    flush(rows)
    log("\n== PRONTO ==")
    log("Leads com erro nas 3 primeiras mensagens: %d de %d" % (len(rows), len(subs)))
    log("Arquivo: ErrorLeads\\leads_erro_3primeiras_COMPLETO.csv")

try:
    main()
except Exception:
    log("ERRO FATAL:\n" + traceback.format_exc())
input("\nPressione Enter para fechar...")
