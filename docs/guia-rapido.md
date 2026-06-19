# Guia Rapido

## Pre-requisitos

| Item | Descricao |
|------|-----------|
| Python 3.12+ | Para rodar os scripts de automacao |
| Claude Code | CLI do Claude com extensao Claude in Chrome |
| Atende Direito | Conta com acesso a API (token) |
| Google Cloud | Conta de servico com acesso a Sheets API |
| Navegador | Chrome com extensao Claude in Chrome instalada |

## Setup Inicial

### 1. Configurar credenciais

Criar arquivo `.env` na raiz do projeto:

```env
MINHA_API_KEY=sua_chave_api_atende_direito
MINHA_API_KEY2=chave_secundaria_opcional
ANTHROPIC_API_KEY=sua_chave_anthropic
```

Baixar credenciais da conta de servico Google e salvar como `gcred.json`.

### 2. Instalar dependencias Python

```bash
pip install google-auth google-api-python-client
```

### 3. Configurar Claude in Chrome

1. Instalar a extensao Claude in Chrome no navegador
2. Logar no Atende Direito no navegador
3. Logar no Google Sheets no mesmo navegador
4. Conectar a extensao ao Claude Code

### 4. Agendar o pipeline diario

```batch
AGENDAR todos os dias 13h.bat
```

Ou manualmente via Agendador de Tarefas do Windows (schtasks, 13:00).

## Operacoes do Dia a Dia

### Analisar leads especificos

```
> analisa o lead Anderson Cortes
> analisa Maria, Joao e Ana
```

Usa a skill `/analisar-lead`. Precisa do Claude in Chrome conectado.

### Rodar o pipeline diario agora

```
> roda o pipeline
```

Ou clique duplo em `RODAR - Pipeline diario (tudo).bat`.

### Processar a planilha em lotes

```
> processa a planilha
> continua o proximo lote
```

Usa a skill `/processar-planilha`. Processa 5 leads por vez.

### Gerar resumos temporais

```
> faz o resumo temporal de todos os clientes
> gera resumo 24h/7/15/30 do Anderson
```

Usa a skill `/resumo-temporal`. Nao precisa de navegador.

### Consultar um cliente

```
> como esta o lead Anderson Cortes?
```

O Claude le `clientes/anderson-cortes.md` e `indice_clientes.md`.

### Reclassificar CRM de leads

```
> reclassifica o CRM do Anderson para Aguardando Fechamento
```

Atualiza o arquivo do cliente e o indice.

## Estrutura Minima para Funcionar

```
Analise de Mensagens/
+-- .env                    # Chaves de API
+-- gcred.json              # Credenciais Google
+-- CLAUDE.md               # Instrucoes do projeto
+-- _memoria/
|   +-- crm_definicoes.md   # Os 12 CRMs (obrigatorio)
|   +-- indice_clientes.md  # Indice de clientes
+-- _templates/
|   +-- prompt_agente_analise.md
+-- clientes/
|   +-- _MODELO_CLIENTE.md  # Template (obrigatorio)
+-- Resumos/                # Pasta para resumos temporais
+-- pipeline_diario.py      # Pipeline automatico
```

## Troubleshooting

| Problema | Solucao |
|----------|---------|
| "MINHA_API_KEY ausente" | Verificar `.env` na raiz do projeto |
| "gcred.json nao encontrado" | Baixar credenciais da conta de servico Google |
| "Faltam libs" | `pip install google-auth google-api-python-client` |
| Lead nao localizado na busca | Tentar variações do nome (so primeiro nome, sobrenome) |
| "WhatsApp Error 131049" | Numero possivelmente invalido; alerta na planilha |
| Planilha sem permissao | Compartilhar com o email da conta de servico como Editor |
| Claude in Chrome nao conecta | Verificar se a extensao esta ativa e o Atende Direito logado |
| Pipeline nao roda as 13h | Verificar tarefa no Agendador de Tarefas do Windows |

## Glossario

| Termo | Significado |
|-------|-------------|
| **CRM** | Estagio macro do lead no funil (1 de 12) |
| **Sequencia** | Posicao detalhada dentro do CRM |
| **user_ns** | Identificador unico do subscriber no Atende Direito |
| **Board** | Quadro/coluna no Atende Direito (= CRM) |
| **Flow** | Fluxo/bot do Atende Direito (Comercial, Comercial 2, SAC) |
| **t0** | Data da primeira mensagem da conversa |
| **Janela temporal** | Periodo acumulado a partir de t0 (24h, 7d, 15d, 30d) |
| **Lead Ads** | Lead vindo de anuncio no Meta (Facebook/Instagram) |
