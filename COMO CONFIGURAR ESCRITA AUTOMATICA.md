# Configurar a escrita automática na planilha (uma vez só)

Para o script preencher a planilha sozinho, ele precisa de uma **conta de serviço** do
Google (uma "credencial de robô") com permissão de editar a sua planilha. Você cria isso
uma única vez. Eu não posso criar credenciais por você — siga os passos abaixo.

Leva ~10 minutos. Qualquer dúvida, me chame em cada passo.

---

## Parte 1 — Criar a conta de serviço e baixar a chave

1. Abra **https://console.cloud.google.com/** e faça login com a conta do Google que tem a planilha.
2. No topo, crie (ou selecione) um **projeto** qualquer (ex.: "Atende Direito"). Clique em
   "Selecionar projeto" / "Novo projeto" se precisar.
3. Ative a API do Sheets: abra **https://console.cloud.google.com/apis/library/sheets.googleapis.com**
   e clique em **Ativar** (Enable).
4. Crie a conta de serviço: abra
   **https://console.cloud.google.com/iam-admin/serviceaccounts** → **Criar conta de serviço**.
   - Nome: `planilha-bot` (qualquer um). Clique em **Criar e continuar** e depois **Concluir**
     (não precisa dar papéis/roles).
5. Abra a conta de serviço recém-criada → aba **Chaves (Keys)** → **Adicionar chave** →
   **Criar nova chave** → tipo **JSON** → **Criar**. Vai baixar um arquivo `.json`.
6. **Renomeie esse arquivo para `gcred.json`** e mova para a pasta do projeto:
   `C:\Users\Thiag\OneDrive\Área de Trabalho\Analise de Mensagens\gcred.json`
   (tem que ficar exatamente com esse nome, nessa pasta).

> Guarde esse arquivo com cuidado — é uma credencial. Não compartilhe.

---

## Parte 2 — Dar acesso da planilha à conta de serviço

7. Copie o **e-mail da conta de serviço** (algo como
   `planilha-bot@seu-projeto.iam.gserviceaccount.com`). Ele aparece na lista de contas de
   serviço e dentro do `gcred.json` (campo "client_email").
8. Abra a planilha **RELATÓRIOS COMERCIAIS NOVA** no navegador → botão **Compartilhar** →
   cole esse e-mail → permissão **Editor** → **Enviar**.

---

## Pronto! Como usar daqui pra frente

Sempre que quiser atualizar os resumos:

1. **`RODAR - Atualizar dados (API + mensagens).bat`** — baixa os leads e conversas.
2. Me avise "feito" — eu analiso as conversas novas e monto os blocos de todas as abas.
3. **`RODAR - Escrever planilha (automatico).bat`** — preenche TODAS as abas sozinho, sem Ctrl+V.

A primeira vez que rodar o passo 3, ele instala umas bibliotecas do Python automaticamente
(precisa de internet, leva ~1 min).

---

## Se der erro

- "nao encontrei gcred.json" → o arquivo não está na pasta certa ou com outro nome.
- "PERMISSION_DENIED" / 403 → a planilha não foi compartilhada com o e-mail da conta de serviço
  (passo 8), ou foi compartilhada como Leitor em vez de Editor.
- "Faltam bibliotecas" → rode no Prompt de Comando: `pip install google-auth google-api-python-client`
- Me mande a mensagem de erro que eu ajusto.
