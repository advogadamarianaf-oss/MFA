---
name: analisar-lead
description: Analisa a conversa de um ou mais leads/clientes no Atende Direito e gera resumo + classificação de CRM e sequência na memória local do projeto "Análise de Mensagens". Quando houver mais de um nome, dispara agentes em paralelo (um por lead). Use quando o usuário pedir para analisar, processar ou classificar lead(s), conversa(s) ou cliente(s) do Atende Direito (ex: "analisa o lead Fulano", "processa Maria, João e Ana", "classifica esses clientes").
---

# Analisar Lead — Atende Direito

Skill do escritório de **Advocacia Médica & Odontológica** (Mariana Friedrich).
Lê a conversa de um lead no Atende Direito, gera resumo, classifica em um dos 12 CRMs
+ a sequência, e grava tudo na memória local do projeto. Suporta **vários leads de uma
vez, em paralelo**.

Sempre responder em **português**.

## Quando usar
O usuário indica **um ou mais** leads/clientes para analisar (por nome).

## Pré-requisitos
- Extensão **Claude in Chrome** conectada, com o **Atende Direito** logado.
- Estrutura padrão do projeto (`_memoria/`, `_templates/`, `clientes/_MODELO_CLIENTE/`).
- Fonte da verdade da classificação: `_memoria/crm_definicoes.md` (os 12 CRMs).

## Decisão inicial: 1 lead ou vários?
1. Extrair a lista de nomes do pedido do usuário.
2. **Conectar ao navegador uma única vez:** listar os navegadores conectados, pedir
   ao usuário qual usar (o que está com o Atende Direito logado) e selecioná-lo.
3. Se houver **1 nome** → executar o "Fluxo de análise de um lead" diretamente.
4. Se houver **2 ou mais nomes** → seguir a "Orquestração em paralelo".

---

## Fluxo de análise de UM lead
(Este é o trabalho que cada agente executa. Recebe: nome do lead + tabId da aba a usar.)

1. **Buscar o lead.** Na aba indicada, ir em "Chat Ao Vivo" (Painel → Chat Ao Vivo),
   clicar no campo "Procurar" e digitar o nome. **Sempre buscar** — nunca assumir que
   a conversa já está aberta na tela.
   - Se a busca não retornar resultado, tentar variações (só primeiro nome, sobrenome).
   - Se ainda assim não achar, registrar "lead não localizado" e seguir para o próximo;
     não inventar dados.
2. **Abrir a conversa** do resultado correto.
3. **Ler a conversa inteira.** Extrair o texto (get_page_text) e **rolar até o topo**
   para capturar o início (formulário de qualificação, primeira mensagem, origem).
   Capturar do painel do contato: telefone, e-mail, cidade, origem (lead_ads etc.),
   data de criação e a **tag de CRM atual** exibida pelo sistema.
4. **Classificar.**
   - **CRM atual** = o mais avançado comprovado pela conversa (ver `crm_definicoes.md`).
     A tag de CRM do Atende Direito é forte indício; confirmar pela conversa.
   - **Sequência** = onde o lead parou no fluxo (ex: "Follow up — 3º follow-up").
   - Em dúvida entre dois CRMs, registrar ambos nas observações.
5. **Criar/atualizar o arquivo do cliente.** Copiar `clientes/_MODELO_CLIENTE.md` para
   `clientes/<nome-em-minusculas-com-hifens>.md` (se não existir) e preencher **um único
   arquivo** com todas as seções: Status (CRM + sequência), Identificação, Resumo,
   Próximo passo, Observações/alertas, Histórico de etapas e Conversa (registro:
   formulário, linha do tempo, observação técnica).
6. **NÃO** editar `_memoria/indice_clientes.md` diretamente (evita conflito entre
   agentes). Em vez disso, **retornar** ao orquestrador a linha pronta do índice:
   `| <Cliente> | <CRM> | <Sequência> | <AAAA-MM-DD> | clientes/<nome>.md |`
   junto de um resumo curto da classificação e do próximo passo.

---

## Orquestração em paralelo (2+ leads)
1. **Preparar as abas.** Para cada lead, criar uma aba própria no grupo MCP do
   navegador (tabs_create_mcp). Anotar o tabId de cada aba e associá-lo a um lead.
   - Limitar a no máximo ~4–5 agentes simultâneos. Se houver mais leads, processar
     em lotes.
2. **Disparar os agentes.** Lançar **um agente (Task) por lead, todos na mesma rodada**
   (chamadas de Agent em paralelo, em uma única mensagem). No prompt de cada agente,
   passar: o nome do lead, o tabId da aba dele, e o "Fluxo de análise de UM lead" acima.
   Instruir o agente a NÃO mexer no índice e a retornar a linha do índice + resumo.
3. **Consolidar.** Quando todos retornarem, o orquestrador atualiza
   `_memoria/indice_clientes.md` **uma vez, sequencialmente**, adicionando/atualizando
   a linha de cada lead.
4. **Entregar.** Apresentar o arquivo único gerado de cada cliente e uma
   tabela-resumo: Lead | CRM | Sequência | Próximo passo. Sinalizar leads não
   localizados.

---

## Regras
- Sempre **buscar** o lead pelo nome; não depender da tela já aberta.
- Nunca inventar dados fora da conversa.
- Sempre o **CRM mais avançado** comprovado.
- Sinalizar alertas: lead qualificado parado, falha de entrega de mensagens, notas
  internas pendentes, no-show etc.
- Escrita no índice central é **exclusiva do orquestrador** (nunca em paralelo).
- Se só houver um navegador/uma aba disponível e vários leads, processar em sequência.

## Os 12 CRMs (resumo — detalhes em _memoria/crm_definicoes.md)
1. LEAD ENTROU NO COMERCIAL
2. LEAD NÃO DEU A 1ª RESPOSTA APÓS FOLLOW UP'S
3. LEAD RECEBEU MENSAGEM FLUXOGRAMA
4. LEAD CHEGOU ATÉ O ATENDIMENTO HUMANO
5. Aguardando Reunião
6. REUNIÃO AGENDADA CLIENTES
7. Reunião Agendada - DEFESA
8. LEAD NÃO Compareceu à REUNIÃO
9. Aguardando Fechamento
10. FECHAMENTO
11. Contrato Assinado
12. Lead Desqualificado
