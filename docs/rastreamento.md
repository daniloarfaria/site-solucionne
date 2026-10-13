# Rastreamento: Google Ads, Google Analytics 4 e Meta

O site **não usa Google Tag Manager**. Tudo é feito direto no código.

> **Migração (out/2026):** o site antigo usava o GTM `GTM-TJ88RS5C` servido pelo Stape (`stape.solucionne.com.br`). Ele deixou de ser carregado. Foram trazidos para o código só o GA4 `G-97STC6HHXB`, o Google Ads `AW-715247679` e os rótulos certos de WhatsApp (`cvCVCML-wLoZEL-gh9UC`) e formulário (`lvtTCNn_obcZEL-gh9UC`). Ficaram de fora: a conversão `UqscCODJo7cZEL-gh9UC`, que disparava em **toda página** (no Google Ads, marque-a como **secundária** ou remova), e uma tag que reescrevia a mensagem do WhatsApp para "eu vi seu anúncio no …".


| Arquivo | O que faz |
|---|---|
| `public/assets/js/rastreamento.js` | IDs, consentimento (LGPD), `gtag.js` (Google Ads + GA4) e Pixel da Meta |
| `public/assets/js/main.js` | Dispara os eventos (`track` / `trackConversao`) |
| `netlify/lib/meta-capi.mjs` | API de Conversões da Meta (servidor), chamada pelas funções `/api/orcamento` (conversões) e `/api/evento` (PageView) |
| `netlify/lib/origem.mjs` | Domínios autorizados a chamar as funções |

## Onde fica cada configuração

| Item | Onde | É secreto? |
|---|---|---|
| ID do Google Ads (`AW-...`) | `rastreamento.js` → `googleAds` | Não (aparece no navegador) |
| Rótulos de conversão do Google Ads | `rastreamento.js` → `conversoesGoogleAds` | Não |
| ID do GA4 (`G-...`) | `rastreamento.js` → `ga4` | Não |
| ID do Pixel da Meta | `rastreamento.js` → `metaPixel` **e** variável `META_PIXEL_ID` na Netlify | Não |
| Token da API de Conversões | Variável **`META_CAPI_TOKEN`** na Netlify | **Sim** — nunca no código |
| Código de teste da Meta | Variável `META_TEST_EVENT_CODE` (opcional, apagar depois de testar) | Não |
| Versão da Graph API | Variável `META_API_VERSION` (opcional, padrão `v26.0`) | Não |

ID em branco no `rastreamento.js` = ferramenta desligada. Sem `META_PIXEL_ID`/`META_CAPI_TOKEN`, a função ignora a Meta.

## Consentimento (LGPD)

- Antes de qualquer tag, o `rastreamento.js` define o modo de consentimento do Google como **negado** (ou concedido, se a pessoa já aceitou: `localStorage.sol_consentimento`).
- Google Ads e GA4 carregam sempre, mas sem cookies até o aceite (o Google recebe sinais anônimos e modela parte das conversões).
- **Pixel da Meta só carrega depois do aceite.** A API de Conversões só envia leads de quem aceitou (`consentimento: "aceito"`).
- O aviso de cookies é criado pelo `main.js`; "Preferências de cookies" no rodapé reabre.

## Conversões

| Evento do site | Google Ads | Meta (pixel + API de Conversões) |
|---|---|---|
| `lead_whatsapp` — preencheu o popup e foi ao WhatsApp | `cvCVCML-wLoZEL-gh9UC` | `Contact` |
| `form_orcamento_enviado` — orçamento salvo na planilha | `lvtTCNn_obcZEL-gh9UC` | `Lead` |

- Cada conversão tem um **ID único** (`event_id`). No Google Ads ele vai como `transaction_id` (evita duplicar); na Meta, o mesmo ID vai pelo pixel (`eventID`) e pela API de Conversões (`event_id`), e a Meta conta uma vez só.
- **Conversões otimizadas (Google Ads):** telefone (`+55...`) e e-mail vão em `user_data`; o Google criptografa antes de enviar.
- **API de Conversões (Meta):** telefone, e-mail, nome e sobrenome criptografados (SHA-256), país, IP, navegador, cookies `_fbp`/`_fbc` (ou `fbclid` do anúncio), página e origem (`utm_source`).

## O que vai para a Meta

| Evento | Navegador (pixel) | Servidor (API de Conversões) |
|---|---|---|
| `PageView` (toda página, após aceite) | URL, `eventID` | mesmo `event_id`, URL, IP, navegador, `_fbp`, `_fbc` |
| `Contact` (popup) / `Lead` (orçamento) | conteúdo, `eventID` + correspondência avançada: telefone, e-mail, nome, sobrenome, país (o pixel criptografa) | mesmo `event_id`, telefone, e-mail, nome, sobrenome e país em SHA-256, IP, navegador, `_fbp`, `_fbc`, página, conteúdo, `utm_source` |

Nunca vai: mensagem do orçamento, endereço, dados de quem recusou os cookies.

### Diagnóstico (só com `META_TEST_EVENT_CODE` cadastrada)
`POST /api/orcamento` com `{"diagnostico": true, "tipo": "whatsapp", "nome": "Teste", "telefone": "31900000000", "pagina": "https://DOMINIO/", "consentimento": "aceito", "event_id": "diag-1"}`
envia só para a Meta (não grava na planilha) e devolve a resposta dela (`events_received`, `messages`, `fbtrace_id`). Sem a variável de teste, esse modo não existe.

## Eventos enviados ao GA4

Todos levam `tipo_pagina` (`inicio`, `produto`, `link_bio`, `obrigado`, `erro_404`, `privacidade`). O formulário de orçamento e o popup levam `interesse` (nome do produto da página ou do botão). As UTMs da URL o GA4 lê sozinho.

| Evento | Quando | Parâmetros |
|---|---|---|
| `lead_whatsapp` ⭐ | Conversão (acima) | `interesse`, `local_clique`, `utm_*`, `event_id` |
| `form_orcamento_enviado` ⭐ | Conversão (acima) | `utm_*`, `event_id` |
| `whatsapp_clique` | Clique em botão de WhatsApp (antes do popup) | `local_clique`, `interesse` |
| `whatsapp_popup_aberto` | Popup apareceu | `local_clique`, `interesse` |
| `whatsapp_popup_erro` | Nome ou telefone inválido | `campo` |
| `whatsapp_popup_fechado` | Fechou sem preencher | `local_clique`, `interesse` |
| `form_orcamento_inicio` | Primeiro foco no formulário | — |
| `form_orcamento_erro` | Falha ao salvar ou telefone inválido | `motivo` |
| `telefone_clique`, `email_clique`, `rota_clique` | Cliques de contato | `local_clique` |
| `rede_social_clique` | Instagram, YouTube, Facebook, TikTok | `local_clique`, `rede_social` |
| `link_bio_clique` | Botão da página `/links` | `botao` |
| `duvida_aberta` | Abriu uma pergunta frequente | `pergunta` |
| `consentimento_cookies` | Escolha no aviso de cookies | `escolha` |

`local_clique`: `menu`, `topo`, `produto`, `servico`, `chamada`, `duvidas`, `contato`, `rodape`, `botao_flutuante`, `link_bio`, `pagina_simples`.

### No painel do GA4 (uma vez)
1. **Administrador → Eventos-chave**: marcar `lead_whatsapp` e `form_orcamento_enviado`.
2. **Administrador → Definições personalizadas → Criar dimensão** (escopo Evento): `tipo_pagina`, `local_clique`, `interesse`, `rede_social`, `botao`.
3. **Administrador → Vinculações do Google Ads**: vincular a conta `AW-715247679`.

## Testar
- **Google:** extensão/site Tag Assistant (tagassistant.google.com) → conectar ao site.
- **Meta:** com `META_TEST_EVENT_CODE` preenchido, Gerenciador de Eventos → **Testar eventos** mostra os eventos do navegador e do servidor; confira "Desduplicado". Depois **apague** a variável e faça novo deploy.
- Erros da API de Conversões: **Netlify → Logs → Functions → orcamento**.

## Adicionar outra ferramenta (TikTok, Hotjar...)
1. Carregar o script dela no `rastreamento.js`, **só depois do consentimento** (como o `carregarMeta`).
2. Adicionar o domínio na `Content-Security-Policy` do `netlify.toml`, senão o navegador bloqueia.
3. Documentar aqui.
