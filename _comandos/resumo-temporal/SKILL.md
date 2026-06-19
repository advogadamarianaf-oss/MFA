---
name: resumo-temporal
description: Gera um resumo das conversas de cada lead/cliente por janelas de tempo (primeiras 24h, 7 dias, 15 dias e 30 dias) a partir dos arquivos em clientes/. Escreve um arquivo por cliente na pasta "Resumos", nomeado "Resumo - Nome do Cliente.md". Use quando o usuário pedir resumos temporais/por período, linha do tempo resumida, ou "resumo de 24h/7/15/30 dias" dos clientes.
---

# Resumo Temporal — por janelas de tempo

Skill do escritório de **Advocacia Médica & Odontológica** (Mariana Friedrich).
Lê o arquivo de cada cliente (`clientes/<nome>.md`) e produz um **mini resumo** das
conversas em janelas **acumuladas a partir do início da conversa**: primeiras 24h,
primeiros 7 dias, primeiros 15 dias e primeiros 30 dias. Grava um arquivo por cliente
na pasta **Resumos**.

Sempre responder em **português**.

## Quando usar
O usuário pede resumos por período/tempo dos clientes (um, vários ou todos).

## Pré-requisitos
- Arquivos de cliente já existentes em `clientes/<nome>.md` (gerados pela skill
  `analisar-lead`). Esta skill **não** acessa o navegador — trabalha só sobre os
  arquivos locais.
- Pasta `Resumos/` na raiz do projeto (criar se não existir).

## Entrada e janelas
- **Marco zero (t0)** = data da primeira mensagem/evento da conversa (campo
  "Conversa iniciada em" / primeiro item da Linha do tempo do arquivo do cliente).
- Janelas **acumuladas** a partir de t0:
  - **Primeiras 24h** — t0 até t0+1 dia.
  - **Primeiros 7 dias** — t0 até t0+7 dias.
  - **Primeiros 15 dias** — t0 até t0+15 dias.
  - **Primeiros 30 dias** — t0 até t0+30 dias.
- Se uma janela ainda não decorreu (conversa mais recente que a janela) ou não houve
  novas interações em relação à janela anterior, registrar explicitamente
  (ex: "Sem novas interações; conversa ainda dentro dos primeiros 7 dias").

## Passo a passo (por cliente)
1. Ler `clientes/<nome>.md` (seção "Conversa (registro)" / "Linha do tempo" e o
   restante para contexto).
2. Identificar t0 e classificar cada evento/mensagem na(s) janela(s) acumulada(s).
3. Escrever um **mini resumo de 2 a 5 linhas por janela**: o que aconteceu até ali
   (mensagens-chave, respostas do lead, mudanças de CRM, falhas de entrega, no-show,
   agendamentos). Acumulado — cada janela inclui o que veio antes, destacando o que
   é novo no período.
4. Salvar em `Resumos/Resumo - <Nome do Cliente>.md` (nome com o nome de exibição do
   cliente; sobrescrever se já existir).

## Formato do arquivo de saída
```
# Resumo Temporal — <Nome do Cliente>

> Base: clientes/<arquivo>.md · Conversa iniciada em <t0> · Gerado em <AAAA-MM-DD>
> CRM atual: <CRM> · Sequência: <sequência>

## Primeiras 24h (até <t0+1d>)
- <mini resumo>

## Primeiros 7 dias (até <t0+7d>)
- <mini resumo / novidades>

## Primeiros 15 dias (até <t0+15d>)
- <mini resumo / novidades ou "sem novas interações...">

## Primeiros 30 dias (até <t0+30d>)
- <mini resumo / novidades ou "janela ainda não decorrida...">
```

## Execução em paralelo (vários clientes)
- Para vários clientes, disparar **um agente por cliente** na mesma rodada (em paralelo).
  Cada agente lê o arquivo do seu cliente e escreve só o seu `Resumos/Resumo - <Nome>.md`
  (sem conflito, pois cada um grava um arquivo distinto).
- Ao final, o orquestrador apresenta os arquivos gerados e uma confirmação.

## Regras
- Nunca inventar dados fora do arquivo do cliente.
- Datas das janelas sempre relativas ao t0 daquele cliente (não à data de hoje).
- Resumos curtos e objetivos (2–5 linhas por janela).
