---
title: Integracoes
layout: default
nav_order: 9
description: "APIs e ferramentas integradas — Atende Direito, Google Sheets, Claude in Chrome e MCP"
---

# Integracoes
{: .no_toc }

O sistema se conecta com 3 plataformas externas e usa 1 extensao de navegador.
{: .fs-6 .fw-300 }

## Indice
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## 1. Atende Direito (API REST)

**Base URL:** `https://app.atendedireito.com.br/api`
**Autenticacao:** Bearer token (`MINHA_API_KEY` no `.env`)
**Documentacao completa:** `APIdoc.md` na raiz do projeto (100+ endpoints)

### Endpoints Usados

| Endpoint | Metodo | Uso no projeto |
|:---------|:-------|:---------------|
| `/subscribers` | GET | Listar todos os leads (paginado, 100/pag) |
| `/subscriber/chat-messages` | GET | Baixar conversa completa de um lead |
| `/subscriber` | PUT | Atualizar tags, campos, board |
| `/subscriber/labels` | POST | Adicionar labels (ex: "CRM ALTERADO PELA IA") |

### Parametros importantes

```
GET /subscribers?limit=100&page=1
GET /subscriber/chat-messages?user_ns=f175863uXXXXX&include_bot=1&include_system=1&include_note=1&limit=100&page=1
```

- `include_system=1` traz eventos como "Moved to board: X" (essencial para CRM)
- `include_bot=1` traz mensagens automaticas do fluxograma
- `include_note=1` traz notas internas dos atendentes

### Boards = CRM

Os boards do Atende Direito correspondem aos 12 CRMs. O evento `"Moved to board: <nome>"`
nas system messages indica mudanca de estagio. O ultimo evento determina o CRM atual.

### Canais (Flows)

| Flow ID | Canal |
|:--------|:------|
| `f175863` | Comercial - API OFICIAL |
| `f270363` | Comercial 2 - API OFICIAL |
| `f229905` | SAC |

O `user_ns` de cada subscriber comeca com o flow ID (ex: `f175863u12345`).

---

## 2. Google Sheets (API v4)

**Planilha:** RELATORIOS COMERCIAIS NOVA
**ID:** `1BodcfEOso5pooeOSnA2Gq-OJVQtVcjleIEAfjvwM5IM`
**Autenticacao:** Conta de servico (`gcred.json`)
**Escopo:** `https://www.googleapis.com/auth/spreadsheets` (leitura + escrita)

### Abas e Colunas

| Aba | Chave de casamento | Colunas RESUMO | Inicio |
|:----|:-------------------|:---------------|:-------|
| CAMPANHA META | TELEFONE (col C) | M, N, O, P | M2 |
| CAMPANHA GOOGLE | ATENDE DIREITO ID | G, H, I, J | G2 |
| ORGANICO | ATENDE DIREITO ID | G, H, I, J | G2 |
| MANYCHAT | ATENDE DIREITO ID | F, G, H, I | F2 |
| REUNIOES & FECHAMENTOS | TELEFONE | V, W, X, Y | V2 |

### Como funciona a escrita

1. `pipeline_diario.py` monta um array 2D de resumos (1 linha por lead, 4 colunas)
2. Chama `sheets.values().update()` com `valueInputOption: RAW`
3. Escreve o bloco inteiro de uma vez, a partir da celula de inicio

### Configuracao

1. Criar conta de servico no Google Cloud Console
2. Baixar credenciais JSON → salvar como `gcred.json`
3. Compartilhar a planilha com o email da conta de servico como **Editor**
4. Instalar: `pip install google-auth google-api-python-client`

---

## 3. Claude in Chrome (extensao)

**Para que serve:** Permite que o Claude Code controle o navegador — buscar leads
no Atende Direito, ler conversas, preencher a planilha.

### Ferramentas usadas

| Ferramenta | Uso |
|:-----------|:----|
| `tabs_context_mcp` | Listar abas existentes no grupo MCP |
| `tabs_create_mcp` | Criar aba nova (1 por lead em paralelo) |
| `navigate` | Ir para URL do Atende Direito ou Google Sheets |
| `get_page_text` | Extrair texto completo da pagina (conversa) |
| `read_page` | Ler arvore de acessibilidade (elementos interativos) |
| `find` | Encontrar campo de busca, botoes |
| `browser_batch` | Executar sequencia de acoes (clicar, digitar, scroll) |
| `javascript_tool` | Executar JS na pagina (extrair dados do DOM) |

### Permissoes configuradas

Arquivo: `.claude/settings.local.json`

```json
{
  "permissions": {
    "allow": [
      "mcp__Claude_in_Chrome__tabs_context_mcp",
      "mcp__Claude_in_Chrome__browser_batch",
      "mcp__Claude_in_Chrome__get_page_text",
      "mcp__Claude_in_Chrome__read_page",
      "mcp__Claude_in_Chrome__javascript_tool",
      "mcp__Claude_in_Chrome__navigate",
      "mcp__Claude_in_Chrome__read_network_requests"
    ]
  }
}
```

---

## 4. Atende Direito MCP (servidor dedicado)

Alem da API REST, o projeto tem um servidor MCP (`atende-direito`) que expoe
endpoints da API como ferramentas nativas do Claude Code.

### Ferramentas disponiveis

| Ferramenta | Descricao |
|:-----------|:----------|
| `mcp__atende-direito__list_endpoints` | Lista todos os endpoints disponiveis |
| `mcp__atende-direito__get_endpoint_schema` | Retorna o schema de um endpoint |
| `mcp__atende-direito__execute_request` | Executa uma requisicao na API |

Isso permite consultar a API sem sair do Claude Code (sem scripts externos).

---

## Diagrama de Integracoes

```
+------------------+
|     Usuario      |
| (Claude Code)    |
+--------+---------+
         |
    +----+----+----+----+
    |         |         |
    v         v         v
+-------+ +-------+ +--------+
| Atende| | Google | | Claude |
| API   | | Sheets | | Chrome |
| REST  | | API v4 | | (ext)  |
+-------+ +-------+ +--------+
    |         |         |
    v         v         v
 leads     planilha   navegador
 msgs      resumos    Atende Dir
 boards    (5 abas)   Google Sheets
```
