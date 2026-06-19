---
title: MFA — Analise de Mensagens
layout: default
nav_order: 1
nav_title: Inicio
description: "Documentacao tecnica do sistema MFA — Analise de Mensagens"
permalink: /
---

<div class="hero">
  <h1>MFA — Analise de Mensagens</h1>
  <p>Documentacao tecnica do sistema de analise, classificacao e acompanhamento de leads para o escritorio de <strong>Advocacia Medica & Odontologica</strong> (Mariana Friedrich).</p>
  <div class="hero-buttons">
    <a href="{{ '/guia-rapido' | relative_url }}" class="btn btn-primary">Guia Rapido</a>
    <a href="https://github.com/advogadamarianaf-oss/MFA" target="_blank" class="btn btn-secondary">Ver no GitHub</a>
  </div>
</div>

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

## Paginas

| Pagina | Descricao |
|:-------|:----------|
| [Visao Geral]({{ '/visao-geral' | relative_url }}) | Problema, solucao, resultados e publico |
| [Arquitetura]({{ '/arquitetura' | relative_url }}) | Diagrama de componentes e fluxo de dados |
| [Estrutura de Arquivos]({{ '/estrutura-arquivos' | relative_url }}) | Mapa completo de pastas e arquivos |
| [CRM — Os 12 Estagios]({{ '/crm-definicoes' | relative_url }}) | Definicao de cada CRM e regras |
| [Fluxo de Trabalho]({{ '/fluxo-trabalho' | relative_url }}) | Como analisar leads passo a passo |
| [Skills e Comandos]({{ '/skills' | relative_url }}) | Referencia das 4 skills do Claude Code |
| [Pipeline Diario]({{ '/pipeline-diario' | relative_url }}) | Automacao: API + resumos + planilha |
| [Integracoes]({{ '/integracoes' | relative_url }}) | Atende Direito, Google Sheets, Chrome |
| [Guia Rapido]({{ '/guia-rapido' | relative_url }}) | Setup inicial e primeiros passos |
