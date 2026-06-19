# -*- coding: utf-8 -*-
"""Adapter de CRM para o Atende Direito.
O "CRM" aqui sao os boards do Atende. Cada opp = um subscriber (lead).
O stage = board atual (ultimo 'Moved to board:').
"""
import datetime
import atende_common as A

def _criado_at(s):
    # usa 'subscribed' do subscriber (ex: '2026-06-11 10:34:09'); cai pra last_message_at
    v = (s or {}).get("subscribed") or (s or {}).get("last_message_at") or ""
    v = str(v).strip()
    if not v:
        return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    return v.replace(" ", "T") + ("Z" if "Z" not in v else "")

def _opp_from_sub(s):
    ns = s.get("user_ns")
    phone = s.get("phone") or ""
    return {
        "opp_id": ns,
        "nome": s.get("name") or s.get("first_name") or ns,
        "nome_lead": s.get("name") or s.get("first_name") or ns,
        # 'telefone' carrega o ns como fallback p/ leads sem telefone (Instagram):
        "telefone": phone or ns,
        "telefone_real": phone,
        "criado_at": _criado_at(s),
        "owner": s.get("agent_id"),
        "canal": s.get("channel"),
        "lead_status": s.get("lead_status"),
    }

def buscar_opps_filtro(filtro=None):
    """filtro (dict) opcional:
       - ns_list   : lista de user_ns especificos
       - limit     : numero maximo de opps
       - com_conversa (bool, default True): so leads que tem mensagens baixadas/registradas
       - canal     : 'whatsapp' | 'instagram' (filtra por canal)
    Retorna lista de opps {opp_id, nome, telefone, criado_at, ...}.
    """
    filtro = filtro or {}
    subs = A.subscribers()
    ns_list = filtro.get("ns_list")
    if ns_list:
        subs = [A.sub_by_ns(ns) for ns in ns_list]
        subs = [s for s in subs if s]
    canal = filtro.get("canal")
    if canal:
        subs = [s for s in subs if (s.get("channel") or "").lower() == canal.lower()]
    opps = []
    com_conversa = filtro.get("com_conversa", True)
    for s in subs:
        ns = s.get("user_ns")
        if not ns:
            continue
        if com_conversa and not ns_list:
            # so inclui quem tem conversa de fato (>=1 msg)
            if not A.raw_messages(ns):
                continue
        opps.append(_opp_from_sub(s))
        if filtro.get("limit") and len(opps) >= int(filtro["limit"]):
            break
    return opps

def get_opp(opp_id):
    """Retorna dict completo da opp (subscriber + stage/board atual)."""
    s = A.sub_by_ns(opp_id) or {"user_ns": opp_id}
    bs = A.board_state(opp_id)
    item = _opp_from_sub(s) if s.get("user_ns") else {"opp_id": opp_id}
    item.update({
        "stage": bs["stage"],
        "boards": bs["boards"],
        "custom_fields": {(f.get("name")): f.get("value") for f in (s.get("user_fields") or [])},
    })
    return item

def update_opp(opp_id, payload):
    """Mover board / atribuir via API ainda nao implementado (a auditoria nao usa).
    A API do Atende usada hoje no projeto e somente leitura."""
    raise NotImplementedError("update_opp: escrita no Atende nao habilitada neste projeto.")
