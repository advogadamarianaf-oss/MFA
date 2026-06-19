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
|   +-- bruna-araujo.md                #   ... (149 clientes ativos)
|   +-- ...
|
+-- Resumos/                           # Resumos temporais por cliente
|   +-- Resumo - Anderson Cortes.md    # Janelas: 24h, 7d, 15d, 30d
|   +-- ...
|
+-- entrada/                           # Dados brutos aguardando processamento
|   +-- processadas/                   # Conversas ja analisadas
|   +-- api/                           # Dados baixados da API
|       +-- subscribers/               # JSONs paginados (p001.json ... p0XX.json)
|       +-- messages/                  # Threads de mensagens por lead (JSON)
|       +-- transcripts/               # Transcricoes processadas
|       +-- manifest.tsv               # Manifesto de leads com contatos
|       +-- paste_*.tsv                # Blocos TSV prontos para escrita na planilha
|       +-- analysis_by_ns.json        # Resultados de analise indexados por user_ns
|
+-- _comandos/                         # Skills do Claude Code
|   +-- analisar-lead/SKILL.md         # Analisa lead(s) no Atende Direito
|   +-- resumo-temporal/SKILL.md       # Gera resumos por janela temporal
|   +-- processar-planilha/SKILL.md    # Processa planilha em lotes de 5
|   +-- processar-planilha-api/SKILL.md # Pipeline API automatico
|
+-- Scripts de automacao:
|   +-- pipeline_diario.py             # Pipeline tudo-em-um (API + resumo + escrita)
|   +-- processar_leads.py             # Atualiza boards CRM via API
|   +-- escrever_planilha.py           # Escreve blocos TSV na planilha via API
|   +-- create_xlsx.py                 # Gera XLSX a partir dos dados
|   +-- process_subscribers.py         # Processa dados de subscribers
|
+-- Scripts auxiliares (PowerShell):
|   +-- atende_pull.ps1                # Baixa todos os subscribers + mensagens
|   +-- atende_mensagens.ps1           # Baixa so mensagens
|   +-- carregar_clipboard.ps1         # Carrega resumos no clipboard
|   +-- baixar_alvos_msgs.ps1          # Baixa mensagens de alvos especificos
|
+-- Atalhos (Batch - Windows):
|   +-- RODAR - Pipeline diario (tudo).bat
|   +-- RODAR - Atende API (amostra).bat
|   +-- AGENDAR todos os dias 13h.bat  # Cria tarefa agendada no Windows
|   +-- ...
|
+-- Pastas auxiliares:
    +-- Auditorias/                     # Relatorios de auditoria
    +-- ErrorLeads/                     # Leads com erro no processamento
    +-- Perguntas_Conversao/            # Analise de perguntas de conversao
    +-- Reclassificacao_CRM/            # Trabalho de reclassificacao
    +-- _auditoria_canal_duplo/         # Auditoria de leads em multiplos canais
```

## Arquivos Sensíveis (NAO versionar)

| Arquivo | Conteudo | Protecao |
|---------|----------|----------|
| `.env` | `MINHA_API_KEY`, `MINHA_API_KEY2`, `ANTHROPIC_API_KEY` | Adicionar ao `.gitignore` |
| `gcred.json` | Credenciais da conta de servico Google | Adicionar ao `.gitignore` |

## Convencoes de Nomeacao

- **Arquivos de clientes**: `nome-em-minusculas-com-hifens.md` (ex: `anderson-cortes.md`)
- **Resumos**: `Resumo - Nome do Cliente.md` (nome de exibicao, com maiusculas)
- **Dados da API**: `p001.json`, `p002.json` (paginados); `<user_ns>.json` (por lead)
- **Blocos TSV**: `paste_<aba>.tsv` (ex: `paste_CAMPANHA_META.tsv`)
