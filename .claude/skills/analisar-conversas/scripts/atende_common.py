# -*- coding: utf-8 -*-
"""Nucleo da integracao com o Atende Direito.
Compartilhado por crm_adapter.py e chat_adapter.py.

Dois modos de dados:
  - LOCAL  : le os JSON ja baixados em <root>/entrada/api/{subscribers,messages}
  - LIVE   : bate na API (precisa de MINHA_API_KEY no .env)
Por padrao usa LOCAL se a pasta existir; senao cai pra LIVE.
Force com a env ATENDE_MODE=local|live.
"""
import os, re, json, time, glob, datetime, urllib.request

API_BASE = "https://app.atendedireito.com.br/api"

# ---------- raiz do projeto + .env ----------
def project_root():
    d = os.path.dirname(os.path.abspath(__file__))
    for _ in range(8):
        if os.path.exists(os.path.join(d, "CLAUDE.md")) or os.path.exists(os.path.join(d, ".env")):
            return d
        nd = os.path.dirname(d)
        if nd == d: break
        d = nd
    # fallback: 4 niveis acima (scripts -> analisar-conversas -> skills -> .claude -> root)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

ROOT = project_root()

def _load_env():
    envf = os.path.join(ROOT, ".env")
    if not os.path.exists(envf): return
    for line in open(envf, encoding="utf-8", errors="ignore"):
        m = re.match(r"\s*([A-Z_]+)\s*=\s*(.+?)\s*$", line)
        if m:
            k, v = m.group(1), m.group(2).strip().strip('"').strip("'")
            os.environ.setdefault(k, v)
_load_env()

API_KEY = os.environ.get("MINHA_API_KEY", "")

def _mode():
    forced = os.environ.get("ATENDE_MODE", "").lower()
    if forced in ("local", "live"): return forced
    if os.path.isdir(os.path.join(ROOT, "entrada", "api", "subscribers")):
        return "local"
    return "live"

MODE = _mode()

# ---------- API ----------
def api_get(path):
    url = API_BASE + path
    req = urllib.request.Request(url, headers={"Authorization": "Bearer " + API_KEY, "Accept": "application/json"})
    for tent in range(3):
        try:
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.load(r)
        except Exception:
            if tent == 2: raise
            time.sleep(1.0)

# ---------- normalizacao de telefone ----------
def digits(s): return re.sub(r"\D", "", str(s) if s is not None else "")
def phone_key(v):
    """Normaliza telefone p/ casar planilha (Excel salva como numero -> '...0') com o Atende.
    Tira '.0', tira pais 55, e usa DDD + ultimos 8 digitos (ignora 9o digito do celular)."""
    if v is None: return ""
    s = re.sub(r"\.0$", "", str(v))
    d = re.sub(r"\D", "", s)
    if d.startswith("55") and len(d) >= 12: d = d[2:]
    if len(d) < 10: return d
    return d[:2] + d[2:][-8:]

_NS_RE = re.compile(r"^f\d+u\d+$")
def is_ns(v): return bool(v and _NS_RE.match(str(v).strip()))

# ---------- subscribers ----------
_SUBS = None  # list
_BY_NS = None
_BY_KEY = None

def _load_subscribers_local():
    subs = []
    for f in sorted(glob.glob(os.path.join(ROOT, "entrada", "api", "subscribers", "*.json"))):
        try:
            d = json.load(open(f, encoding="utf-8"))
        except Exception:
            continue
        if isinstance(d, list): subs += d
        elif isinstance(d, dict) and "data" in d: subs += d["data"]
        elif isinstance(d, dict): subs.append(d)
    return subs

def _load_subscribers_live():
    p1 = api_get("/subscribers?limit=100&page=1")
    last = int(p1["meta"]["last_page"])
    subs = list(p1["data"])
    for pg in range(2, last + 1):
        subs += api_get("/subscribers?limit=100&page=%d" % pg)["data"]
        time.sleep(0.1)
    return subs

def subscribers():
    global _SUBS, _BY_NS, _BY_KEY
    if _SUBS is None:
        _SUBS = _load_subscribers_local() if MODE == "local" else _load_subscribers_live()
        _BY_NS = {s.get("user_ns"): s for s in _SUBS if s.get("user_ns")}
        _BY_KEY = {}
        for s in _SUBS:
            k = phone_key(s.get("phone"))
            if k: _BY_KEY.setdefault(k, s)
    return _SUBS

def sub_by_ns(ns):
    subscribers(); return _BY_NS.get(ns)

def ns_by_phone(phone):
    subscribers()
    s = _BY_KEY.get(phone_key(phone))
    return s.get("user_ns") if s else None

# ---------- mensagens ----------
_MEDIA_URLS = {}  # msg_id -> url

def iso_from_ts(ts):
    try:
        return datetime.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%dT%H:%M:%SZ")
    except Exception:
        return None

_TYPE_MAP = {
    "text": "chat", "wa_template": "chat", "button_template": "chat",
    "audio": "audio", "image": "image", "file": "document", "video": "video",
    "react": "react", "postback": "system", "action": "system",
    "error": "system", "feed": "system",
}

def _texto(m):
    p = m.get("payload") or {}
    mt = m.get("msg_type")
    if mt == "audio" and p.get("transcribed_text"):
        return p.get("transcribed_text")
    if mt == "wa_template":
        return p.get("body") or p.get("text") or (m.get("content") or None)
    return p.get("text") or (m.get("content") or None)

def normalizar(m):
    """Converte uma msg crua do Atende pro schema esperado pela skill."""
    t = m.get("type")            # in / out / agent / system / note
    mt = m.get("msg_type")       # text / audio / image / file / ...
    p = m.get("payload") or {}
    mid = str(m.get("id"))
    url = p.get("url")
    if url: _MEDIA_URLS[mid] = url
    skill_type = _TYPE_MAP.get(mt, "chat" if t in ("in", "out", "agent") else "system")
    if t in ("system", "note"):
        skill_type = "note" if t == "note" else "system"
    return {
        "id": mid,
        "created_at": iso_from_ts(m.get("ts")),
        "is_from_company": t in ("out", "agent"),
        "is_from_bot": t == "out",            # 'out' = template/bot; 'agent' = humano
        "author_id": m.get("sender_id"),
        "author_name": m.get("username"),
        "type": skill_type,
        "text": _texto(m),
        "media_id": mid if url else None,
        "_raw_type": t,
        "_raw_msg_type": mt,
        "_content": m.get("content"),
    }

def _raw_messages_local(ns):
    f = os.path.join(ROOT, "entrada", "api", "messages", "%s.json" % ns)
    if not os.path.exists(f): return []
    try:
        d = json.load(open(f, encoding="utf-8"))
    except Exception:
        return []
    return d.get("messages", []) if isinstance(d, dict) else (d if isinstance(d, list) else [])

def _raw_messages_live(ns):
    out, page, lastp = [], 1, 1
    while page <= lastp:
        r = api_get("/subscriber/chat-messages?user_ns=%s&include_bot=1&include_system=1&include_note=1&limit=100&page=%d" % (ns, page))
        out += r.get("data", [])
        try: lastp = int(r["meta"]["last_page"])
        except Exception: lastp = 1
        page += 1; time.sleep(0.05)
    return out

def raw_messages(ns):
    raw = _raw_messages_local(ns) if MODE == "local" else _raw_messages_live(ns)
    raw = [m for m in raw if m.get("ts")]
    raw.sort(key=lambda m: int(m["ts"]))
    return raw

def media_url(msg_id):
    return _MEDIA_URLS.get(str(msg_id))

# ---------- estado de CRM (boards) ----------
def board_state(ns):
    """Le os boards (Moved to board: ...) e devolve o board atual + historico."""
    boards = []
    for m in raw_messages(ns):
        c = m.get("content")
        if isinstance(c, str) and c.startswith("Moved to board:"):
            b = c.replace("Moved to board:", "").replace("***", "").strip()
            boards.append(b)
    return {"stage": boards[-1] if boards else "LEAD ENTROU NO COMERCIAL", "boards": boards}
