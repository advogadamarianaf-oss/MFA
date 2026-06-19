# Pipeline Diario

O `pipeline_diario.py` e o script de automacao principal. Roda na maquina do
usuario (sem Claude), agendado para todos os dias as 13h via Agendador de Tarefas
do Windows.

## O que faz (em sequencia)

```
1. Le credenciais do .env (MINHA_API_KEY) e gcred.json
         |
2. Baixa TODOS os subscribers do Atende Direito
   (paginado, 100 por pagina)
   -> indexa por user_ns e por telefone
         |
3. Le cada aba da planilha via Google Sheets API
   (CAMPANHA META, CAMPANHA GOOGLE, ORGANICO, MANYCHAT, REUNIOES & FECHAMENTOS)
         |
4. Para cada lead de cada aba:
   a) Casa por telefone ou user_ns (conforme a aba)
   b) Baixa as mensagens da conversa (GET /subscriber/chat-messages)
   c) Analisa por janela temporal (24h, 7d, 15d, 30d):
      - Conta mensagens de entrada/saida
      - Extrai CRM real (ultimo "Moved to board:")
      - Detecta falhas de entrega (WhatsApp Error 131049)
      - Detecta reuniao, atendimento humano, fluxograma
   d) Gera 4 textos de resumo (max 250 caracteres cada)
         |
5. Escreve os resumos nas colunas corretas de cada aba
   via Google Sheets API (valueInputOption: RAW)
         |
6. Loga tudo em pipeline_log.txt
```

## Como Executar

### Manualmente

```batch
RODAR - Pipeline diario (tudo).bat
```

Ou direto:

```powershell
python pipeline_diario.py
```

### Agendamento Automatico

```batch
AGENDAR todos os dias 13h.bat
```

Cria uma tarefa no Agendador de Tarefas do Windows (`schtasks`) que roda
`pipeline_diario.py` todos os dias as 13:00.

## Dependencias

```
pip install google-auth google-api-python-client
```

## Credenciais Necessarias

| Credencial | Arquivo | Para que |
|------------|---------|----------|
| `MINHA_API_KEY` | `.env` | API do Atende Direito (Bearer token) |
| Google Service Account | `gcred.json` | Leitura/escrita na planilha Google |

A conta de servico Google precisa estar compartilhada como **Editor** na planilha.

## Logica de Casamento (matching)

Cada aba usa um campo diferente para encontrar o subscriber:

| Aba | Campo na planilha | Logica |
|-----|-------------------|--------|
| CAMPANHA META | TELEFONE | Normaliza digitos, remove DDI 55, compara ultimos 10 |
| CAMPANHA GOOGLE | ATENDE DIREITO ID | Compara user_ns diretamente |
| ORGANICO | ATENDE DIREITO ID | Compara user_ns diretamente |
| MANYCHAT | ATENDE DIREITO ID | Compara user_ns (leads com @ sem ID ficam em branco) |
| REUNIOES & FECHAMENTOS | TELEFONE | Mesma logica da CAMPANHA META |

## Logica de Resumo (por janela)

Para cada lead com conversa encontrada:

1. **t0** = timestamp da primeira mensagem
2. **Janelas**: t0+1d, t0+7d, t0+15d, t0+30d
3. Para cada janela, analisa mensagens ate o cutoff:
   - `boards[]` = todos os "Moved to board: X" ate ali
   - `crm` = ultimo board (ou "LEAD ENTROU NO COMERCIAL" se nenhum)
   - `nin` / `nout` = contagem de mensagens de entrada/saida
   - `errs` = contagem de falhas de entrega
   - `reun` / `hum` / `flux` = flags de reuniao/humano/fluxograma
4. Monta texto com:
   - Origem + cidade + perfil do formulario
   - Acao do lead (respondeu X vezes, nao respondeu, etc.)
   - CRM atual na janela
   - Alertas de falha de entrega

## Perfil do Formulario

O pipeline extrai campos personalizados (user_fields) do subscriber:

| Campo | O que representa |
|-------|------------------|
| Tem clinica / dono ou gestor | Tipo de clinica (medica, odonto, estetica, multi) |
| Recebeu processos | Se ja foi processado (defesa vs prevencao) |
| Quantas clinicas / CNPJ | Escala do negocio (2-4, 5-10, +1 CNPJ) |
| Quantos profissionais | Numero de profissionais |
| Cidade/Estado | Localizacao |

## Saida

- **Planilha**: colunas RESUMO preenchidas em todas as abas
- **Log**: `pipeline_log.txt` com timestamp, contadores e erros
- **Console**: progresso em tempo real

Exemplo de log:
```
=== execucao 19/06/2026 13:00:15 ===
Baixando subscribers...
  subscribers: 847
[CAMPANHA META] 142 linhas escritas em M2 (568 celulas).
[CAMPANHA GOOGLE] 87 linhas escritas em G2 (348 celulas).
[ORGANICO] 53 linhas escritas em G2 (212 celulas).
[MANYCHAT] 31 linhas escritas em F2 (124 celulas).
[REUNIOES & FECHAMENTOS] 28 linhas escritas em V2 (112 celulas).

Concluido em 19/06 13:04. Total de celulas: 1364. Leads analisados: 312.
```
