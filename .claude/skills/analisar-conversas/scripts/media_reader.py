import os, base64, json, urllib.request, urllib.error, re, tempfile

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL  = "claude-sonnet-4-5-20250929"

# Cache permanente — transcrever 1x e nunca de novo
_CACHE = "cache_transcricoes.json"

def _carrega_cache():
    if not os.path.exists(_CACHE): return {}
    try:
        with open(_CACHE, encoding="utf-8") as f: return json.load(f)
    except: return {}

def _salva_cache(c):
    with open(_CACHE, "w", encoding="utf-8") as f: json.dump(c, f, ensure_ascii=False, indent=1)

def _baixar(url):
    r = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}, method="GET")
    with urllib.request.urlopen(r, timeout=120) as x: return x.read()

# Whisper local — lazy load
_whisper = None
def _whisper_model():
    global _whisper
    if _whisper is None:
        from faster_whisper import WhisperModel
        _whisper = WhisperModel("small", device="cpu", compute_type="int8")
    return _whisper

def transcrever_audio(audio_bytes, ext="mp3", lang="pt", cache_key=None):
    """Transcreve áudio via Whisper local. cache_key opcional (ex: msg_id) pra cachear."""
    if cache_key:
        c = _carrega_cache()
        if cache_key in c: return c[cache_key]
    with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as t:
        t.write(audio_bytes); path = t.name
    try:
        segments, _ = _whisper_model().transcribe(path, language=lang, beam_size=5, vad_filter=True)
        texto = " ".join(s.text.strip() for s in segments).strip() or "[sem fala]"
    finally:
        os.unlink(path)
    if cache_key:
        c = _carrega_cache(); c[cache_key] = texto; _salva_cache(c)
    return texto

def ler_doc(doc_bytes, mime, cache_key=None):
    """Lê PDF/imagem via Claude vision. mime = 'application/pdf' ou 'image/jpeg' etc."""
    if cache_key:
        c = _carrega_cache()
        if cache_key in c: return c[cache_key]
    b64 = base64.b64encode(doc_bytes).decode("ascii")
    if mime.startswith("image/"):
        block = {"type":"image","source":{"type":"base64","media_type":mime,"data":b64}}
    elif mime == "application/pdf":
        block = {"type":"document","source":{"type":"base64","media_type":"application/pdf","data":b64}}
    else:
        return f"[tipo não suportado: {mime}]"
    body = {"model":CLAUDE_MODEL,"max_tokens":1500,
        "messages":[{"role":"user","content":[block,
            {"type":"text","text":"Resume em até 2 frases o que este documento mostra. Responda em português."}]}]}
    H = {"x-api-key":ANTHROPIC_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"}
    r = urllib.request.Request("https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"), headers=H, method="POST")
    with urllib.request.urlopen(r, timeout=120) as x: d = json.load(x)
    txt = "".join(b.get("text","") for b in d.get("content",[]) if b.get("type")=="text").strip()
    if cache_key:
        c = _carrega_cache(); c[cache_key] = txt; _salva_cache(c)
    return txt
