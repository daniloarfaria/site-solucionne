/*
 * Rastreamento direto no site (sem Google Tag Manager): Google Ads, Google Analytics 4 e Pixel da Meta.
 * Carregado no <head> de todas as páginas, ANTES de qualquer outro script.
 *
 * IDs abaixo são públicos (aparecem no navegador de qualquer forma). O que é secreto — o token da
 * API de Conversões da Meta — fica só nas variáveis de ambiente da Netlify (ver docs/rastreamento.md).
 * ID em branco = ferramenta desligada.
 */
(function () {
  var CONFIG = {
    googleAds: 'AW-715247679',
    ga4: 'G-97STC6HHXB',
    metaPixel: '',      // ID do pixel da Meta (ex.: '1234567890123456'); em branco = desligado
    // Conversões do Google Ads: evento do site → "AW-ID/rótulo"
    conversoesGoogleAds: {
      lead_whatsapp: 'AW-715247679/cvCVCML-wLoZEL-gh9UC',
      form_orcamento_enviado: 'AW-715247679/lvtTCNn_obcZEL-gh9UC'
    },
    // Eventos padrão da Meta para as conversões do site
    eventosMeta: {
      lead_whatsapp: 'Contact',
      form_orcamento_enviado: 'Lead'
    },
    chaveConsentimento: 'sol_consentimento'
  };

  var html = document.documentElement;
  html.classList.add('js');
  var tipoPagina = html.getAttribute('data-pagina') || 'outra';

  window.dataLayer = window.dataLayer || [];
  function gtag() { window.dataLayer.push(arguments); }
  window.gtag = gtag;

  // ===== Consentimento (LGPD) =====
  // Tudo que grava cookie de anúncio/análise começa negado até a pessoa aceitar.
  var escolha = null;
  try { escolha = localStorage.getItem(CONFIG.chaveConsentimento); } catch (e) {}
  var aceitou = escolha === 'aceito';
  var status = aceitou ? 'granted' : 'denied';
  gtag('consent', 'default', {
    ad_storage: status, ad_user_data: status, ad_personalization: status, analytics_storage: status,
    functionality_storage: 'granted', security_storage: 'granted', wait_for_update: 500
  });
  gtag('set', 'ads_data_redaction', !aceitou);
  gtag('set', 'url_passthrough', true);

  // ===== Google (Ads + GA4 num único gtag.js) =====
  var idPrincipal = CONFIG.ga4 || CONFIG.googleAds;
  if (idPrincipal) {
    var s = document.createElement('script');
    s.async = true;
    s.src = 'https://www.googletagmanager.com/gtag/js?id=' + idPrincipal;
    document.head.appendChild(s);
    gtag('js', new Date());
    if (CONFIG.ga4) gtag('config', CONFIG.ga4, { tipo_pagina: tipoPagina });
    if (CONFIG.googleAds) gtag('config', CONFIG.googleAds, { allow_enhanced_conversions: true });
  }

  // ===== Pixel da Meta (só carrega depois do aceite) =====
  var metaCarregado = false;
  function carregarMeta() {
    if (!CONFIG.metaPixel || metaCarregado) return;
    metaCarregado = true;
    /* eslint-disable */
    !function (f, b, e, v, n, t, s) {
      if (f.fbq) return; n = f.fbq = function () { n.callMethod ? n.callMethod.apply(n, arguments) : n.queue.push(arguments); };
      if (!f._fbq) f._fbq = n; n.push = n; n.loaded = !0; n.version = '2.0'; n.queue = [];
      t = b.createElement(e); t.async = !0; t.src = v; s = b.getElementsByTagName(e)[0]; s.parentNode.insertBefore(t, s);
    }(window, document, 'script', 'https://connect.facebook.net/en_US/fbevents.js');
    /* eslint-enable */
    // Sem eventos automáticos da Meta (cliques em qualquer botão): só os eventos definidos aqui
    window.fbq('set', 'autoConfig', false, CONFIG.metaPixel);
    window.fbq('init', CONFIG.metaPixel);
    // PageView pelo navegador e pelo servidor (API de Conversões) com o mesmo ID: a Meta conta uma vez
    var idPageView = novoId();
    window.fbq('track', 'PageView', {}, { eventID: idPageView });
    enviarPageViewServidor(idPageView);
  }

  function novoId() {
    return (window.crypto && crypto.randomUUID) ? crypto.randomUUID()
      : Date.now().toString(36) + Math.random().toString(36).slice(2);
  }

  // Espera o pixel criar o cookie _fbp (até 3 s) para o servidor mandar a mesma identificação
  function enviarPageViewServidor(eventId) {
    var tentativas = 0;
    (function enviar() {
      if (document.cookie.indexOf('_fbp=') === -1 && tentativas++ < 6) return setTimeout(enviar, 500);
      try {
        fetch('/api/evento', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ event_id: eventId, pagina: location.href, consentimento: 'aceito' }),
          keepalive: true
        }).catch(function () {});
      } catch (e) {}
    })();
  }

  // Correspondência avançada do pixel: telefone, e-mail e nome (o pixel criptografa antes de enviar)
  function dadosMeta(contato) {
    var d = {};
    if (contato.telefone) d.ph = '55' + contato.telefone;
    if (contato.email) d.em = contato.email.trim().toLowerCase();
    var nomes = String(contato.nome || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '')
      .toLowerCase().replace(/[^a-z\s-]/g, '').trim().split(/\s+/).filter(Boolean);
    if (nomes.length) d.fn = nomes[0];
    if (nomes.length > 1) d.ln = nomes[nomes.length - 1];
    d.country = 'br';
    return d;
  }
  if (aceitou) carregarMeta();

  // ===== API usada pelo main.js =====
  var conversaoGoogle = function (evento, eventId) {
    var destino = CONFIG.conversoesGoogleAds[evento];
    if (destino) gtag('event', 'conversion', { send_to: destino, transaction_id: eventId });
  };

  window.rastreamento = {
    // Evento comum: vai para o GA4 (se configurado)
    evento: function (nome, params) {
      if (CONFIG.ga4) gtag('event', nome, Object.assign({ send_to: CONFIG.ga4, tipo_pagina: tipoPagina }, params || {}));
    },
    // Conversão: GA4 + Google Ads (com dados para conversões otimizadas) + Meta (mesmo ID da API de Conversões)
    conversao: function (nome, params, contato, eventId) {
      var digitos = (contato && contato.telefone) || '';
      var userData = {};
      if (digitos) userData.phone_number = '+55' + digitos;
      if (contato && contato.email) userData.email = contato.email.trim().toLowerCase();
      if (userData.phone_number || userData.email) gtag('set', 'user_data', userData);

      this.evento(nome, Object.assign({ event_id: eventId }, params || {}));
      conversaoGoogle(nome, eventId);
      var eventoMeta = CONFIG.eventosMeta[nome];
      if (eventoMeta && metaCarregado && window.fbq) {
        window.fbq('init', CONFIG.metaPixel, dadosMeta(contato || {}));
        window.fbq('track', eventoMeta, { content_name: (params && params.interesse) || nome }, { eventID: eventId });
      }
    },
    consentimento: function () {
      try { return localStorage.getItem(CONFIG.chaveConsentimento) || ''; } catch (e) { return ''; }
    },
    definirConsentimento: function (valor) {
      try { localStorage.setItem(CONFIG.chaveConsentimento, valor); } catch (e) {}
      var st = valor === 'aceito' ? 'granted' : 'denied';
      gtag('consent', 'update', { ad_storage: st, ad_user_data: st, ad_personalization: st, analytics_storage: st });
      gtag('set', 'ads_data_redaction', st === 'denied');
      if (valor === 'aceito') { if (window.fbq) window.fbq('consent', 'grant'); carregarMeta(); }
      else if (window.fbq) window.fbq('consent', 'revoke');
      this.evento('consentimento_cookies', { escolha: valor });
    }
  };
})();
