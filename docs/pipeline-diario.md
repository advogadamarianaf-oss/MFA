---
title: Pipeline Diario
layout: default
nav_order: 8
nav_title: Pipeline
description: "Documentacao do pipeline_diario.py — automacao de coleta, analise e escrita"
---

# Pipeline Diario

O `pipeline_diario.py` e o script de automacao principal. Roda sem Claude,
agendado para todos os dias as 13h via Agendador de Tarefas do Windows.

## O que faz

```
1. Le credenciais do .env e gcred.json
         |
2. Baixa TODOS os subscribers do Atende Direito (paginado, 100/pag)
         |
3. Le cada aba da planilha via Google Sheets API
         |
4. Para cada lead de cada aba:
   a) Casa por telefone ou user_ns
   b) Baixa as mensagens (GET /subscriber/chat-messages)
   c) Analisa por janela temporal (24h, 7d, 15d, 30d)
   d) Gera 4 textos de resumo (max 250 chars cada)
         |
5. Escreve os resumos nas colunas corretas (Sheets API)
         |
6. Loga tudo em pipeline_log.txt
```

## Como Executar

```bash
# Manualmente
python pipeline_diario.py

# Ou pelo atalho
RODAR - Pipeline diario (tudo).bat

# Agendar (cria tarefa no Windows)
AGENDAR todos os dias 13h.bat
```

## Credenciais

| Credencial | Arquivo | Para que |
|:-----------|:--------|:---------|
| `MINHA_API_KEY` | `.env` | API do Atende Direito (Bearer token) |
| Google Service Account | `gcred.json` | Leitura/escrita na planilha Google |

> A conta de servico Google precisa estar compartilhada como **Editor** na planilha.

## Logica de Casamento

| Aba | Campo | Logica |
|:----|:------|:-------|
| CAMPANHA META | TELEFONE | Normaliza digitos, remove DDI 55, compara ultimos 10 |
| CAMPANHA GOOGLE | ATENDE DIREITO ID | Compara user_ns diretamente |
| ORGANICO | ATENDE DIREITO ID | Compara user_ns diretamente |
| MANYCHAT | ATENDE DIREITO ID | Compara user_ns |
| REUNIOES & FECHAMENTOS | TELEFONE | Mesma logica da CAMPANHA META |

## Logica de Resumo

Para cada lead com conversa encontrada:

1. **t0** = timestamp da primeira mensagem
2. **Janelas**: t0+1d, t0+7d, t0+15d, t0+30d
3. Analisa mensagens ate o cutoff de cada janela:
   - `boards[]` = todos os "Moved to board: X"
   - `crm` = ultimo board
   - `nin` / `nout` = mensagens de entrada/saida
   - `errs` = falhas de entrega
   - `reun` / `hum` / `flux` = flags de reuniao/humano/fluxograma

## Exemplo de log

```
=== execucao 19/06/2026 13:00:15 ===
Baixando subscribers...
  subscribers: 847
[CAMPANHA META] 142 linhas escritas em M2 (568 celulas).
[CAMPANHA GOOGLE] 87 linhas escritas em G2 (348 celulas).
[ORGANICO] 53 linhas escritas em G2 (212 celulas).
[MANYCHAT] 31 linhas escritas em F2 (124 celulas).
[REUNIOES & FECHAMENTOS] 28 linhas escritas em V2 (112 celulas).

Concluido em 19/06 13:04. Total: 1364 celulas. Leads: 312.
```
