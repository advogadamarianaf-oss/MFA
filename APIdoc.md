Ferramentas Disponíveis


Agentes e Tarefas de IA



getFlowAiAgents — Lista todos os Agentes de IA configurados no workspace.
postFlowUpdateAiAgentProvider — Atualiza o provedor de IA de um Agente de IA específico.
getFlowAiTasks — Lista todas as Tarefas de IA configuradas no sistema.
postFlowUpdateAiTaskProvider — Atualiza o provedor de IA para uma Tarefa de IA específica.
getFlowAgentActivityLogData — Obtém logs de atividade (entradas, saídas, custo, tokens) de um agente de IA.


Conversas



getFlowConversationsData — Lista conversas do workspace com paginação.


Eventos Customizados



getFlowCustomEvents — Lista eventos customizados.
getFlowCustomEventsSummary — Resumo de um evento customizado por período.
getFlowCustomEventsData — Dados detalhados de eventos customizados com paginação.


Bot Fields



getFlowBotFields — Lista campos de bot configurados.
postFlowCreateBotField — Cria um novo campo de bot.
putFlowSetBotField / putFlowSetBotFieldByName — Atualiza valor de um campo de bot (por ID ou nome).
putFlowSetBotFields / putFlowSetBotFieldsByName — Atualiza múltiplos campos de bot.
deleteFlowDeleteBotField / deleteFlowDeleteBotFieldByName — Remove campo de bot.


Segmentos



getFlowSegments — Lista segmentos de usuários.


Subscribers (Contatos/Usuários)



getSubscribers — Lista e filtra subscribers (contatos). Filtra por nome, telefone, email, canal, tags, eventos, campos personalizados.
getSubscriberGetInfo — Obtém dados de um subscriber pelo user_ns.
getSubscriberGetInfoByUserId — Obtém dados de um subscriber pelo user_id.
postSubscriberCreate — Cria um novo subscriber.
putSubscriberUpdate — Atualiza dados de um subscriber.
deleteSubscriberDelete — Remove um subscriber.
postSubscriberAddTag / postSubscriberAddTags — Adiciona tag(s) por ID.
postSubscriberAddTagByName / postSubscriberAddTagsByName — Adiciona tag(s) por nome.
deleteSubscriberRemoveTag / deleteSubscriberRemoveTags — Remove tag(s) por ID.
deleteSubscriberRemoveTagByName / deleteSubscriberRemoveTagsByName — Remove tag(s) por nome.
postSubscriberAddLabelsByName — Adiciona labels por nome.
deleteSubscriberRemoveLabelsByName — Remove labels por nome.
putSubscriberSetUserField / putSubscriberSetUserFields — Atualiza campo(s) personalizado(s) por ID.
putSubscriberSetUserFieldByName / putSubscriberSetUserFieldsByName — Atualiza campo(s) por nome.
deleteSubscriberClearUserField / deleteSubscriberClearUserFields — Limpa campo(s) por ID.
deleteSubscriberClearUserFieldByName / deleteSubscriberClearUserFieldsByName — Limpa campo(s) por nome.


Mensagens e Fluxos



postSubscriberSendMainFlow — Envia fluxo principal para um subscriber.
postSubscriberSendSubFlow — Envia sub-fluxo por ID.
postSubscriberSendSubFlowByFlowName — Envia sub-fluxo por nome.
postSubscriberSendSubFlowByUserId — Envia sub-fluxo usando user_id.
postSubscriberBroadcast — Broadcast para um subscriber.
postSubscriberBroadcastByUserId — Broadcast por user_id.
postSubscriberBroadcastByTag — Broadcast para todos com determinada tag.
postSubscriberBroadcastBySegment — Broadcast para um segmento.
postSubscriberSendContent — Envia conteúdo avulso.
postSubscriberSendText — Envia mensagem de texto.
postSubscriberSendSms — Envia SMS.
postSubscriberSendEmail — Envia e-mail.
postSubscriberSendNode — Envia um nó específico do fluxo.
postSubscriberSendWhatsappTemplate — Envia template de WhatsApp para subscriber.
postSubscriberSendWhatsappTemplateByUserId — Envia template de WhatsApp por user_id.
getSubscriberChatMessages — Obtém histórico de mensagens do chat de um subscriber.
postSubscriberChatMessagesByMids — Obtém mensagens específicas por IDs.


Gerenciamento de Atendimento



postSubscriberPauseBot — Pausa o bot para um subscriber.
postSubscriberResumeBot — Retoma o bot para um subscriber.
postSubscriberMoveChatTo — Move o chat para outra fila/departamento.
postSubscriberAssignAgent — Atribui um agente ao chat.
postSubscriberAssignAgentGroup — Atribui um grupo de agentes ao chat.
postSubscriberUnassignAgent — Remove atribuição de agente.
postSubscriberSubscribeToBot — Inscreve subscriber no bot.
deleteSubscriberUnsubscribeFromBot — Desinscreve subscriber do bot.
postSubscriberOptInSms / deleteSubscriberOptOutSms — Opt-in/out de SMS.
postSubscriberOptInEmail / deleteSubscriberOptOutEmail — Opt-in/out de e-mail.
postSubscriberLogCustomEvent — Registra um evento customizado para o subscriber.


Sub-fluxos e Agentes



getFlowSubflows — Lista sub-fluxos configurados.
deleteFlowDeleteSubFlow — Deleta um sub-fluxo.
getFlowBotUsersCount — Retorna contagem total de usuários do bot.
getFlowAgents — Lista agentes/atendentes humanos.
getFlowTemplateInstalls — Lista templates instalados.
postFlowSetDefaultStartFlow — Define fluxo de início padrão.
postFlowSetWebChatWidgetDefaultStartFlow — Define fluxo padrão para widget Web Chat.


Configurações e Webhooks



postFlowSettingsSetAudioTranscription — Configura transcrição de áudio.
postFlowSettingsSetDefaultAiProvider — Define o provedor de IA padrão.
getFlowInboundWebhooks — Lista webhooks de entrada.
getFlowChatButtonWidgets — Lista widgets de botão de chat.


Tags e Campos



getFlowTags — Lista todas as tags do sistema.
postFlowCreateTag — Cria uma nova tag.
deleteFlowDeleteTag / deleteFlowDeleteTagByName — Remove tag por ID ou nome.
getFlowUserFields — Lista campos personalizados de usuário.
postFlowCreateUserField — Cria novo campo personalizado.
postFlowUpdateUserField — Atualiza definição de campo personalizado.
deleteFlowDeleteUserField / deleteFlowDeleteUserFieldByName — Remove campo por ID ou nome.


Templates de WhatsApp



postWhatsappTemplateList — Lista templates de WhatsApp aprovados/pendentes.
postWhatsappTemplateCreate — Cria e envia template para aprovação.
deleteWhatsappTemplateDelete — Deleta um template.
postWhatsappTemplateSync — Sincroniza templates com a API do WhatsApp.


Estatísticas



getFlowSummary — Estatísticas e resumo dos fluxos automáticos por período.
getFlowAgentSummary — Performance geral de agentes e atendentes.
getTeamBotUsers — Busca avançada de subscribers com múltiplos filtros.