# MFA — Analise de Mensagens

Sistema de analise, classificacao e acompanhamento de leads para o escritorio de
**Advocacia Medica & Odontologica** (Mariana Friedrich).

Combina automacao por IA (Claude Code), API do Atende Direito e Google Sheets
para transformar conversas brutas em inteligencia comercial acionavel.

## O que faz

- **Analisa conversas** de leads no Atende Direito (via navegador ou API)
- **Classifica cada lead** em 1 dos 12 estagios do funil (CRM) + sequencia detalhada
- **Gera resumos temporais** por janelas de 24h, 7, 15 e 30 dias
- **Preenche a planilha** de relatorios comerciais automaticamente (pipeline diario 13h)
- **Consolida leads multicanal** (Comercial, Comercial 2, SAC) em um unico perfil

## Stack

| Componente | Tecnologia |
|------------|------------|
| CRM / Chat | Atende Direito (API REST + WhatsApp Business) |
| Planilha | Google Sheets (API v4, conta de servico) |
| IA | Claude Code + Claude in Chrome (analise + navegacao) |
| Scripts | Python 3.12, PowerShell, Batch |
| Dados | Markdown (clientes), JSON (API), TSV (blocos de escrita) |

## Inicio Rapido

```bash
# 1. Configurar credenciais
#    .env  -> MINHA_API_KEY, ANTHROPIC_API_KEY
#    gcred.json -> conta de servico Google

# 2. Instalar dependencias
pip install google-auth google-api-python-client

# 3. Rodar o pipeline
python pipeline_diario.py

# 4. Ou analisar leads via Claude Code
#    > analisa o lead Anderson Cortes
#    > processa a planilha
```

## Estrutura do Projeto

```
_memoria/           # Fonte da verdade (CRMs + indice de clientes)
_templates/         # Modelos de prompt e arquivo
clientes/           # Um arquivo .md por cliente (149 ativos)
Resumos/            # Resumos temporais por janela
entrada/api/        # Dados da API (subscribers, messages)
_comandos/          # Skills do Claude Code
docs/               # Documentacao completa
```

## Documentacao

Documentacao tecnica completa em [`docs/`](docs/README.md):

- [Visao Geral](docs/visao-geral.md) — problema, solucao, resultados
- [Arquitetura](docs/arquitetura.md) — componentes, fluxo de dados, integraccoes
- [Estrutura de Arquivos](docs/estrutura-arquivos.md) — mapa completo do projeto
- [CRM — Os 12 Estagios](docs/crm-definicoes.md) — definicoes e regras de classificacao
- [Fluxo de Trabalho](docs/fluxo-trabalho.md) — como analisar leads passo a passo
- [Skills e Comandos](docs/skills.md) — referencia das 4 skills do Claude Code
- [Pipeline Diario](docs/pipeline-diario.md) — automacao: API + resumos + planilha
- [Integracoes](docs/integracoes.md) — Atende Direito, Google Sheets, Chrome
- [Guia Rapido](docs/guia-rapido.md) — setup e primeiros passos

## Os 12 CRMs

| # | Estagio | Descricao curta |
|---|---------|-----------------|
| 1 | LEAD ENTROU NO COMERCIAL | Novo, sem qualificacao |
| 2 | NAO DEU 1a RESPOSTA | Follow-ups sem retorno |
| 3 | RECEBEU FLUXOGRAMA | Sequencia automatica enviada |
| 4 | ATENDIMENTO HUMANO | Escalado para atendente real |
| 5 | Aguardando Reuniao | Interesse mas sem data |
| 6 | REUNIAO AGENDADA (Clientes) | Data/hora confirmados |
| 7 | REUNIAO AGENDADA (Defesa) | Caso de defesa profissional |
| 8 | NAO Compareceu a Reuniao | No-show |
| 9 | Aguardando Fechamento | Pos-reuniao, avaliando proposta |
| 10 | FECHAMENTO | Negociacao final ativa |
| 11 | Contrato Assinado | Cliente fechado |
| 12 | Lead Desqualificado | Fora do perfil ou desistiu |

## Licenca

Projeto privado — uso exclusivo do escritorio Mariana Friedrich Advocacia.
