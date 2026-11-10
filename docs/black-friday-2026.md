# Mês da Black Friday 2026 — como desfazer (em dezembro)

Pedido da cliente em 10/11/2026. Só a página de links da bio (`/links`) foi alterada.

## O que mudou
Em `ferramentas/gerar_paginas.py`, função `pagina_links()`:
1. O botão **"Orçamento de Janela Acústica"** virou **"MÊS DA BLACK FRIDAY SOLUCIONNE"** (classe extra `bio__link--bf`, `data-utm-content="whatsapp_blackfriday"`, interesse "Black Friday").
   - Mensagem automática do WhatsApp: "Vim pela Black! Gostaria de saber mais sobre o Mês da Black Friday Solucionne." (identifica quem chegou pela campanha).
2. Foram removidos da seção "No site" os links **Janelas acústicas** e **Portas acústicas**. A cliente pediu a retirada em definitivo; a de dezembro só reverte o item 1 (confirmar com ela se quer os links de volta).
3. Em `public/assets/css/styles.css`: bloco `.bio__link--bf` (degradê preto/vermelho, borda e brilho), logo antes de `.bio__titulo`. Pode ser apagado.

## Como desfazer o card
Trocar a linha do botão `whatsapp_blackfriday` por:

```python
botao('Vim pelo Instagram e gostaria de um orçamento de Janela Acústica.', 'Orçamento de Janela Acústica', 'Linhas Basic, Confort e Advanced', 'whatsapp_janela', 'Janela Acústica'),
```

Apagar as 4 linhas `.bio__link--bf` do CSS, rodar `python3 ferramentas/gerar_paginas.py` e dar push na `main`.

Também dá para reverter pelo git: `git revert <commit "black friday">` (traz de volta os links de janelas e portas também).

## Pendente
- Área de obras no site (clientes com 3 ou mais serviços), ainda sem definição da cliente. Clientes citados por ela: Audi, Banco do Brasil, Correios, Inter, PMMG, PUC Minas, Sebrae e Stellantis. Só publicar com autorização de uso das marcas.
