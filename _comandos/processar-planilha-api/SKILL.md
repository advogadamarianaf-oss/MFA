---
name: processar-planilha-api
description: Atualiza os resumos (24h/7/15/30) de todas as abas da planilha RELATORIOS COMERCIAIS NOVA usando a API do Atende Direito + Google Sheets API. Tem um modo automatico (pipeline_diario.py, data-driven, agendado para as 13h) e um modo de analise profunda das conversas (agentes, sob demanda). Use quando o usuario disser que tem leads novos, pedir para atualizar/rodar a planilha, ou processar as abas.
---

# Processar Planilha por API — Atende Direito (automatico)

Escritorio de Advocacia Medica & Odontologica (Mariana Friedrich). Responda em portugues.

## Dois modos
1. **Automatico / data-driven (pipeline_diario.py)** — roda 100% na maquina do usuario, sem
   Claude. Le as abas da planilha pela Google Sheets API, baixa subscribers + conversas da API
   do Atende Direito, gera resumo data-driven (origem, perfil do formulario, CRM real pelos
   eventos "Moved to board", eventos como reuniao/no-show/falha de entrega) e escreve as colunas
   RESUMO de cada aba. **Agendado para todos os dias as 13h** (Agendador de Tarefas do Windows).
2. **Analise profunda (sob demanda, com Claude)** — agentes leem os transcripts e escrevem
   resumos nuançados ("Miguel ofereceu remarcar", objecao de preco, etc.). Use quando o usuario
   quiser qualidade extra em leads especificos.

## Arquivos
- `.env` (MINHA_API_KEY) e `gcred.json` (conta de servico Google, compartilhada como Editor na planilha).
- `pipeline_diario.py` — o tudo-em-um. `RODAR - Pipeline diario (tudo).bat` executa.
- `AGENDAR todos os dias 13h.bat` — cria a tarefa diaria no Windows (schtasks, 13:00).
- `pipeline_log.txt` — log das execucoes.
- Para analise profunda: gerar_transcripts.py / transcripts_ns + agentes -> analise/*.json.

## Abas tratadas (e onde escrever)
- CAMPANHA META: casa por TELEFONE; RESUMO em M:P.
- CAMPANHA GOOGLE: casa por ATENDE DIREITO ID (user_ns); RESUMO em G:J.
- ORGANICO: ATENDE DIREITO ID; G:J.
- MANYCHAT: ATENDE DIREITO ID; F:I (linhas com @ do Instagram, sem ID, ficam em branco).
- REUNIOES & FECHAMENTOS: casa por TELEFONE; RESUMO em V:Y.
- CAPTACAO ATIVA (prospeccao de saida) e PIXEL META ficam de fora (sem conversa / sem colunas).
O pipeline detecta as colunas pelo cabecalho (NOME/TELEFONE/ATENDE DIREITO ID/RESUMO APOS 24H),
entao se mudarem de lugar continua funcionando. Ler via Sheets API ja vem limpo (sem o problema
do "|" no nome).

## Conceitos-chave
- CRM granular = ultimo "Moved to board: X" no transcript (os boards sao os 12 CRMs). Os labels
  do subscriber sao categorias, nao os 12 CRMs.
- Casar por user_ns/telefone, NUNCA por numero de linha (leads novos entram no topo).
- Falha de entrega no WhatsApp = "WhatsApp Error 131049" (alerta importante; numero possivelmente invalido).
- O sandbox do Claude NAO tem rede; por isso a API e a escrita rodam na maquina do usuario (scripts).

## Fluxo quando o usuario pede para rodar agora
- Se quer o automatico: rodar `RODAR - Pipeline diario (tudo).bat` (ou esperar as 13h).
- Se quer analise profunda: garantir conversas baixadas (alvos atualizados), gerar transcripts,
  disparar agentes que leem e escrevem os 4 resumos por lead, remontar e escrever via API.

## Regras
- Nunca inventar dados fora da conversa; resumos <=250 char por celula, uma linha.
- Escrever so nas colunas RESUMO de cada aba.
- Sinalizar alertas: falha de entrega, no-show, reuniao agendada/perdida, objecao, fechamento.
