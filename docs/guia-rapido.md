---
title: Guia Rapido
layout: default
nav_order: 10
description: "Setup inicial, operacoes do dia a dia e troubleshooting"
---

# Guia Rapido

## Pre-requisitos

| Item | Descricao |
|:-----|:----------|
| Python 3.12+ | Scripts de automacao |
| Claude Code | CLI com extensao Claude in Chrome |
| Atende Direito | Conta com acesso a API |
| Google Cloud | Conta de servico (Sheets API) |
| Chrome | Extensao Claude in Chrome |

## Setup

### 1. Credenciais

```env
# .env na raiz do projeto
MINHA_API_KEY=sua_chave_api_atende_direito
ANTHROPIC_API_KEY=sua_chave_anthropic
```

Baixar credenciais Google → salvar como `gcred.json`.

### 2. Dependencias

```bash
pip install google-auth google-api-python-client
```

### 3. Claude in Chrome

1. Instalar a extensao no Chrome
2. Logar no Atende Direito e Google Sheets
3. Conectar a extensao ao Claude Code

### 4. Pipeline diario

```batch
AGENDAR todos os dias 13h.bat
```

## Operacoes do Dia a Dia

### Analisar leads

```
> analisa o lead Anderson Cortes
> analisa Maria, Joao e Ana
```

### Pipeline diario

```
> roda o pipeline
```

Ou clique duplo em `RODAR - Pipeline diario (tudo).bat`.

### Processar planilha

```
> processa a planilha
> continua o proximo lote
```

### Resumos temporais

```
> faz o resumo temporal de todos os clientes
> gera resumo 24h/7/15/30 do Anderson
```

### Consultar cliente

```
> como esta o lead Anderson Cortes?
```

### Reclassificar CRM

```
> reclassifica o CRM do Anderson para Aguardando Fechamento
```

## Troubleshooting

| Problema | Solucao |
|:---------|:--------|
| "MINHA_API_KEY ausente" | Verificar `.env` na raiz |
| "gcred.json nao encontrado" | Baixar credenciais Google |
| "Faltam libs" | `pip install google-auth google-api-python-client` |
| Lead nao localizado | Tentar variacoes do nome |
| "WhatsApp Error 131049" | Numero invalido; alerta na planilha |
| Planilha sem permissao | Compartilhar com email da conta de servico |
| Chrome nao conecta | Verificar extensao + Atende Direito logado |
| Pipeline nao roda 13h | Checar Agendador de Tarefas do Windows |

## Glossario

| Termo | Significado |
|:------|:------------|
| **CRM** | Estagio do lead no funil (1 de 12) |
| **Sequencia** | Posicao detalhada dentro do CRM |
| **user_ns** | ID unico do subscriber no Atende Direito |
| **Board** | Quadro no Atende Direito (= CRM) |
| **Flow** | Fluxo/bot (Comercial, Comercial 2, SAC) |
| **t0** | Data da primeira mensagem |
| **Janela temporal** | Periodo acumulado a partir de t0 |
| **Lead Ads** | Lead de anuncio Meta (Facebook/Instagram) |
