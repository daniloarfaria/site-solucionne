# Site Solucionne — contexto do projeto

Cliente da agência. **Isolamento (LGPD):** não usar arquivos de outros clientes, da Melvin ou pessoais aqui.

- Padrão: skill `site-cliente-netlify` (estrutura `public/`, formulários via função, rastreamento direto, LGPD).
- Hospedagem: Netlify plano grátis (100 GB/mês de banda, 125 mil chamadas de função/mês). Não usar Netlify Forms.
- **Páginas são geradas**: edite `ferramentas/gerar_paginas.py` e rode `python3 ferramentas/gerar_paginas.py`. Nunca editar `public/*.html` à mão.
- Imagens: originais em `originais/imagens/`, publicar só `.webp` via `ferramentas/otimizar_imagens.py`. Trocar imagem = nome novo (cache de 1 ano).
- Identidade: vermelho `#A01217` (texto vermelho sobre escuro: `#F0464C`), fundo `#0E0E0F`, fonte Inter hospedada. Visual escuro, premium, técnico.
- Rastreamento: `public/assets/js/rastreamento.js` (GA4 `G-97STC6HHXB`, Ads `AW-715247679`; pixel da Meta pendente). Não reintroduzir o GTM/Stape antigo. Detalhes em `docs/rastreamento.md`.
- Sem `<script>` embutido nas páginas (a CSP do `netlify.toml` bloqueia).
- Conteúdo: não inventar depoimentos, números ou clientes. Os depoimentos do site antigo foram retirados por parecerem fictícios; só voltam com depoimentos reais autorizados.
