---
title: Inicio
layout: default
nav_order: 1
description: "Documentacao tecnica completa do sistema MFA — Analise de Mensagens para Advocacia Medica & Odontologica"
permalink: /
---

# MFA — Analise de Mensagens
{: .fs-9 }

Documentacao tecnica do sistema de analise, classificacao e acompanhamento de leads
para o escritorio de **Advocacia Medica & Odontologica** (Mariana Friedrich).
{: .fs-6 .fw-300 }

[Guia Rapido]({% link guia-rapido.md %}){: .btn .btn-primary .fs-5 .mb-4 .mb-md-0 .mr-2 }
[Ver no GitHub](https://github.com/advogadamarianaf-oss/MFA){: .btn .fs-5 .mb-4 .mb-md-0 }

---

## O que e o MFA?

O **MFA (Mensagem, Funil, Analise)** e um sistema hibrido que combina automacao por IA,
API REST e Google Sheets para transformar conversas brutas de leads em inteligencia
comercial acionavel.

### O problema

O escritorio recebe dezenas de leads por dia via Meta Ads, Google Ads, organico e
Instagram. Cada lead inicia uma conversa no **Atende Direito** e precisa ser classificado,
acompanhado e reportado. Fazer isso manualmente para 100+ leads e inviavel.

### A solucao

| Componente | O que faz |
|:-----------|:----------|
| **Memoria local (Markdown)** | Um arquivo por cliente com conversa, CRM, resumo e proximo passo |
| **Automacao por IA** | Claude Code analisa conversas em paralelo, classifica CRM e gera resumos |
| **Pipeline diario** | Script Python (13h) baixa da API, gera resumos e escreve na planilha |
| **4 Skills customizadas** | Comandos do Claude Code para operacoes recorrentes |

### Resultados

| Metrica | Antes | Depois |
|:--------|:------|:-------|
| Tempo por lead | ~15 min manual | ~2 min automatico |
| Leads analisados/dia | 10-15 | 50+ (lotes de 5) |
| Atualizacao da planilha | manual, 1x/semana | automatica, diaria 13h |
| Cobertura de resumos | parcial | 100% (4 janelas temporais) |
| Classificacao CRM | subjetiva | padronizada (12 estagios) |

---

## Stack

| Componente | Tecnologia |
|:-----------|:-----------|
| CRM / Chat | Atende Direito (API REST + WhatsApp Business) |
| Planilha | Google Sheets (API v4, conta de servico) |
| IA | Claude Code + Claude in Chrome |
| Scripts | Python 3.12, PowerShell, Batch |
| Dados | Markdown, JSON, TSV |

---

## Indice da documentacao

| Pagina | Descricao |
|:-------|:----------|
| [Visao Geral]({% link visao-geral.md %}) | Problema, solucao, resultados e publico |
| [Arquitetura]({% link arquitetura.md %}) | Diagrama de componentes e fluxo de dados |
| [Estrutura de Arquivos]({% link estrutura-arquivos.md %}) | Mapa completo de pastas e arquivos |
| [CRM — Os 12 Estagios]({% link crm-definicoes.md %}) | Definicao de cada CRM e regras de classificacao |
| [Fluxo de Trabalho]({% link fluxo-trabalho.md %}) | Como analisar leads passo a passo |
| [Skills e Comandos]({% link skills.md %}) | Referencia das 4 skills do Claude Code |
| [Pipeline Diario]({% link pipeline-diario.md %}) | Automacao: API + resumos + planilha |
| [Integracoes]({% link integracoes.md %}) | Atende Direito, Google Sheets, Chrome |
| [Guia Rapido]({% link guia-rapido.md %}) | Setup inicial e primeiros passos |
