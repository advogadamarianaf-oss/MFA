# Projeto: Análise de Mensagens — Atende Direito

Escritório de **Advocacia Médica & Odontológica**. Este projeto gerencia memória
**local** para analisar conversas de leads/clientes no Atende Direito, gerar
resumos e classificar cada um em um **CRM** e sua **sequência**.

## Sempre responder em português.

## Estrutura
- `_memoria/` — memória central (não apagar).
  - `crm_definicoes.md` — os 12 CRMs e o conceito de sequência. **Fonte da verdade.**
  - `indice_clientes.md` — lista de todos os clientes e CRM atual de cada um.
- `_templates/` — modelo de prompt do agente de análise.
- `clientes/<nome>.md` — **um arquivo por cliente** com tudo: status (CRM + sequência),
  identificação, resumo, próximo passo, histórico e a conversa registrada.
  - `_MODELO_CLIENTE.md` — copie este arquivo ao criar um cliente novo.
- `entrada/` — conversas brutas aguardando processamento (`processadas/` = já analisadas).

## Fluxo de trabalho
1. Para cada lead/conversa, ler a conversa (no navegador, via agente, ou colada em `entrada/`).
2. Criar/atualizar `clientes/<nome>.md` a partir de `_MODELO_CLIENTE.md`.
3. Preencher status (CRM + sequência), resumo e a conversa no mesmo arquivo (ver `crm_definicoes.md`).
4. Atualizar a linha do cliente em `_memoria/indice_clientes.md`.

## Regras de classificação
- Sempre o **CRM mais avançado** comprovado pela conversa.
- Detalhar a **sequência** (onde o lead parou no fluxo).
- Em dúvida entre dois CRMs, registrar ambos nas observações.
- Nunca inventar dados fora da conversa.

## Lead em mais de um canal (Comercial / Comercial 2 / SAC)
Bots/fluxos do workspace: **Comercial - API OFICIAL** (`f175863`),
**Comercial 2 - API OFICIAL** (`f270363`) e **SAC** (`f229905`). O mesmo lead pode ter
**cadastros separados** em mais de um fluxo (ex.: formulário web no Comercial e WhatsApp
no Comercial 2). Quando o **mesmo telefone/pessoa** aparece em mais de um canal:
- **Um cliente = um arquivo.** Nunca criar dois arquivos para a mesma pessoa; consolidar em `clientes/<nome>.md`.
- **Linha do tempo única**, ordenada por data/hora, marcando o canal de cada trecho (`[Comercial]` / `[Comercial 2]` / `[SAC]`).
- **Classificar pelo CRM mais avançado** comprovado em **qualquer** dos canais.
- **Registrar todos os `user_ns` e os canais** no cabeçalho do arquivo (rastreabilidade).
- Conflito entre canais (avançado num, parado no outro) → registrar ambos nas observações.
- Ao buscar, **conferir por telefone se há mais de um resultado** (um por fluxo) e abrir todos antes de classificar; senão o lead fica subclassificado.

## Análise no navegador (em paralelo)
Use `_templates/prompt_agente_analise.md` para disparar um agente por lead.
Requer a extensão Claude in Chrome conectada ao Atende Direito.
