---
name: analisar-conversas
description: Audita conversas comerciais/atendimento entre vendedor/SDR e cliente (qualquer CRM + qualquer canal de mensagens). Extrai métricas (TR, contagens), transcreve áudios localmente, lê PDFs/imagens via LLM e gera análise IA estruturada por caso (estado, score 0-100, próximo passo, alerta crítico). Use quando o usuário pedir auditoria de um grupo de conversas/leads/chamados e quiser entender por que não fecharam, onde travou, e o que fazer.
---

# Análise de conversas comerciais com IA

Skill genérica pra auditar grupos de conversas (vendas, atendimento, qualificação) e devolver:
- Métricas objetivas: tempo de resposta inicial, tempo médio entre msgs, contagem de mensagens
- Conteúdo enriquecido: transcrição de áudios + leitura de docs/imagens anexados
- Análise IA por caso: estado, score de fechamento, próximo passo concreto, alertas críticos

Funciona com qualquer combinação de CRM (Pipedrive, HubSpot, GHL, Salesforce, CRM próprio) + canal de mensagens (WhatsApp, Digisac, Twilio, Intercom, próprio).

## Quando usar

- Auditoria de grupo: "estuda esses 20 leads que travaram", "ver por que não fecharam essa semana"
- Triagem de fila: dentre N leads em determinado estágio, quais merecem atenção agora
- Pós-mortem: depois de uma campanha, analisar o que rolou em cada lead
- Análise de SDR: comparar performance, tempo de resposta, qualidade de atendimento
- Identificar travas: onde leads param (preço? proposta? sumiço do vendedor?)

## Arquitetura — 3 módulos plug-and-play

```
crm_adapter.py         -> busca opps + custom fields do seu CRM
chat_adapter.py        -> busca mensagens + baixa mídia do seu canal
media_reader.py        -> transcreve áudio (Whisper local) + lê doc/img (Claude)
auditor_completo.py    -> orquestra tudo, aplica análise IA, retorna dict por lead
```

Cada adapter é independente — troca CRM/canal sem mexer no resto.

## Pré-requisitos

```bash
pip install faster-whisper
# Whisper local roda em CPU, baixa modelo "small" (~500MB) na primeira execução
```

Tokens necessários (placeholders):
```python
ANTHROPIC_API_KEY = "sk-ant-..."   # pra análise IA + leitura de docs/imagens
CRM_TOKEN         = "..."          # depende do CRM
CHAT_TOKEN        = "..."          # depende do canal de chat
```

Estimativa de custo: ~$0.02 por lead analisado (Claude Sonnet). Whisper local = grátis.

## Esqueleto do `crm_adapter.py`

```python
"""Adapter pro seu CRM. Implementar essas funções."""

def buscar_opps_filtro(filtro):
    """Retorna lista de opps que casam com filtro (stage, owner, criado_apos, etc).
    Cada opp deve ter: {opp_id, nome_lead, telefone, criado_at, owner, stage, custom_fields}.
    """
    raise NotImplementedError

def get_opp(opp_id):
    """Retorna dict completo da opp."""
    raise NotImplementedError

def update_opp(opp_id, payload):
    """Atualiza opp (mover stage, atribuir owner, etc)."""
    raise NotImplementedError
```

## Esqueleto do `chat_adapter.py`

```python
"""Adapter pro seu canal de chat. Implementar essas funções."""

def find_contact_by_phone(phone):
    """Retorna contact_id no canal de chat a partir do telefone."""
    raise NotImplementedError

def get_messages(contact_id, since_iso=None):
    """Retorna lista paginada de mensagens (todas). Cada msg deve ter:
      id, created_at (ISO), is_from_company (bool), is_from_bot (bool),
      author_id, author_name, type ('chat'|'audio'|'image'|'document'|...),
      text (string ou None), media_id (string ou None).
    IMPORTANTE: paginar até esvaziar — leads podem ter 200+ msgs.
    """
    raise NotImplementedError

def get_media_url(message_id):
    """Retorna URL temporária pra baixar a mídia anexada à mensagem."""
    raise NotImplementedError
```

## `media_reader.py` — pronto pra usar

Independente de CRM/canal. Só recebe URL ou bytes.

```python
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
```

## `auditor_completo.py` — orquestrador

```python
"""Auditor genérico. Recebe lista de opp_ids, busca conversas, enriquece com
mídia, e gera análise IA por caso."""

import json, os, re, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

import crm_adapter, chat_adapter, media_reader

ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY","")
CLAUDE_MODEL  = "claude-sonnet-4-5-20250929"

def _msg_real(m):
    """Filtra ruído de sistema. Customizar conforme seu canal."""
    if m["type"] in ("ticket","hsm","system","log","note"): return False
    return bool((m.get("text") or "").strip()) or m["type"] in ("audio","ptt","image","video","document","sticker","location")

def _tempos(criado_iso, ms):
    """Calcula TR inicial + TR médio + contagens."""
    cr = datetime.fromisoformat(criado_iso.replace("Z","+00:00"))
    if cr.tzinfo is None: cr = cr.replace(tzinfo=timezone.utc)
    primeira_sdr = next((m for m in ms if m["is_from_company"] and not m["is_from_bot"]), None)
    tr_inicial = None
    if primeira_sdr:
        ps = datetime.fromisoformat(primeira_sdr["created_at"].replace("Z","+00:00"))
        tr_inicial = int((ps - cr).total_seconds()/60)
    intervalos = []
    i = 0
    while i < len(ms):
        m = ms[i]
        if not m["is_from_company"]:
            t_l = datetime.fromisoformat(m["created_at"].replace("Z","+00:00"))
            for j in range(i+1, len(ms)):
                n = ms[j]
                if n["is_from_company"] and not n["is_from_bot"]:
                    t_s = datetime.fromisoformat(n["created_at"].replace("Z","+00:00"))
                    intervalos.append(int((t_s-t_l).total_seconds()/60)); break
                if not n["is_from_company"]: break
        i += 1
    return {
        "tr_inicial_min": tr_inicial,
        "tr_medio_min": sum(intervalos)//len(intervalos) if intervalos else None,
        "n_lead": sum(1 for m in ms if not m["is_from_company"]),
        "n_company": sum(1 for m in ms if m["is_from_company"] and not m["is_from_bot"]),
        "n_bot": sum(1 for m in ms if m["is_from_bot"]),
    }

def _enriquecer(ms, max_audios=8, max_docs=5):
    """Transcreve áudios da empresa (cliente já vem transcrito em alguns canais)
    e lê docs/imgs. Retorna dict {msg_id: texto}."""
    out = {}
    audios_empresa_sem_text = [m for m in ms if m["is_from_company"]
                                and m["type"] in ("audio","ptt")
                                and not (m.get("text") or "").strip()]
    docs_imgs = [m for m in ms if m["type"] in ("image","document")]
    for m in audios_empresa_sem_text[-max_audios:]:
        try:
            url = chat_adapter.get_media_url(m["id"])
            audio = urllib.request.urlopen(url).read()
            out[m["id"]] = media_reader.transcrever_audio(audio, cache_key=m["id"])
        except Exception as e: out[m["id"]] = f"[erro: {e}]"
    for m in docs_imgs[-max_docs:]:
        try:
            url = chat_adapter.get_media_url(m["id"])
            data = urllib.request.urlopen(url).read()
            mime = "application/pdf" if m["type"]=="document" else "image/jpeg"
            out[m["id"]] = media_reader.ler_doc(data, mime, cache_key=m["id"])
        except Exception as e: out[m["id"]] = f"[erro: {e}]"
    return out

PROMPT_ANALISE = """Você é analista de chamados de vendas/atendimento. Analise o caso e responda em JSON:

{
  "resumo_caso": "1-2 frases descrevendo o que aconteceu",
  "sinais_positivos": ["sinais favoráveis ao fechamento"],
  "sinais_negativos": ["sinais que freiam o fechamento"],
  "objecoes_identificadas": ["objeções concretas do cliente (preço, eficácia, prazo, concorrência, dúvida no produto)"],
  "estado_atual": "uma de: 'aguardando_doc_cliente', 'proposta_apresentada_aguardando_decisao', 'reuniao_proposta_sem_horario', 'agendou_reuniao', 'em_negociacao', 'aguardando_evento_externo', 'qualificacao_inicial', 'inviavel', 'cliente_silencio_vendedor_pendente', 'fechado_ganho', 'fechado_perdido', 'outro'",
  "score_fechamento": 0,
  "score_justificativa": "1 frase",
  "proximo_passo_vendedor": "mensagem pronta que o vendedor deveria mandar AGORA (1-2 frases, tom casual)",
  "alerta_critico": "URGÊNCIA detectada (prazo expirando, cliente reclamando, concorrência ganhando) — ou null"
}

Score 0-100: 0-30 difícil/inviável, 31-60 normal, 61-85 quente, 86+ quase fechado.

CONTEXTO:
"""

def _analisar_ia(contexto):
    body = {"model": CLAUDE_MODEL, "max_tokens": 1500,
        "messages":[{"role":"user","content": PROMPT_ANALISE + contexto + "\n\nResponda APENAS JSON."}]}
    H = {"x-api-key":ANTHROPIC_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"}
    try:
        r = urllib.request.Request("https://api.anthropic.com/v1/messages",
            data=json.dumps(body).encode("utf-8"), headers=H, method="POST")
        with urllib.request.urlopen(r, timeout=120) as x: d = json.load(x)
        txt = "".join(b.get("text","") for b in d.get("content",[]) if b.get("type")=="text").strip()
        txt = re.sub(r"^```(?:json)?\s*","",txt); txt = re.sub(r"\s*```$","",txt)
        return json.loads(txt)
    except Exception as e: return {"erro": str(e)}

def auditar(opps, janela_dias=2):
    """opps: lista de {opp_id, nome, telefone, criado_at}.
    Retorna lista de dicts enriquecidos com tempos, midia, e análise IA."""
    cutoff = (datetime.now(timezone.utc) - timedelta(days=janela_dias)).isoformat().replace("+00:00","Z")
    out = []
    for idx, ob in enumerate(opps, 1):
        print(f"[{idx}/{len(opps)}] {ob.get('nome','?')[:40]}")
        try:
            opp_full = crm_adapter.get_opp(ob["opp_id"])
            contact = chat_adapter.find_contact_by_phone(ob["telefone"])
            ms_all = chat_adapter.get_messages(contact, since_iso=cutoff)
            ms = [m for m in ms_all if _msg_real(m)]
            item = {**ob, "opp_completo": opp_full, "tempos": _tempos(ob["criado_at"], ms)}
            enriched = _enriquecer(ms)
            def texto(m):
                t = (m.get("text") or "").strip()
                if t: return t
                if m["id"] in enriched:
                    e = enriched[m["id"]]
                    return f"[{m['type'].upper()} INTERPRETADO] {e}"
                return f"<{m['type']}>"
            quem = lambda m: ("CLIENTE" if not m["is_from_company"]
                              else ("BOT" if m["is_from_bot"] else f"VENDEDOR-{m.get('author_name','?')[:15]}"))
            ctx = [f"Opp: {ob.get('nome')} | Stage: {opp_full.get('stage')}",
                   f"Métricas: {item['tempos']}",
                   "\n--- CONVERSA ---"]
            for m in ms:
                ctx.append(f"[{m['created_at'][11:16]}] {quem(m)}: {texto(m)[:400]}")
            contexto = "\n".join(ctx)
            if len(contexto) > 30000: contexto = contexto[:30000] + "\n[truncado]"
            item["analise_ia"] = _analisar_ia(contexto)
            out.append(item)
        except Exception as e:
            out.append({**ob, "erro": str(e)})
    return out
```

## Como rodar

```python
import auditor_completo

opps_pra_analisar = [
    {"opp_id":"abc","nome":"João","telefone":"+5511999...","criado_at":"2026-06-11T10:00:00Z"},
    # ... mais opps
]

resultados = auditor_completo.auditar(opps_pra_analisar, janela_dias=2)

# Cada resultado tem:
# - tempos: {tr_inicial_min, tr_medio_min, n_lead, n_company, n_bot}
# - analise_ia: {resumo_caso, estado_atual, score_fechamento, proximo_passo_vendedor, alerta_critico, ...}

with open("resultado_auditoria.json","w",encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=1)
```

## Apresentação dos resultados

Formato sugerido pra cada lead:
```
N. Nome (+telefone)
   Estado: <estado_atual>
   Score: <0-100>/100 — <justificativa>
   Resumo: <resumo_caso>
   ALERTA: <alerta_critico se houver>
   Próximo passo: <mensagem pronta>
```

E uma tabela consolidada no topo com TR, contagens, último contato — ordenada por score (mais quentes primeiro) ou por alerta crítico.

## Padrões importantes

- **Sempre paginar mensagens até esvaziar** — leads engajados podem ter 200+ msgs; cortar perde o contexto crítico (reunião marcada anteriormente, link enviado, decisão tomada).
- **Cache permanente das transcrições** — transcrever áudio é caro em CPU; uma vez transcrito (msg_id é imutável) o texto não muda nunca.
- **Filtrar templates do typebot** ("Desejo continuar", "Olá, vi sua página sobre X") da contagem de engajamento — esses não são engajamento real, só clique no botão.
- **Tom da `proximo_passo_vendedor`** — ajustar no prompt pro tom da empresa (formal, casual, com emoji, sem emoji).
- **Janela_dias** — pra conversas que arrastam (vendas complexas), aumentar pra 7-14 dias. Pra fila quente diária, 1-2 dias basta.

## Customização do prompt de análise

O `PROMPT_ANALISE` está em português e focado em vendas. Pra outros contextos:
- Suporte/customer success: trocar "score_fechamento" por "score_satisfacao", "objecoes" por "problemas_relatados"
- Cobrança: trocar por "score_recuperacao", "objecoes" por "alegacoes_inadimplencia"
- Recrutamento: "score_aceite_oferta", "objecoes" por "duvidas_proposta"

## Limitações conhecidas

- Whisper local pode errar siglas, nomes próprios e jargão técnico — vale humano revisar quando crítico.
- Claude pode "alucinar" números/fatos não presentes na conversa — sempre validar score altos antes de agir.
- Modelo `small` do Whisper roda em CPU mas demora ~5-15s por minuto de áudio. Pra volume grande, considere modelo `tiny` (mais rápido, menos preciso) ou GPU.
- Caso a empresa tenha um pipeline próprio com regras específicas (ex: produto X só vende com reunião, produto Y é venda direta), refinar o prompt com essas regras no contexto.

---

## Integração com o Atende Direito (deste projeto)

Os adapters já vêm **implementados e plugados no Atende Direito** — não são mais esqueletos.

Arquivos em `scripts/`:
- `atende_common.py` — núcleo: lê `.env`, pagina a API, carrega subscribers, normaliza
  mensagens (in/out/agent/system/note → schema da skill), lê os boards (CRM).
- `crm_adapter.py` — opps = subscribers; `stage` = board atual (`Moved to board:`).
- `chat_adapter.py` — mensagens normalizadas; URL de mídia já vem embutida; áudios já
  trazem `transcribed_text` do próprio Atende (dispensa Whisper na maioria dos casos).
- `run_atende.py` — orquestrador pronto.

### Dois modos de dados
- **LOCAL** (padrão se existir `entrada/api/subscribers/`): usa os JSON já baixados —
  offline e de graça.
- **LIVE**: bate na API (`MINHA_API_KEY` no `.env`). Force com `ATENDE_MODE=live`.

### Como rodar
```bash
cd ".claude/skills/analisar-conversas/scripts"
python run_atende.py 10                 # 10 leads mais recentes com conversa
python run_atende.py 10 --janela 30      # janela de 30 dias (conversas que arrastam)
python run_atende.py f175863u764586043   # um user_ns específico
python run_atende.py 10 --no-ia          # só métricas (sem chamar a IA)
python run_atende.py 10 --canal whatsapp # filtra canal
```
Saídas na raiz do projeto: `auditoria_resultado.json` + `auditoria_resumo.md`
(tabela ordenada por alerta crítico e score).

### Pré-requisito da camada de IA
A análise IA (estado, score, próximo passo) e a leitura de imagens/PDF usam a API da
Anthropic. Adicione no `.env`:
```
ANTHROPIC_API_KEY = sk-ant-...
```
Sem essa chave, o runner roda automaticamente em modo `--no-ia` (só métricas + conversa).
