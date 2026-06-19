---
title: Skills e Comandos
layout: default
nav_order: 7
nav_title: Skills
description: "Referencia das 4 skills customizadas do Claude Code"
---

# Skills e Comandos

O projeto utiliza 4 skills customizadas do Claude Code.

---

## 1. /analisar-lead

**O que faz:** Analisa a conversa de um ou mais leads no Atende Direito e gera
resumo + classificacao CRM + sequencia.

**Quando usar:** "analisa o lead Fulano", "analisa Maria, Joao e Ana"

**Requer:** Claude in Chrome conectado, Atende Direito logado.

| Cenario | Execucao |
|:--------|:---------|
| 1 lead | Executa direto, sequencial |
| 2+ leads | Agentes em paralelo (1 por lead, max 4-5) |

**Saida:** Arquivo do cliente + tabela-resumo (Lead, CRM, Sequencia, Proximo passo)

---

## 2. /resumo-temporal

**O que faz:** Gera resumo por janelas de tempo (24h, 7d, 15d, 30d) a partir
dos arquivos em `clientes/`.

**Quando usar:** "faz o resumo temporal do Anderson"

**Requer:** Arquivo do cliente ja existente. **Nao precisa de navegador.**

**Saida:** Arquivo `Resumos/Resumo - <Nome>.md` com 4 secoes.

---

## 3. /processar-planilha

**O que faz:** Processa leads da planilha RELATORIOS COMERCIAIS NOVA (aba CAMPANHA META)
em lotes de 5.

**Quando usar:** "processa a planilha", "roda o proximo lote"

**Requer:** Claude in Chrome conectado, Atende Direito + Google Sheets logados.

| Etapa | Quem | O que faz |
|:------|:-----|:----------|
| 1 | Orquestrador | Seleciona proximos 5 nomes |
| 2 | 1 agente (sequencial) | Busca no Atende Direito, extrai texto |
| 3 | 5 agentes (paralelo) | Cria cliente.md + Resumo.md |
| 4 | Orquestrador | Atualiza indice + preenche planilha M:P |

---

## 4. /processar-planilha-api

**O que faz:** Atualiza resumos de TODAS as abas via API. Dois modos:

### Modo Automatico

> Roda 100% na maquina, sem Claude. Agendado todos os dias as 13h.

Script: `pipeline_diario.py`. Le planilha → baixa subscribers/conversas → gera resumos → escreve.

### Modo Analise Profunda

Sob demanda, com Claude. Agentes leem transcripts e escrevem resumos nuancados
(detecta objecoes, tom, contexto).

### Abas e colunas

| Aba | Casamento | Colunas RESUMO |
|:----|:----------|:---------------|
| CAMPANHA META | Telefone | M:P |
| CAMPANHA GOOGLE | user_ns | G:J |
| ORGANICO | user_ns | G:J |
| MANYCHAT | user_ns | F:I |
| REUNIOES & FECHAMENTOS | Telefone | V:Y |
