# -*- coding: utf-8 -*-
"""Runner da skill analisar-conversas plugado no Atende Direito.

Uso:
  python run_atende.py 10                  # audita os 10 leads mais recentes com conversa
  python run_atende.py f175863u123 f175...  # audita user_ns especificos
  python run_atende.py 10 --janela 14       # janela de 14 dias
  python run_atende.py 10 --no-ia           # so metricas+conversa (sem chamar a IA)
  python run_atende.py 10 --canal whatsapp  # filtra canal

Saidas:
  - auditoria_resultado.json  (na raiz do projeto)
  - auditoria_resumo.md       (tabela legivel ordenada por score/alerta)
"""
import os, sys, json, datetime
import atende_common as A
import crm_adapter, chat_adapter
import auditor_completo as AUD

def parse_args(argv):
    ns_list, limit, janela, no_ia, canal = [], None, 2, False, None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a == "--janela": janela = int(argv[i+1]); i += 2; continue
        if a == "--no-ia": no_ia = True; i += 1; continue
        if a == "--canal": canal = argv[i+1]; i += 2; continue
        if A.is_ns(a): ns_list.append(a)
        elif a.isdigit(): limit = int(a)
        i += 1
    return ns_list, limit, janela, no_ia, canal

def main():
    ns_list, limit, janela, no_ia, canal = parse_args(sys.argv[1:])
    filtro = {}
    if ns_list: filtro["ns_list"] = ns_list
    if limit: filtro["limit"] = limit
    if canal: filtro["canal"] = canal
    if not ns_list and not limit: filtro["limit"] = 10

    if no_ia or not os.environ.get("ANTHROPIC_API_KEY"):
        if not no_ia:
            print("AVISO: ANTHROPIC_API_KEY ausente no .env -> rodando SEM analise IA (so metricas).")
        AUD._analisar_ia = lambda ctx: {"_sem_ia": True}

    opps = crm_adapter.buscar_opps_filtro(filtro)
    print("Leads a auditar: %d (modo dados: %s, janela: %dd)" % (len(opps), A.MODE, janela))
    resultados = AUD.auditar(opps, janela_dias=janela)

    out_json = os.path.join(A.ROOT, "auditoria_resultado.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=1)

    def score(r):
        ia = r.get("analise_ia") or {}
        return ia.get("score_fechamento") if isinstance(ia.get("score_fechamento"), int) else -1
    ordenados = sorted(resultados, key=lambda r: (0 if (r.get("analise_ia") or {}).get("alerta_critico") else 1, -score(r)))

    linhas = ["# Auditoria de conversas — %s" % datetime.datetime.now().strftime("%d/%m/%Y %H:%M"), ""]
    linhas.append("| # | Lead | Estado | Score | TR inicial | Msgs (lead/emp) | Alerta |")
    linhas.append("|---|------|--------|-------|-----------|-----------------|--------|")
    for i, r in enumerate(ordenados, 1):
        ia = r.get("analise_ia") or {}; t = r.get("tempos") or {}
        linhas.append("| %d | %s | %s | %s | %s min | %s/%s | %s |" % (
            i, (r.get("nome") or "?")[:28], ia.get("estado_atual", "-"),
            ia.get("score_fechamento", "-"), t.get("tr_inicial_min", "-"),
            t.get("n_lead", "-"), t.get("n_company", "-"),
            "SIM" if ia.get("alerta_critico") else ""))
    linhas.append("")
    for i, r in enumerate(ordenados, 1):
        ia = r.get("analise_ia") or {}
        linhas += ["## %d. %s (%s)" % (i, r.get("nome", "?"), r.get("telefone_real") or r.get("opp_id")),
                   "- **Estado:** %s" % ia.get("estado_atual", "-"),
                   "- **Score:** %s/100 — %s" % (ia.get("score_fechamento", "-"), ia.get("score_justificativa", "")),
                   "- **Resumo:** %s" % ia.get("resumo_caso", "-"),
                   "- **Próximo passo:** %s" % ia.get("proximo_passo_vendedor", "-")]
        if ia.get("alerta_critico"): linhas.append("- **ALERTA:** %s" % ia["alerta_critico"])
        if r.get("erro"): linhas.append("- **erro:** %s" % r["erro"])
        linhas.append("")
    out_md = os.path.join(A.ROOT, "auditoria_resumo.md")
    open(out_md, "w", encoding="utf-8").write("\n".join(linhas))
    print("OK -> %s" % out_json)
    print("OK -> %s" % out_md)

if __name__ == "__main__":
    main()
