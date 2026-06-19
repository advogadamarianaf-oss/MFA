# MFA — Documentacao do Projeto

Documentacao tecnica completa do sistema **Analise de Mensagens** do escritorio
de Advocacia Medica & Odontologica (Mariana Friedrich).

## Indice

| Pagina | Descricao |
|--------|-----------|
| [Visao Geral](visao-geral.md) | O que e o projeto, problema resolvido e resultados |
| [Arquitetura](arquitetura.md) | Diagrama de componentes, fluxo de dados e integraccoes |
| [Estrutura de Arquivos](estrutura-arquivos.md) | Mapa completo de pastas e arquivos |
| [CRM — Os 12 Estagios](crm-definicoes.md) | Definicao de cada CRM e regras de classificacao |
| [Fluxo de Trabalho](fluxo-trabalho.md) | Como analisar leads passo a passo |
| [Skills e Comandos](skills.md) | Referencia das 4 skills do Claude Code |
| [Pipeline Diario](pipeline-diario.md) | Automacao: coleta API + resumos + escrita na planilha |
| [Integracoes](integracoes.md) | APIs do Atende Direito, Google Sheets e Claude in Chrome |
| [Guia Rapido](guia-rapido.md) | Setup inicial e primeiros passos |

## Stack

- **CRM/Chat**: Atende Direito (API REST + WhatsApp Business)
- **Planilha**: Google Sheets (API v4, conta de servico)
- **IA / Automacao**: Claude Code (Claude in Chrome, skills, agentes paralelos)
- **Scripts**: Python 3.12, PowerShell, Batch (Windows)
- **Dados**: Markdown (clientes + memoria), JSON (API), TSV (blocos de escrita)
