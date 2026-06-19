---
name: processar-planilha
description: Processa os leads da planilha RELATORIOS COMERCIAIS NOVA (aba CAMPANHA META) em lotes de 5, na ordem dos nomes. Para cada lead: busca a conversa no Atende Direito, gera o arquivo do cliente e o resumo temporal, e preenche na planilha as colunas RESUMO APOS 24H/7/15/30 DIAS. Use quando o usuario pedir para processar a planilha, rodar os leads da planilha, preencher os resumos da planilha, ou continuar o proximo lote.
---

# Processar Planilha de Leads — pipeline completo

Escritorio de Advocacia Medica & Odontologica (Mariana Friedrich). Responda em portugues.
Orquestra o fluxo de ponta a ponta para os leads da planilha de relatorios comerciais,
em lotes de 5, na ordem dos nomes.

## Pre-requisitos
- Planilha Google "RELATORIOS COMERCIAIS NOVA" (id 1BodcfEOso5pooeOSnA2Gq-OJVQtVcjleIEAfjvwM5IM),
  aba CAMPANHA META. Conteudo disponivel via fonte sincronizada (sync) ou leitura.
- Extensao Claude in Chrome conectada; navegador com o Atende Direito logado E o Google logado
  com permissao de edicao na planilha (no mesmo navegador). Padrao usado: navegador "DEV".
- Estrutura do projeto: clientes/_MODELO_CLIENTE.md, pasta Resumos/, _memoria/crm_definicoes.md,
  _memoria/indice_clientes.md.

## Mapa da planilha (aba CAMPANHA META)
- Linha 1 = cabecalho. Dados comecam na linha 2.
- Coluna B = NOME (ordem de processamento). Coluna C = TELEFONE (use para confirmar o lead certo).
- Colunas a preencher: **M = RESUMO APOS 24H, N = RESUMO APOS 7 DIAS, O = RESUMO APOS 15 DIAS,
  P = RESUMO APOS 30 DIAS**. Nunca escrever em outras colunas.

## Definicao das janelas (resumo temporal)
- t0 = data da primeira mensagem/evento da conversa do lead.
- Janelas ACUMULADAS a partir de t0: primeiras 24h; primeiros 7; 15; 30 dias.
- Se a janela ainda nao decorreu (conversa recente) ou nao houve novas interacoes, registrar
  isso ("Janela ainda nao decorrida..."/"Sem novos eventos...").

## Fluxo por LOTE (5 leads por vez, na ordem da coluna NOME)
1. **Selecionar o lote.** Pegar os proximos 5 nomes ainda nao processados, na ordem da planilha.
   (Pular linhas que ja tenham M:P preenchidas, salvo se o usuario pedir reprocessar.)

2. **Ler as conversas (1 agente leitor, sequencial).** Disparar UM agente que, numa unica aba do
   navegador DEV (Atende Direito > Chat Ao Vivo), busca cada um dos 5 nomes pelo campo "Procurar",
   abre a conversa (conferindo pelo telefone), extrai o texto (get_page_text), rola ate o topo e
   extrai de novo. Para cada lead, captura: contato (tel/e-mail/cidade/origem/data de inicio), a TAG
   de CRM do sistema, respostas do formulario e a linha do tempo (datas/horas, quem, mensagem-chave,
   status como "Falha na entrega", respostas do lead). Retorna os dados estruturados dos 5.
   - Motivo de ser sequencial e num so agente: ha um unico navegador/janela; buscas simultaneas
     disputariam o foco. Se houver varios navegadores conectados, pode-se paralelizar as leituras.

3. **Escrever arquivos + resumos (agentes em paralelo).** Disparar 1 agente por lead (em paralelo;
   trabalho so de arquivos, sem navegador), passando os dados ja lidos. Cada agente:
   - cria/atualiza clientes/<nome-em-minusculas-com-hifens>.md a partir de _MODELO_CLIENTE.md
     (classificando CRM + sequencia conforme _memoria/crm_definicoes.md; sempre o CRM mais avancado
     comprovado);
   - cria Resumos/Resumo - <Nome do Cliente>.md com as 4 janelas;
   - **nao** edita o indice; retorna a linha do indice + os 4 textos CURTOS prontos para as celulas
     (RESUMO_24H, RESUMO_7D, RESUMO_15D, RESUMO_30D), cada um objetivo (~180 caracteres, sem quebra
     de linha).

4. **Consolidar o indice.** O orquestrador atualiza _memoria/indice_clientes.md uma vez, com as
   linhas dos 5 (sequencial, sem conflito).

5. **Preencher a planilha (orquestrador, via navegador).** Abrir a planilha no navegador
   (https://docs.google.com/spreadsheets/d/1BodcfEOso5pooeOSnA2Gq-OJVQtVcjleIEAfjvwM5IM/edit),
   garantir que a aba ativa e CAMPANHA META. Para cada lead, descobrir a linha pela posicao do nome
   (confirmar por NOME/telefone). Escrever as 4 celulas com a Caixa de Nome:
   - clicar na Caixa de Nome (canto superior esquerdo), digitar "M<linha>", Enter;
   - digitar o texto de 24h; Tab; texto de 7 dias; Tab; 15 dias; Tab; 30 dias; Enter.
   - O Tab comita e anda para a direita; o Enter ao fim volta para a coluna M da proxima linha.
   - Conferir por screenshot a cada 1-2 linhas. Nunca sobrescrever colunas que ja tenham conteudo
     (so M:P, que costumam estar vazias). Aguardar "Alteracoes salvas no Drive".
   - Modificar planilha compartilhada: confirmar com o usuario antes da PRIMEIRA gravacao do dia.

6. **Entregar o lote.** Apresentar uma tabela-resumo (Lead | CRM | Sequencia | Proximo passo),
   sinalizar leads nao localizados, e oferecer continuar com o proximo lote.

## Regras
- Processar SEMPRE na ordem dos nomes da planilha; lotes de 5.
- Nunca inventar dados fora da conversa; nunca escrever fora de M:P.
- Escrita no indice e nas celulas e exclusiva do orquestrador.
- Leitura no Atende Direito sequencial (um navegador); paralelizar so a escrita de arquivos.
- Sinalizar alertas: lead qualificado parado, falha de entrega, no-show, nota interna pendente.

## Lead em mais de um canal (Comercial / Comercial 2 / SAC)
Bots/fluxos: Comercial - API OFICIAL (f175863), Comercial 2 - API OFICIAL (f270363), SAC (f229905).
O mesmo lead pode ter cadastros separados em mais de um fluxo. Ao buscar pelo nome/telefone,
CONFERIR se aparece mais de um resultado (um por fluxo) e abrir TODOS antes de classificar.
- Um cliente = um arquivo: consolidar tudo em clientes/<nome>.md (nunca dois arquivos p/ a mesma pessoa).
- Linha do tempo unica, ordenada por data/hora, marcando o canal de cada trecho ([Comercial]/[Comercial 2]/[SAC]).
- Classificar pelo CRM mais avancado comprovado em QUALQUER canal.
- Registrar todos os user_ns e os canais no cabecalho do arquivo.
- Conflito entre canais (avancado num, parado no outro) -> registrar ambos nas observacoes.
- Na planilha, e UMA linha por pessoa: se houver linhas duplicadas (mesmo telefone), preencher a
  classificacao consolidada e sinalizar a duplicidade ao usuario (nao apagar linha sem confirmar).

## Os 12 CRMs (detalhes em _memoria/crm_definicoes.md)
LEAD ENTROU NO COMERCIAL; LEAD NAO DEU A 1a RESPOSTA APOS FOLLOW UPS; LEAD RECEBEU MENSAGEM
FLUXOGRAMA; LEAD CHEGOU ATE O ATENDIMENTO HUMANO; Aguardando Reuniao; REUNIAO AGENDADA CLIENTES;
Reuniao Agendada - DEFESA; LEAD NAO Compareceu a REUNIAO; Aguardando Fechamento; FECHAMENTO;
Contrato Assinado; Lead Desqualificado.
