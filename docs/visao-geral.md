---
title: Visao Geral
layout: default
nav_order: 2
description: "O que e o projeto MFA, o problema resolvido e os resultados"
---

# Visao Geral

## O Problema

O escritorio de **Advocacia Medica & Odontologica** (Mariana Friedrich) recebe
dezenas de leads por dia via Meta Ads, Google Ads, organico e Instagram. Cada lead
inicia uma conversa no **Atende Direito** (plataforma de atendimento com WhatsApp
Business API) e precisa ser:

1. **Classificado** em um dos 12 estagios do funil (CRM)
2. **Acompanhado** ao longo do tempo (24h, 7, 15, 30 dias)
3. **Reportado** em uma planilha central com resumos por periodo

Fazer isso manualmente para 100+ leads por campanha e inviavel.

## A Solucao

O **MFA (Mensagem, Funil, Analise)** e um sistema hibrido que combina:

- **Memoria local em Markdown** — um arquivo por cliente com conversa completa,
  classificacao CRM, resumo e proximo passo
- **Automacao por IA** — Claude Code analisa conversas no navegador (Atende Direito)
  em paralelo, classifica CRM e gera resumos
- **Pipeline diario** — script Python que baixa dados da API, gera resumos
  data-driven e escreve na planilha Google automaticamente (agendado 13h)
- **Skills customizadas** — 4 comandos no Claude Code para operacoes recorrentes

## Resultados

| Metrica | Antes | Depois |
|:--------|:------|:-------|
| Tempo por lead (analise) | ~15 min manual | ~2 min (automatico) |
| Leads analisados/dia | 10-15 | 50+ (em lotes de 5) |
| Atualizacao da planilha | manual, 1x/semana | automatica, diaria 13h |
| Cobertura de resumos | parcial | 100% (4 janelas temporais) |
| Classificacao CRM | subjetiva | padronizada (12 estagios + sequencia) |

## Publico deste projeto

- **Mariana Friedrich** — advogada, dona do escritorio. Usa a planilha e os
  resumos para decisoes de followup e fechamento.
- **Equipe comercial** — recebe os alertas de leads parados, no-shows e
  oportunidades de reagendamento.
- **Thiago** — desenvolvedor/operador. Configura as skills, roda o pipeline,
  evolui a automacao.

## Principios

1. **Um cliente = um arquivo.** Mesmo que apareca em 3 canais diferentes.
2. **CRM mais avancado.** Sempre classificar pelo estagio mais avancado comprovado.
3. **Nunca inventar.** So registrar o que a conversa comprova.
4. **Fonte da verdade.** `_memoria/crm_definicoes.md` define os 12 CRMs;
   `_memoria/indice_clientes.md` indexa todos os clientes.
