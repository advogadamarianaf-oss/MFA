---
title: Arquitetura
layout: default
nav_order: 3
description: "Diagrama de componentes, fluxo de dados e modos de operacao do MFA"
---

# Arquitetura

## Diagrama de Componentes

```
                         +-------------------+
                         |   Google Sheets   |
                         | (planilha central)|
                         +--------+----------+
                                  ^
                     escrita API  |  leitura API
                    (gcred.json)  |  (gcred.json)
                                  |
+------------------+    +---------+-----------+    +------------------+
|  Atende Direito  |    |   pipeline_diario   |    |   Claude Code    |
|  (API REST)      +--->+      .py            |    |  (skills + IA)   |
|  subscribers,    |    | (agendado 13h)      |    +--------+---------+
|  messages,       |    +---------------------+             |
|  boards, tags    |                                        |
+--------+---------+                              +---------+----------+
         |                                        |  Claude in Chrome  |
         |  API REST                              |  (extensao)        |
         |  (MINHA_API_KEY)                       +--------+-----------+
         |                                                 |
         v                                                 v
+--------+---------+                              +--------+---------+
|  entrada/api/    |                              |  Chat Ao Vivo    |
|  subscribers/    |                              |  (navegador)     |
|  messages/       |                              +------------------+
+------------------+
         |
         v
+------------------+     +---------------------+
|  clientes/*.md   |<--->|  _memoria/          |
|  (1 por cliente) |     |  crm_definicoes.md  |
+------------------+     |  indice_clientes.md |
         |               +---------------------+
         v
+------------------+
|  Resumos/*.md    |
|  (por cliente)   |
+------------------+
```

## Fluxo de Dados

### 1. Coleta (API)

```
Atende Direito API
    |
    +-- GET /subscribers (paginado, 100/pagina)
    |       -> entrada/api/subscribers/p001.json ... p0XX.json
    |
    +-- GET /subscriber/chat-messages?user_ns=...
            -> entrada/api/messages/<ns>.json
```

### 2. Analise (IA ou data-driven)

```
Conversa bruta (API ou navegador)
    |
    +-- Classificacao CRM (1 dos 12 estagios)
    |       fonte: _memoria/crm_definicoes.md
    |       sinal: ultimo "Moved to board: X" nos eventos
    |
    +-- Sequencia (onde parou no fluxo)
    |       ex: "Follow-up 3 de 5 sem resposta"
    |
    +-- Resumo por janela temporal
    |       24h | 7 dias | 15 dias | 30 dias
    |
    +-- Arquivo do cliente
            clientes/<nome>.md (modelo: _MODELO_CLIENTE.md)
```

### 3. Escrita (planilha)

```
Resumos gerados
    |
    +-- pipeline_diario.py (automatico, data-driven)
    |       -> Google Sheets API -> colunas RESUMO (M:P, G:J, V:Y, F:I)
    |
    +-- processar-planilha (skill, via navegador)
            -> Claude in Chrome -> celulas M:P na aba CAMPANHA META
```

## Canais de Entrada

O escritorio recebe leads por 3 bots/fluxos no Atende Direito:

| Canal | Flow ID | Descricao |
|:------|:--------|:----------|
| Comercial - API OFICIAL | `f175863` | Principal (formulario web, Meta Ads) |
| Comercial 2 - API OFICIAL | `f270363` | Secundario (WhatsApp direto) |
| SAC | `f229905` | Suporte / pos-venda |

O mesmo lead pode ter cadastros separados em mais de um fluxo. O sistema
consolida tudo em **um unico arquivo** por pessoa.

## Modos de Operacao

| Modo | Quando usar | Como roda |
|:-----|:------------|:----------|
| **Pipeline diario** | Atualizacao em massa, todos os dias | `pipeline_diario.py` (agendado 13h, sem Claude) |
| **Analise por skill** | Leads especificos, analise profunda | Claude Code + Claude in Chrome (sob demanda) |
| **Analise em lote** | Planilha inteira, em lotes de 5 | Skill `processar-planilha` (orquestrador + agentes) |
| **Resumo temporal** | Gerar resumos 24h/7/15/30 de clientes ja analisados | Skill `resumo-temporal` (so arquivos locais) |
