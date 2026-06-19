# -*- coding: utf-8 -*-
"""Adapter de chat para o Atende Direito.
Implementa o contrato esperado pela skill, plugado no Atende.
"""
import atende_common as A

def find_contact_by_phone(value):
    """Aceita telefone OU user_ns (a skill chama isso com o campo 'telefone' da opp,
    que pode carregar o user_ns como fallback quando o lead nao tem telefone — ex: Instagram).
    Retorna o user_ns (contact_id) ou None.
    """
    if not value:
        return None
    if A.is_ns(value):
        return str(value).strip()
    return A.ns_by_phone(value)

def get_messages(contact_id, since_iso=None):
    """contact_id = user_ns. Retorna mensagens normalizadas (todas, ordenadas),
    opcionalmente filtradas a partir de since_iso (ISO 'YYYY-MM-DDTHH:MM:SSZ').
    """
    ms = [A.normalizar(m) for m in A.raw_messages(contact_id)]
    ms = [m for m in ms if m["created_at"]]
    if since_iso:
        ms = [m for m in ms if m["created_at"] >= since_iso]
    return ms

def get_media_url(message_id):
    """URL temporaria da midia. No Atende a URL ja vem embutida na msg e e cacheada
    durante a normalizacao, entao basta consultar o cache."""
    return A.media_url(message_id)
