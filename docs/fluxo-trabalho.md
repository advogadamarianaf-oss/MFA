---
title: Fluxo de Trabalho
layout: default
nav_order: 6
nav_title: Fluxo
description: "Como analisar leads passo a passo — individual, em paralelo e em lote"
---

# Fluxo de Trabalho

## Fluxo Principal

```
1. Identificar lead(s) a analisar
         |
2. Buscar conversa no Atende Direito (navegador ou API)
         |
3. Ler conversa completa (formulario + linha do tempo)
         |
4. Classificar CRM (1 dos 12) + sequencia
         |
5. Criar/atualizar clientes/<nome>.md
         |
6. Atualizar _memoria/indice_clientes.md
         |
7. [Opcional] Gerar resumo temporal
```

## Analise Individual (1 lead)

1. O usuario pede: "analisa o lead Fulano"
2. O Claude abre o Atende Direito no navegador via Claude in Chrome
3. Busca o lead por nome em Chat Ao Vivo > campo "Procurar"
4. Abre a conversa, rola ate o topo, extrai todo o texto
5. Captura dados do painel: telefone, email, cidade, origem, data, tag CRM
6. Classifica o CRM + sequencia conforme `crm_definicoes.md`
7. Cria/atualiza o arquivo `clientes/<nome>.md` a partir do modelo
8. Atualiza a linha do lead em `indice_clientes.md`
9. Apresenta resumo + proximo passo recomendado

## Analise em Paralelo (2+ leads)

1. O usuario passa uma lista de nomes: "analisa Maria, Joao e Ana"
2. O orquestrador cria uma aba por lead no navegador (max 4-5 simultaneos)
3. Dispara um agente por lead, cada um com seu tabId
4. Cada agente executa o fluxo individual na sua aba
5. Agentes retornam a linha do indice (NAO editam o indice diretamente)
6. O orquestrador consolida e atualiza o indice uma vez, sequencialmente
7. Apresenta tabela-resumo: Lead | CRM | Sequencia | Proximo passo

## Processamento de Planilha (lotes de 5)

```
1. Ler a planilha Google (aba CAMPANHA META)
         |
2. Selecionar proximos 5 nomes nao processados
         |
3. Agente leitor (sequencial, 1 navegador):
   busca cada nome, extrai conversa completa
         |
4. 5 agentes escritores (paralelo, so arquivos):
   cria clientes/<nome>.md + Resumos/<Nome>.md
         |
5. Orquestrador consolida indice
         |
6. Orquestrador preenche planilha via navegador
         |
7. Apresenta tabela-resumo, oferece proximo lote
```

## Leads em Multiplos Canais

O mesmo lead pode aparecer em ate 3 canais (Comercial, Comercial 2, SAC).

> Sempre conferir por telefone se ha mais de um resultado ao buscar um lead.

### Regras de consolidacao

| Regra | Descricao |
|:------|:----------|
| Um cliente = um arquivo | Nunca criar 2 arquivos para a mesma pessoa |
| Linha do tempo unica | Ordenada por data/hora, marcando canal de cada trecho |
| CRM mais avancado | De qualquer canal |
| Registrar todos os user_ns | Para rastreabilidade |
| Conferir por telefone | Verificar se ha mais de 1 resultado |

## Resumo Temporal

Para cada cliente ja analisado, e possivel gerar um resumo por janelas de tempo:

| Janela | Periodo |
|:-------|:--------|
| **Primeiras 24h** | t0 ate t0 + 1 dia |
| **Primeiros 7 dias** | t0 ate t0 + 7 dias |
| **Primeiros 15 dias** | t0 ate t0 + 15 dias |
| **Primeiros 30 dias** | t0 ate t0 + 30 dias |

Onde **t0** = data da primeira mensagem da conversa. Cada janela e **acumulada**.
