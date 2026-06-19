# CRM — Os 12 Estagios

O funil comercial do escritorio e dividido em **12 estagios (CRMs)**, que representam
as "colunas" do quadro no Atende Direito. Cada lead e classificado em exatamente um
CRM a qualquer momento.

## Conceitos

- **CRM** — o estagio macro do lead no funil. E o status principal.
- **Sequencia** — a posicao do lead *dentro* do fluxo daquele CRM.
  Exemplo: "Follow-up 3 de 5 sem resposta", "Fluxograma — etapa de qualificacao".

## Tabela dos 12 CRMs

| # | CRM | O que significa | Sinais na conversa |
|---|-----|-----------------|--------------------|
| 1 | **LEAD ENTROU NO COMERCIAL** | Lead novo, recem-chegado ao comercial. | Primeiro contato, ainda sem qualificacao. |
| 2 | **LEAD NAO DEU A 1a RESPOSTA APOS FOLLOW UP'S** | Foram enviados follow-ups e o lead nao respondeu. | Mensagens do escritorio sem retorno; varios follow-ups sem resposta. |
| 3 | **LEAD RECEBEU MENSAGEM FLUXOGRAMA** | Lead recebeu o fluxo automatizado de mensagens. | Sequencia automatica enviada; aguardando interacao. |
| 4 | **LEAD CHEGOU ATE O ATENDIMENTO HUMANO** | Lead avancou do automatico para atendente humano. | Conversa deixa de ser automatica; atendente real respondendo. |
| 5 | **Aguardando Reuniao** | Reuniao combinada mas ainda nao agendada formalmente. | Interesse em reuniao manifestado; sem data fechada. |
| 6 | **REUNIAO AGENDADA CLIENTES** | Reuniao marcada com data/hora (perfil cliente). | Data e horario confirmados. |
| 7 | **Reuniao Agendada - DEFESA** | Reuniao marcada, caso de defesa profissional. | Data confirmada; demanda de defesa medica/odontologica. |
| 8 | **LEAD NAO Compareceu a REUNIAO** | Reuniao marcada mas o lead faltou. | No-show; reagendamento pendente. |
| 9 | **Aguardando Fechamento** | Pos-reuniao, aguardando decisao/contrato. | Proposta/honorarios apresentados; lead avaliando. |
| 10 | **FECHAMENTO** | Em processo ativo de fechamento. | Negociacao final; lead sinalizou que vai contratar. |
| 11 | **Contrato Assinado** | Cliente fechado, contrato assinado. | Confirmacao de assinatura/pagamento. |
| 12 | **Lead Desqualificado** | Lead fora do perfil ou sem interesse. | Sem fit, sem condicoes, ou desistencia explicita. |

## Funil Visual

```
  1. ENTROU NO COMERCIAL
         |
  2. NAO DEU 1a RESPOSTA --------+
         |                       |
  3. RECEBEU FLUXOGRAMA          |
         |                       |
  4. ATENDIMENTO HUMANO          |
         |                       |
  5. AGUARDANDO REUNIAO          |
        / \                      |
  6. REUNIAO      7. REUNIAO     |
     CLIENTES        DEFESA      |
        \ /                      |
  8. NAO COMPARECEU              |
         |                       |
  9. AGUARDANDO FECHAMENTO       |
         |                       |
 10. FECHAMENTO                  |
         |                       |
 11. CONTRATO ASSINADO           |
                                 |
 12. LEAD DESQUALIFICADO  <------+
```

## Regras de Classificacao

1. **Sempre o CRM mais avancado** que a conversa comprova.
2. Se a conversa nao comprova avanco, manter o CRM anterior registrado.
3. Registrar a **sequencia** com o maximo de detalhe (ex: "Follow-up 3 de 5").
4. Em caso de duvida entre dois CRMs, anotar ambos nas observacoes e marcar o mais provavel.
5. **Nunca inventar** dados que nao estejam na conversa.

## Como o Pipeline Identifica o CRM

No pipeline automatico (`pipeline_diario.py`), o CRM e extraido do ultimo evento
`"Moved to board: <nome_do_board>"` nos system messages da conversa. Os boards do
Atende Direito correspondem exatamente aos 12 CRMs acima.

Na analise via IA (skills do Claude Code), o agente le a conversa completa e
classifica usando a definicao acima + o sinal da tag de CRM do sistema.
