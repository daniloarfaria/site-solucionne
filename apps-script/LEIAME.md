# Formulário do site → Google Planilhas

Caminho dos dados:

```
Site (/api/orcamento)  →  Netlify Function  →  Google Apps Script  →  Planilha + e-mail de aviso
                          (guarda a URL e         (só aceita quem
                           a senha em segredo)     manda a senha)
```

A URL do Apps Script e a senha nunca aparecem no código do site.

O script grava em duas abas, criadas sozinhas no primeiro envio de cada tipo:

- **Orçamentos**: formulário "Solicite um orçamento" (manda e-mail de aviso).
- **Leads WhatsApp**: popup que aparece ao clicar em qualquer botão de WhatsApp (nome, telefone, interesse e UTMs).
  Para receber e-mail também desses leads, mude `AVISAR_LEADS_WHATSAPP` para `true` no topo do script.

## 1. Criar a senha

Gere uma senha longa e aleatória (ex.: no terminal, `openssl rand -hex 24`). Ela vai em dois lugares: no Apps Script e na Netlify.

## 2. Planilha e Apps Script

1. Crie uma planilha nova no Google Drive da ótica (ex.: "Orçamentos do site").
2. Na planilha: **Extensões → Apps Script**.
3. Apague o conteúdo de `Código.gs`, cole todo o conteúdo de `Codigo.gs` desta pasta e salve.
4. Se quiser, ajuste no topo do script o e-mail que recebe os avisos (`EMAIL_AVISO`).
5. Engrenagem **Configurações do projeto** → **Propriedades do script** → **Adicionar propriedade**:
   - Propriedade: `SEGREDO_FORMULARIO`
   - Valor: a senha do passo 1
   - **Salvar propriedades do script**
6. Volte ao editor, escolha a função **testar** e clique em **Executar**.
   - O Google pede autorização: escolha a conta → **Avançado → Acessar (não seguro)** → **Permitir**.
   - Confira: apareceu a aba **Orçamentos** com uma linha de teste e chegou o e-mail de aviso.
7. **Implantar → Nova implantação** → engrenagem → **App da Web**:
   - Executar como: **Eu**
   - Quem pode acessar: **Qualquer pessoa** (a senha é que protege)
   - **Implantar** e copie a **URL do app da Web** (termina em `/exec`).

## 3. Netlify

**Site configuration → Environment variables → Add a variable**, crie duas:

| Nome | Valor |
|---|---|
| `APPS_SCRIPT_URL` | a URL `/exec` do passo 2.7 |
| `FORM_SECRET` | a mesma senha do passo 1 |

Depois: **Deploys → Trigger deploy → Deploy site** (variáveis novas só valem após um novo deploy).

## 4. Testar

Envie um orçamento pelo site no ar. A linha deve aparecer na planilha e o e-mail deve chegar.
Se der erro: **Netlify → Logs → Functions → orcamento** mostra o motivo.

## Alterei o script depois. Preciso trocar a URL?

Não, se fizer assim: **Implantar → Gerenciar implantações → lápis (editar) → Versão: Nova versão → Implantar**.
"Nova implantação" gera outra URL; aí atualize `APPS_SCRIPT_URL` na Netlify e faça novo deploy.

## Trocar a senha

Mude nos dois lugares (`SEGREDO_FORMULARIO` no Apps Script e `FORM_SECRET` na Netlify) e faça novo deploy na Netlify.
