---
title: Estrutura de Arquivos
layout: default
nav_order: 4
nav_title: Arquivos
description: "Mapa completo de pastas e arquivos do projeto MFA"
---

# Estrutura de Arquivos

## Arvore do Projeto

```
Analise de Mensagens/
|
+-- CLAUDE.md                          # Instrucoes do projeto para o Claude Code
+-- README.md                          # Visao geral rapida
+-- APIdoc.md                          # Referencia da API do Atende Direito (100+ endpoints)
+-- .env                               # Chaves de API (NAO versionar)
+-- gcred.json                         # Credenciais Google Service Account (NAO versionar)
|
+-- _memoria/                          # MEMORIA CENTRAL (fonte da verdade)
|   +-- crm_definicoes.md              # Os 12 CRMs + regras de classificacao
|   +-- indice_clientes.md             # Indice: todos os clientes + CRM atual + data
|
+-- _templates/                        # Modelos reutilizaveis
|   +-- prompt_agente_analise.md       # Prompt para agentes de analise no navegador
|
+-- clientes/                          # UM ARQUIVO POR CLIENTE
|   +-- _MODELO_CLIENTE.md             # Template (copiar ao criar cliente novo)
|   +-- anderson-cortes.md             # Exemplo de arquivo de cliente completo
|   +-- ...                            # (149 clientes ativos)
|
+-- Resumos/                           # Resumos temporais por cliente
+-- entrada/                           # Dados brutos aguardando processamento
|   +-- processadas/                   # Conversas ja analisadas
|   +-- api/                           # Dados baixados da API
|
+-- _comandos/                         # Skills do Claude Code
|   +-- analisar-lead/SKILL.md
|   +-- resumo-temporal/SKILL.md
|   +-- processar-planilha/SKILL.md
|   +-- processar-planilha-api/SKILL.md
|
+-- Scripts de automacao:
|   +-- pipeline_diario.py             # Pipeline tudo-em-um
|   +-- processar_leads.py             # Atualiza boards CRM via API
|   +-- escrever_planilha.py           # Escreve blocos TSV na planilha
|
+-- Scripts auxiliares (PowerShell):
|   +-- atende_pull.ps1                # Baixa todos os subscribers + mensagens
|   +-- atende_mensagens.ps1           # Baixa so mensagens
|
+-- Atalhos (Batch - Windows):
    +-- RODAR - Pipeline diario (tudo).bat
    +-- AGENDAR todos os dias 13h.bat
```

## Arquivos Sensiveis

> Estes arquivos contem credenciais ou dados pessoais e **nunca devem ser versionados**.

| Arquivo | Conteudo | Protecao |
|:--------|:---------|:---------|
| `.env` | `MINHA_API_KEY`, `MINHA_API_KEY2`, `ANTHROPIC_API_KEY` | `.gitignore` |
| `gcred.json` | Credenciais da conta de servico Google | `.gitignore` |
| `clientes/*.md` | Dados pessoais de leads (telefone, conversa) | `.gitignore` |
| `_memoria/indice_clientes.md` | Nomes reais de clientes | `.gitignore` |

## Convencoes de Nomeacao

| Tipo | Padrao | Exemplo |
|:-----|:-------|:--------|
| Arquivo de cliente | `nome-em-minusculas-com-hifens.md` | `anderson-cortes.md` |
| Resumo temporal | `Resumo - Nome do Cliente.md` | `Resumo - Anderson Cortes.md` |
| Dados da API | `p001.json` (paginado) ou `<user_ns>.json` | `f175863u12345.json` |
| Blocos TSV | `paste_<aba>.tsv` | `paste_CAMPANHA_META.tsv` |
