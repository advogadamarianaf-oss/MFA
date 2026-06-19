# Skills e Comandos

O projeto utiliza 4 skills customizadas do Claude Code. Cada skill e um comando
que pode ser invocado para executar uma operacao especifica.

## 1. `/analisar-lead`

**O que faz:** Analisa a conversa de um ou mais leads no Atende Direito e gera
resumo + classificacao CRM + sequencia.

**Quando usar:** "analisa o lead Fulano", "processa Maria, Joao e Ana",
"classifica esses clientes"

**Pre-requisitos:**
- Claude in Chrome conectado
- Atende Direito logado no navegador

**Comportamento:**
- 1 lead → executa direto
- 2+ leads → agentes em paralelo (1 por lead, max 4-5 simultaneos)
- Cada agente busca por nome, le a conversa inteira, classifica CRM
- Cria/atualiza `clientes/<nome>.md`
- Agentes NAO editam o indice (evita conflito)
- Orquestrador consolida o indice ao final

**Saida:** Arquivo do cliente + tabela-resumo (Lead | CRM | Sequencia | Proximo passo)

---

## 2. `/resumo-temporal`

**O que faz:** Gera resumo por janelas de tempo (24h, 7d, 15d, 30d) a partir
dos arquivos em `clientes/`.

**Quando usar:** "faz o resumo temporal do Anderson", "gera resumos de 24h/7/15/30 dias"

**Pre-requisitos:**
- Arquivo do cliente ja existente em `clientes/<nome>.md`
- NAO precisa de navegador (trabalha so com arquivos locais)

**Comportamento:**
- Le o arquivo do cliente, identifica t0 (primeira mensagem)
- Classifica cada evento nas 4 janelas acumuladas
- Gera mini resumo de 2-5 linhas por janela
- Salva em `Resumos/Resumo - <Nome do Cliente>.md`
- Para varios clientes, dispara agentes em paralelo

**Saida:** Arquivo de resumo com 4 secoes (24h, 7d, 15d, 30d)

---

## 3. `/processar-planilha`

**O que faz:** Processa os leads da planilha RELATORIOS COMERCIAIS NOVA (aba
CAMPANHA META) em lotes de 5, na ordem dos nomes.

**Quando usar:** "processa a planilha", "roda o proximo lote", "preenche os resumos"

**Pre-requisitos:**
- Claude in Chrome conectado
- Atende Direito + Google Sheets logados no navegador
- Planilha compartilhada com permissao de edicao

**Fluxo por lote:**

| Etapa | Quem | O que faz |
|-------|------|-----------|
| 1. Selecionar lote | Orquestrador | Proximos 5 nomes nao processados |
| 2. Ler conversas | 1 agente (sequencial) | Busca no Atende Direito, extrai texto |
| 3. Escrever arquivos | 5 agentes (paralelo) | Cria cliente.md + Resumo.md |
| 4. Consolidar indice | Orquestrador | Atualiza indice_clientes.md |
| 5. Preencher planilha | Orquestrador (navegador) | Escreve M:P via Caixa de Nome |

**Mapa da planilha (CAMPANHA META):**
- Coluna B = NOME (ordem de processamento)
- Coluna C = TELEFONE (confirmacao)
- Coluna M = RESUMO APOS 24H
- Coluna N = RESUMO APOS 7 DIAS
- Coluna O = RESUMO APOS 15 DIAS
- Coluna P = RESUMO APOS 30 DIAS

---

## 4. `/processar-planilha-api`

**O que faz:** Atualiza os resumos de TODAS as abas usando API do Atende Direito
+ Google Sheets API. Tem dois modos.

**Quando usar:** "atualiza a planilha", "roda o pipeline", "tem leads novos"

### Modo Automatico (data-driven)

- Roda 100% na maquina, sem Claude
- Script: `pipeline_diario.py`
- Agendado: todos os dias as 13h (Agendador de Tarefas do Windows)
- Le planilha via Sheets API → baixa subscribers/conversas da API → gera resumos → escreve

### Modo Analise Profunda (com Claude)

- Sob demanda, para leads especificos
- Agentes leem transcripts e escrevem resumos nuancados
- Qualidade superior (detecta objecoes, tom, contexto)

**Abas tratadas e colunas:**

| Aba | Casamento | Colunas RESUMO |
|-----|-----------|----------------|
| CAMPANHA META | Telefone | M:P |
| CAMPANHA GOOGLE | Atende Direito ID (user_ns) | G:J |
| ORGANICO | Atende Direito ID | G:J |
| MANYCHAT | Atende Direito ID | F:I |
| REUNIOES & FECHAMENTOS | Telefone | V:Y |

CAPTACAO ATIVA e PIXEL META ficam de fora (sem conversa / sem colunas de resumo).
