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
