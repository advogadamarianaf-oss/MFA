---
title: Integracoes
layout: default
nav_order: 9
description: "APIs e ferramentas integradas — Atende Direito, Google Sheets, Chrome e MCP"
---

# Integracoes

O sistema se conecta com 3 plataformas externas e 1 extensao de navegador.

---

## 1. Atende Direito (API REST)

**Base URL:** `https://app.atendedireito.com.br/api`
**Auth:** Bearer token (`MINHA_API_KEY`)

### Endpoints usados

| Endpoint | Metodo | Uso |
|:---------|:-------|:----|
| `/subscribers` | GET | Listar leads (paginado, 100/pag) |
| `/subscriber/chat-messages` | GET | Baixar conversa de um lead |
| `/subscriber` | PUT | Atualizar tags, campos, board |
| `/subscriber/labels` | POST | Adicionar labels |

### Parametros importantes

```
GET /subscribers?limit=100&page=1
GET /subscriber/chat-messages?user_ns=f175863uXXXXX
    &include_bot=1&include_system=1&include_note=1&limit=100&page=1
```

- `include_system=1` — eventos "Moved to board: X" (essencial para CRM)
- `include_bot=1` — mensagens automaticas do fluxograma
- `include_note=1` — notas internas dos atendentes

### Canais (Flows)

| Flow ID | Canal |
|:--------|:------|
| `f175863` | Comercial - API OFICIAL |
| `f270363` | Comercial 2 - API OFICIAL |
| `f229905` | SAC |

---

## 2. Google Sheets (API v4)

**Planilha:** RELATORIOS COMERCIAIS NOVA
**Auth:** Conta de servico (`gcred.json`)

### Abas e colunas

| Aba | Chave | Colunas RESUMO | Inicio |
|:----|:------|:---------------|:-------|
| CAMPANHA META | TELEFONE (col C) | M, N, O, P | M2 |
| CAMPANHA GOOGLE | ATENDE DIREITO ID | G, H, I, J | G2 |
| ORGANICO | ATENDE DIREITO ID | G, H, I, J | G2 |
| MANYCHAT | ATENDE DIREITO ID | F, G, H, I | F2 |
| REUNIOES & FECHAMENTOS | TELEFONE | V, W, X, Y | V2 |

### Setup

1. Criar conta de servico no Google Cloud Console
2. Baixar credenciais JSON → salvar como `gcred.json`
3. Compartilhar a planilha com o email da conta como **Editor**
4. `pip install google-auth google-api-python-client`

---

## 3. Claude in Chrome

Extensao que permite ao Claude Code controlar o navegador.

| Ferramenta | Uso |
|:-----------|:----|
| `tabs_context_mcp` | Listar abas no grupo MCP |
| `tabs_create_mcp` | Criar aba nova |
| `navigate` | Ir para URL |
| `get_page_text` | Extrair texto da pagina |
| `read_page` | Ler arvore de acessibilidade |
| `find` | Encontrar campos, botoes |
| `browser_batch` | Sequencia de acoes |
| `javascript_tool` | Executar JS na pagina |

---

## 4. Atende Direito MCP

Servidor MCP dedicado que expoe a API como ferramentas nativas do Claude Code.

| Ferramenta | Descricao |
|:-----------|:----------|
| `list_endpoints` | Lista endpoints disponiveis |
| `get_endpoint_schema` | Schema de um endpoint |
| `execute_request` | Executa requisicao na API |
