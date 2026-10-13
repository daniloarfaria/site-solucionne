# Site Solucionne

Site da **Solucionne – Termo Acústico do Brasil** (Belo Horizonte – MG): https://solucionne.com.br

Site estático hospedado na Netlify. Não tem etapa de build na Netlify: a pasta `public/` é publicada como está.

## Estrutura

```
public/                         O que vai para o ar (raiz do domínio) — GERADO, não edite à mão
├── index.html, <produto>.html (10), links.html, obrigado.html, 404.html, politica-de-privacidade.html
├── robots.txt, sitemap.xml
└── assets/ (css/styles.css, fonts/, js/rastreamento.js, js/main.js, img/, favicon/)
ferramentas/gerar_paginas.py    Textos, produtos e layout de todas as páginas → gera public/*.html
ferramentas/otimizar_imagens.py Originais → .webp em duas larguras, favicon e og-image
ferramentas/icones/             Ícones SVG (viram um sprite dentro de cada página)
netlify/functions/orcamento.mjs Formulários (/api/orcamento): planilha + API de Conversões da Meta
netlify/functions/evento.mjs    PageView pela API de Conversões (/api/evento)
netlify/lib/                    meta-capi.mjs (envio à Meta), origem.mjs (domínios autorizados)
apps-script/                    Script do Google Planilhas + LEIAME.md (instalação)
originais/imagens/              Fotos e logos originais em alta (não são publicados)
docs/rastreamento.md            Google Ads, GA4, Meta (pixel + API de Conversões) e eventos
netlify.toml                    Configuração da Netlify (CSP, cache, redirecionamentos)
.env.example                    Modelo das variáveis de ambiente
```

## Como editar
```bash
# 1. Texto, produto, contato, FAQ: edite ferramentas/gerar_paginas.py
# 2. Imagem nova: coloque em originais/imagens/fotos/ (nome novo!), registre em FOTOS e rode:
python3 ferramentas/otimizar_imagens.py
# 3. Gere as páginas e confira:
python3 ferramentas/gerar_paginas.py
python3 -m http.server -d public 8000
```
Estilo: `public/assets/css/styles.css` (cores e fontes nos tokens de `:root`). Comportamento: `public/assets/js/main.js`.

## Formulários
```
Site → /api/orcamento (Netlify Function) → Google Apps Script → Planilha
```
- **Solicite um orçamento** (início e páginas de produto) → aba `Orçamentos` (com e-mail de aviso).
- **Popup antes do WhatsApp** → aba `Leads WhatsApp`.

A URL do Apps Script, a senha e o token da Meta ficam nas variáveis da Netlify (`APPS_SCRIPT_URL`, `FORM_SECRET`, `META_CAPI_TOKEN`), nunca no código.

## Rastreamento
Sem Google Tag Manager: Google Ads, GA4 e Pixel da Meta em `public/assets/js/rastreamento.js` (com consentimento LGPD),
API de Conversões da Meta nas funções da Netlify. IDs, variáveis e eventos: [docs/rastreamento.md](docs/rastreamento.md).

## Rodar com os formulários
```bash
npx netlify-cli dev   # precisa do .env
```

## Publicar
Todo push na `main` publica automaticamente. Antes: gerar as páginas e conferir `grep -rn "{{" public netlify apps-script` (vazio).

## Endereços
- `/links` (bio do Instagram); `/bio` e o antigo `/link-bio` redirecionam para ele.
- `/politica-de-privacidade` (`/privacidade` redireciona).
