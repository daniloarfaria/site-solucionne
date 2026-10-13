document.addEventListener('DOMContentLoaded', function () {
  // Navegação: fundo sólido ao rolar
  const nav = document.querySelector('.nav');
  if (nav) {
    const onScroll = () => nav.classList.toggle('is-scrolled', window.scrollY > 24);
    requestAnimationFrame(onScroll);
    window.addEventListener('scroll', onScroll, { passive: true });

    // Menu do celular: abre/fecha e fecha ao escolher um link
    const toggle = nav.querySelector('.nav__toggle');
    const fecharMenu = () => {
      nav.classList.remove('is-open');
      document.body.classList.remove('menu-aberto');
      toggle.setAttribute('aria-expanded', 'false');
    };
    if (toggle) {
      toggle.addEventListener('click', () => {
        const aberto = nav.classList.toggle('is-open');
        document.body.classList.toggle('menu-aberto', aberto);
        toggle.setAttribute('aria-expanded', String(aberto));
      });
      nav.querySelectorAll('.nav__menu a').forEach((a) => a.addEventListener('click', fecharMenu));
      document.addEventListener('keydown', (e) => { if (e.key === 'Escape') fecharMenu(); });
    }

    // Submenu de produtos: clique (toque) além do hover
    const sub = nav.querySelector('.nav__sub');
    if (sub) {
      const botao = sub.querySelector('button');
      botao.addEventListener('click', () => {
        const aberto = sub.classList.toggle('is-open');
        botao.setAttribute('aria-expanded', String(aberto));
      });
      document.addEventListener('click', (e) => {
        if (!sub.contains(e.target)) { sub.classList.remove('is-open'); botao.setAttribute('aria-expanded', 'false'); }
      });
    }
  }

  // Revelação dos elementos ao entrar na tela
  const reveals = document.querySelectorAll('.reveal');
  if ('IntersectionObserver' in window) {
    // Escalona elementos irmãos para entrarem em sequência
    reveals.forEach((el) => {
      const siblings = Array.from(el.parentElement.children).filter((c) => c.classList.contains('reveal'));
      el.style.setProperty('--delay', (siblings.indexOf(el) * 0.08) + 's');
    });
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    reveals.forEach((el) => observer.observe(el));
  } else {
    reveals.forEach((el) => el.classList.add('is-visible'));
  }

  // Ano no rodapé
  const ano = document.getElementById('ano');
  if (ano) ano.textContent = new Date().getFullYear();

  // Parâmetros UTM: se a URL trouxer algum, valem só os da URL (não mistura origens);
  // sem nenhum, usa o padrão da página (ex.: <body data-utm-source="instagram"> nos links da bio)
  const UTM_KEYS = ['utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term'];
  const urlParams = new URLSearchParams(window.location.search);
  const urlTemUtm = UTM_KEYS.some((key) => urlParams.get(key));
  const getUtm = (key) => {
    if (urlTemUtm) return urlParams.get(key) || '';
    return document.body.dataset[key.replace(/_(\w)/g, (m, c) => c.toUpperCase())] || '';
  };

  // Netlify Function que repassa para a planilha (a URL do Apps Script fica escondida nela)
  const endpoint = '/api/orcamento';

  // ===== Telefone =====
  // Aceita qualquer jeito de digitar: +55 31 90000-0000, 5531900000000, 031 90000 0000, (31)90000-0000...
  // Guarda sempre só DDD + número (10 ou 11 dígitos). Mesma regra em netlify/functions/orcamento.mjs.
  const telefone = {
    normalizar(valor) {
      let d = String(valor || '').replace(/\D/g, '');
      // Código do país: com "+", ou quando sobram dígitos demais começando por 55
      if (d.startsWith('55') && (String(valor).trim().startsWith('+') || d.length > 11)) d = d.slice(2);
      // Zero de discagem (0 31...) e código de operadora (0 21 31...)
      if (d.startsWith('0')) {
        d = d.replace(/^0+/, '');
        if (d.length > 11) d = d.slice(2);
      }
      return d;
    },
    // Celular: DDD + 9 + 8 dígitos. Fixo: DDD + 8 dígitos começando de 2 a 5.
    valido(d) {
      return /^[1-9][1-9]9\d{8}$/.test(d) || /^[1-9][1-9][2-5]\d{7}$/.test(d);
    },
    formatar(d) {
      if (d.length <= 2) return d ? '(' + d : '';
      const ddd = '(' + d.slice(0, 2) + ') ';
      const resto = d.slice(2);
      if (resto.length <= 4) return ddd + resto;
      const corte = resto.length > 8 ? 5 : 4;
      return ddd + resto.slice(0, corte) + '-' + resto.slice(corte);
    },
    // Máscara durante a digitação; quem começa com "+" vê o que digitou até sair do campo
    mascarar(campo) {
      campo.setAttribute('maxlength', '20');
      campo.addEventListener('input', () => {
        const bruto = campo.value;
        if (bruto.trim().startsWith('+')) {
          campo.value = bruto.replace(/[^\d+\s()-]/g, '');
          return;
        }
        const digitos = bruto.replace(/\D/g, '').slice(0, 15);
        const d = digitos.length > 11 ? telefone.normalizar(digitos) : digitos;
        campo.value = telefone.formatar(d.slice(0, 11));
      });
      campo.addEventListener('blur', () => {
        const d = telefone.normalizar(campo.value);
        if (d) campo.value = telefone.formatar(d.slice(0, 11));
      });
    }
  };

  // ===== Eventos de rastreamento =====
  // Todos os eventos passam por track() / trackConversao(); quem envia para Google e Meta é o rastreamento.js.
  // Lista completa e parâmetros: docs/rastreamento.md
  const rastreamento = window.rastreamento || {
    evento() {}, conversao() {}, consentimento: () => '', definirConsentimento() {}
  };
  const track = (event, params) => rastreamento.evento(event, params);

  // ID único da conversão: o mesmo vai pelo navegador (pixel) e pelo servidor (API de Conversões),
  // e a Meta conta uma vez só
  const novoEventId = () => (window.crypto && crypto.randomUUID)
    ? crypto.randomUUID()
    : Date.now().toString(36) + Math.random().toString(36).slice(2);

  const trackConversao = (event, params, contato, eventId) => {
    rastreamento.conversao(event, params, {
      telefone: telefone.normalizar(contato.telefone),
      email: contato.email,
      nome: contato.nome
    }, eventId);
  };

  // Onde o elemento clicado está na página (para comparar botões no relatório)
  const LOCAIS = [
    ['.float-whats', 'botao_flutuante'], ['.nav', 'menu'], ['.hero', 'topo'], ['.janela-linhas', 'produto'],
    ['.card', 'produto'], ['.service', 'servico'], ['.cta', 'chamada'],
    ['.faq', 'duvidas'], ['.contact', 'contato'], ['.footer', 'rodape'],
    ['.bio__links', 'link_bio'], ['.bio', 'link_bio'], ['.simple', 'pagina_simples']
  ];
  const localDe = (el) => {
    const achado = LOCAIS.find(([seletor]) => el.closest(seletor));
    return achado ? achado[1] : 'outro';
  };
  const interesseDe = (link) => {
    const titulo = link.closest('article') && link.closest('article').querySelector('h3');
    return link.dataset.interesse || (titulo ? titulo.firstChild.textContent.trim() : '');
  };

  // Cliques em links de contato, rotas, redes sociais e botões da página de links
  document.addEventListener('click', (e) => {
    const link = e.target.closest('a[href]');
    if (!link) return;
    const href = link.getAttribute('href');
    const local = localDe(link);

    if (/wa\.me\//.test(href)) {
      track('whatsapp_clique', { local_clique: local, interesse: interesseDe(link) || 'Contato geral' });
    } else if (href.startsWith('tel:')) {
      track('telefone_clique', { local_clique: local });
    } else if (href.startsWith('mailto:')) {
      track('email_clique', { local_clique: local });
    } else if (/google\.com\/maps/.test(href)) {
      track('rota_clique', { local_clique: local });
    } else if (link.closest('.social')) {
      track('rede_social_clique', { local_clique: local, rede_social: (link.getAttribute('aria-label') || '').split(' ')[0].toLowerCase() });
    }

    if (link.classList.contains('bio__link')) {
      const texto = link.querySelector('strong');
      track('link_bio_clique', { botao: texto ? texto.textContent.trim() : href });
    }
  }, true);

  // ===== Aviso de cookies (LGPD) =====
  // Padrão negado é definido no rastreamento.js (no <head>); aqui a pessoa escolhe e Google/Meta são avisados.
  const aplicarEscolha = (escolha) => rastreamento.definirConsentimento(escolha);

  const abrirAvisoCookies = () => {
    if (document.querySelector('.cookies')) return;
    const aviso = document.createElement('div');
    aviso.className = 'cookies';
    aviso.setAttribute('role', 'region');
    aviso.setAttribute('aria-label', 'Aviso de cookies');
    aviso.innerHTML =
      '<p>Usamos cookies para medir visitas e anúncios. Você escolhe se aceita. ' +
      '<a href="/politica-de-privacidade#cookies">Saiba mais</a></p>' +
      '<div class="cookies__acoes">' +
      '<button type="button" class="btn btn--ghost-dark btn--sm" data-escolha="recusado">Recusar</button>' +
      '<button type="button" class="btn btn--red btn--sm" data-escolha="aceito">Aceitar</button>' +
      '</div>';
    aviso.addEventListener('click', (e) => {
      const botao = e.target.closest('[data-escolha]');
      if (!botao) return;
      aplicarEscolha(botao.dataset.escolha);
      aviso.remove();
    });
    document.body.appendChild(aviso);
  };

  if (!rastreamento.consentimento()) abrirAvisoCookies();
  document.addEventListener('click', (e) => {
    if (e.target.closest('[data-abrir-cookies]')) { e.preventDefault(); abrirAvisoCookies(); }
  });

  // Perguntas frequentes abertas
  document.querySelectorAll('.faq__item').forEach((item) => {
    item.addEventListener('toggle', () => {
      if (item.open) track('duvida_aberta', { pergunta: item.querySelector('summary').textContent.trim() });
    });
  });

  // Formulário de orçamento (página inicial e páginas de produto)
  const form = document.getElementById('contato-form');
  if (form) initOrcamento();

  function initOrcamento() {
    const fillUtms = () => {
      UTM_KEYS.forEach((key) => { document.getElementById(key).value = getUtm(key); });
    };
    fillUtms();

    const status = document.getElementById('form-status');
    const button = form.querySelector('button[type="submit"]');

    const setStatus = (message, type) => {
      status.textContent = message;
      status.className = 'form-status ' + (type ? 'is-' + type : '');
    };

    const successMessage = 'Mensagem enviada com sucesso! Em breve entraremos em contato.';
    telefone.mascarar(form.telefone);

    // Primeira interação com o formulário
    let iniciou = false;
    form.addEventListener('focusin', () => {
      if (iniciou) return;
      iniciou = true;
      track('form_orcamento_inicio', {});
    });

    // Manipula o evento de envio do formulário
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      // Robô preencheu o campo escondido: finge sucesso e descarta
      if (form.empresa.value) {
        setStatus(successMessage, 'ok');
        form.reset();
        fillUtms();
        return;
      }

      const fone = telefone.normalizar(form.telefone.value);
      if (!telefone.valido(fone)) {
        setStatus('Confira o telefone: informe DDD + número, ex.: (31) 90000-0000.', 'error');
        track('form_orcamento_erro', { motivo: 'telefone_invalido' });
        form.telefone.focus();
        return;
      }
      form.telefone.value = telefone.formatar(fone);

      // Coleta os dados do formulário
      const data = {
        nome: form.nome.value,
        email: form.email.value,
        telefone: telefone.formatar(fone),
        mensagem: form.mensagem.value,
        interesse: form.interesse ? form.interesse.value : '',
        utm_source: form.utm_source.value,
        utm_medium: form.utm_medium.value,
        utm_campaign: form.utm_campaign.value,
        utm_content: form.utm_content.value,
        utm_term: form.utm_term.value,
        pagina: window.location.href,
        event_id: novoEventId(),
        consentimento: rastreamento.consentimento()
      };

      button.disabled = true;
      setStatus('Enviando…');

      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
      })
        .then((response) => response.json())
        .then((result) => {
          if (!result.ok) throw new Error(result.mensagem || 'Falha ao salvar');
          trackConversao('form_orcamento_enviado', {
            interesse: data.interesse || 'Contato geral',
            utm_source: data.utm_source, utm_medium: data.utm_medium, utm_campaign: data.utm_campaign
          }, { email: data.email, telefone: data.telefone, nome: data.nome }, data.event_id);
          setStatus(successMessage, 'ok');
          form.reset();
          fillUtms();
        })
        .catch((error) => {
          console.error('Erro ao enviar:', error);
          track('form_orcamento_erro', { motivo: error.message });
          setStatus('Erro ao enviar. Tente novamente ou chame no WhatsApp.', 'error');
        })
        .finally(() => {
          button.disabled = false;
        });
    });
  }

  // ===== Popup antes do WhatsApp =====
  // Captura nome e telefone, registra na planilha (com UTMs) e segue para o WhatsApp
  const lead = document.getElementById('lead-whats');
  if (!lead) return;
  const leadForm = document.getElementById('lead-form');
  const leadErro = document.getElementById('lead-erro');
  const leadInteresse = document.getElementById('lead-interesse');
  const LEAD_KEY = 'sol_lead_whats';
  let destino = null;
  let enviouLead = false;

  const storage = {
    get: () => { try { return sessionStorage.getItem(LEAD_KEY); } catch (err) { return null; } },
    set: (v) => { try { sessionStorage.setItem(LEAD_KEY, v); } catch (err) { /* sem armazenamento */ } }
  };

  telefone.mascarar(leadForm.telefone);

  // Abre em nova aba como os links originais; se o navegador bloquear, abre na mesma
  const abrirWhatsApp = (url) => {
    const aba = window.open(url, '_blank');
    if (aba) aba.opener = null;
    else window.location.href = url;
  };

  if (typeof lead.showModal === 'function') {
    document.addEventListener('click', (e) => {
      const link = e.target.closest('a[href*="wa.me/"]');
      if (!link) return;

      // Já preencheu nesta visita: vai direto
      if (storage.get()) return;

      e.preventDefault();
      // Interesse: atributo data-interesse do link ou o título do card do produto/serviço
      const interesse = interesseDe(link);
      // UTMs fixas do botão (data-utm-source, data-utm-content...) têm prioridade sobre as da página
      const utmDoLink = {};
      UTM_KEYS.forEach((key) => {
        const valor = link.dataset[key.replace(/_(\w)/g, (m, c) => c.toUpperCase())];
        if (valor) utmDoLink[key] = valor;
      });
      destino = { url: link.href, interesse: interesse || 'Contato geral', utm: utmDoLink, local: localDe(link) };
      leadInteresse.textContent = interesse
        ? 'Sobre ' + interesse + '. Informe seu nome e telefone para continuar.'
        : 'Informe seu nome e telefone para continuar.';
      leadErro.textContent = '';
      enviouLead = false;
      lead.showModal();
      leadForm.nome.focus();
      track('whatsapp_popup_aberto', { local_clique: destino.local, interesse: destino.interesse });
    });

    // Fechou sem preencher
    lead.addEventListener('close', () => {
      if (!enviouLead && destino) track('whatsapp_popup_fechado', { local_clique: destino.local, interesse: destino.interesse });
    });

    lead.querySelector('[data-fechar]').addEventListener('click', () => lead.close());
    // Clique fora do cartão fecha o popup
    lead.addEventListener('click', (e) => { if (e.target === lead) lead.close(); });
  }

  leadForm.addEventListener('submit', (e) => {
    e.preventDefault();
    if (!destino) return;

    const nome = leadForm.nome.value.trim();
    const fone = telefone.normalizar(leadForm.telefone.value);
    const invalido = (campo, mensagem) => {
      leadErro.textContent = mensagem;
      leadForm[campo].focus();
      track('whatsapp_popup_erro', { campo: campo });
    };
    if (nome.length < 2) return invalido('nome', 'Informe seu nome.');
    if (!telefone.valido(fone)) return invalido('telefone', 'Confira o telefone: DDD + número, ex.: (31) 90000-0000.');
    const foneFormatado = telefone.formatar(fone);

    // Mensagem do WhatsApp já vem com o nome da pessoa
    const url = new URL(destino.url);
    url.searchParams.set('text', (url.searchParams.get('text') || '').trim() + ' Meu nome é ' + nome + '.');

    if (!leadForm.empresa.value) {
      const data = {
        tipo: 'whatsapp',
        nome: nome,
        telefone: foneFormatado,
        interesse: destino.interesse,
        pagina: window.location.href,
        event_id: novoEventId(),
        consentimento: rastreamento.consentimento()
      };
      const temUtmNoLink = Object.keys(destino.utm).length > 0;
      UTM_KEYS.forEach((key) => { data[key] = temUtmNoLink ? (destino.utm[key] || '') : getUtm(key); });

      // keepalive: o envio termina mesmo depois que a página vai para o WhatsApp
      fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
        keepalive: true
      }).catch((error) => console.error('Erro ao registrar lead:', error));

      trackConversao('lead_whatsapp', {
        local_clique: destino.local, interesse: destino.interesse,
        utm_source: data.utm_source, utm_medium: data.utm_medium, utm_campaign: data.utm_campaign, utm_content: data.utm_content
      }, { telefone: fone, nome: nome }, data.event_id);
    }

    enviouLead = true;
    storage.set('1');
    lead.close();
    leadForm.reset();
    abrirWhatsApp(url.toString());
  });
});
