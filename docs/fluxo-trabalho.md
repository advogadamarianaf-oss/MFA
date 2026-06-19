# Fluxo de Trabalho

## Fluxo Principal — Analise de Lead

```
1. Identificar lead(s) a analisar
         |
2. Buscar conversa no Atende Direito
   (navegador ou API)
         |
3. Ler conversa completa
   (formulario + linha do tempo)
         |
4. Classificar CRM (1 dos 12) + sequencia
   (fonte: _memoria/crm_definicoes.md)
         |
5. Criar/atualizar clientes/<nome>.md
   (modelo: _MODELO_CLIENTE.md)
         |
6. Atualizar _memoria/indice_clientes.md
         |
7. [Opcional] Gerar resumo temporal
   (Resumos/Resumo - <Nome>.md)
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
   busca cada nome no Atende Direito,
   extrai conversa completa
         |
4. 5 agentes escritores (paralelo, so arquivos):
   cria clientes/<nome>.md + Resumos/<Nome>.md
   retorna linha do indice + 4 textos de resumo
         |
5. Orquestrador consolida indice
         |
6. Orquestrador preenche planilha via navegador:
   Caixa de Nome -> M<linha> -> digita 24h Tab 7d Tab 15d Tab 30d Enter
         |
7. Apresenta tabela-resumo, oferece proximo lote
```

## Leads em Multiplos Canais

O mesmo lead pode aparecer em ate 3 canais (Comercial, Comercial 2, SAC).

**Regras de consolidacao:**

| Regra | Descricao |
|-------|-----------|
| Um cliente = um arquivo | Nunca criar 2 arquivos para a mesma pessoa |
| Linha do tempo unica | Ordenada por data/hora, marcando canal de cada trecho |
| CRM mais avancado | De qualquer canal |
| Registrar todos os user_ns | Para rastreabilidade |
| Conferir por telefone | Ao buscar, verificar se ha mais de 1 resultado |

**Ao buscar um lead:**
1. Digitar o nome no campo "Procurar"
2. Se aparecer mais de 1 resultado (mesmo telefone, canais diferentes) → abrir TODOS
3. Consolidar as conversas em ordem cronologica
4. Marcar cada trecho com `[Comercial]`, `[Comercial 2]` ou `[SAC]`

## Template do Arquivo de Cliente

```markdown
# {Nome do Cliente}

> Atende Direito · Ultima analise: AAAA-MM-DD · Status no chat: Aberto/Finalizado
> URL/NS: {link ou NS do Usuario}

## Status
- **CRM atual:** {um dos 12 CRMs}
- **Sequencia:** {onde o lead parou no fluxo}

## Identificacao
- **Telefone/WhatsApp:** {numero}
- **E-mail:** {e-mail}
- **Cidade:** {cidade}
- **Origem:** {lead_ads, inbound_webhook, organico...}
- **Conversa iniciada em:** {data}
- **Tipo de demanda:** {defesa / preventivo / odonto / medica...}

## Resumo
{2 a 5 frases sobre o que o lead procura, contexto e tom.}

## Proximo passo
{acao concreta recomendada ao escritorio}

## Observacoes / alertas
- {perfil, objecoes, falhas de entrega, no-show, notas internas}

## Historico de etapas
| Data | CRM | Sequencia | Observacao |
|------|-----|-----------|------------|

## Conversa (registro)
### Respostas do formulario
### Linha do tempo
### Observacao tecnica
```

## Resumo Temporal

Para cada cliente ja analisado, e possivel gerar um resumo por janelas de tempo:

- **t0** = data da primeira mensagem da conversa
- **Primeiras 24h** — t0 ate t0+1 dia
- **Primeiros 7 dias** — t0 ate t0+7 dias
- **Primeiros 15 dias** — t0 ate t0+15 dias
- **Primeiros 30 dias** — t0 ate t0+30 dias

Cada janela e **acumulada** (inclui o que veio antes, destacando o que e novo).
Arquivo gerado em `Resumos/Resumo - <Nome do Cliente>.md`.
