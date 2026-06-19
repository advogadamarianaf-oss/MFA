# Rodar o pipeline na nuvem (Google Apps Script) — sem depender da sua máquina

Com isto, a planilha se atualiza **sozinha todo dia às 13h, nos servidores do Google**.
Não precisa de computador ligado, nem da conta de serviço (`gcred.json`) — o Apps Script
escreve direto na planilha. Você só precisa da **chave da API do Atende Direito**.

Leva ~5 minutos, uma vez só.

---

## Passo 1 — Abrir o editor de Apps Script
1. Abra a planilha **RELATÓRIOS COMERCIAIS NOVA**.
2. Menu **Extensões → Apps Script**.

## Passo 2 — Colar o código
3. Apague o conteúdo que aparece (o `function myFunction() {}`).
4. Abra o arquivo **`apps_script_pipeline.gs`** (na pasta do projeto), copie TODO o conteúdo
   e cole no editor.
5. Clique no ícone de **salvar** (disquete). Pode dar um nome ao projeto, ex.: "Pipeline Atende".

## Passo 3 — Informar a chave da API (fica guardada no Google, não no código)
6. No editor, clique na engrenagem **Configurações do projeto** (menu à esquerda).
7. Em **Propriedades do script**, clique em **Adicionar propriedade do script**:
   - Propriedade: `ATENDE_API_KEY`
   - Valor: **(cole a sua chave da API do Atende Direito)**
8. Salve.

## Passo 4 — Autorizar e testar
9. Volte ao editor (ícone `<>`). No topo, selecione a função **`atualizarPlanilha`** e clique **Executar**.
10. O Google vai pedir autorização (é o seu próprio script):
    - "Revisar permissões" → escolha sua conta.
    - Vai aparecer um aviso "Google não verificou este app" → clique em **Avançado** →
      **Acessar Pipeline Atende (não seguro)** → **Permitir**.
    - (Isso é normal: é o seu script acessando a sua planilha e a internet.)
11. Ele vai rodar e preencher as colunas RESUMO. Pode levar 1–4 min na primeira vez.
    Confira o resultado na planilha. (Em **Execuções**, à esquerda, você vê o log.)

## Passo 5 — Agendar para todo dia às 13h
12. No topo, selecione a função **`instalarGatilho`** e clique **Executar**.
    Isso cria o agendamento diário (~13h). Pronto — roda sozinho daqui pra frente.

---

## Como funciona / observações
- **Incremental:** o script guarda um cache (aba oculta `_estado_pipeline`) e, nos dias
  seguintes, só reprocessa os leads cuja conversa mudou — fica rápido.
- Se a primeira execução for grande e bater no limite de ~6 min do Google, ela preenche o que
  der e **mantém o resto como está**; as próximas execuções completam. (A planilha nunca fica
  pior do que estava.)
- Abas processadas: CAMPANHA META, CAMPANHA GOOGLE, ORGÂNICO, MANYCHAT, REUNIÕES & FECHAMENTOS.
  CAPTAÇÃO ATIVA e PIXEL META ficam de fora (sem conversa / sem colunas de resumo).
- O resumo é o **data-driven** (origem, perfil, CRM real, reunião/no-show/falha de entrega).
  Para a **análise profunda** de leads específicos, é só me pedir aqui no Claude.

## Se der erro
- "Falta a propriedade ATENDE_API_KEY" → refaça o Passo 3.
- "API 401/403" → a chave está errada ou expirada.
- Erro de autorização → refaça o Passo 4 (Avançado → Permitir).
- Me mande a mensagem de erro (em **Execuções**) que eu ajusto o código.
