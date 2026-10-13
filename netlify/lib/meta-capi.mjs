// API de Conversões da Meta: envia a conversão pelo servidor (não depende do navegador nem de bloqueador).
// Variáveis de ambiente (Netlify):
//   META_PIXEL_ID          → ID do pixel (mesmo do rastreamento.js)
//   META_CAPI_TOKEN        → token gerado no Gerenciador de Eventos (SECRETO)
//   META_TEST_EVENT_CODE   → opcional: código de "Testar eventos"; com ele os eventos só aparecem no teste
//   META_API_VERSION       → opcional: versão da Graph API (padrão abaixo)
import { createHash } from 'node:crypto';

const VERSAO_PADRAO = 'v26.0';
const EVENTOS = { whatsapp: 'Contact', orcamento: 'Lead', pageview: 'PageView' };

const hash = (valor) => (valor ? createHash('sha256').update(valor).digest('hex') : undefined);

// Normalização exigida pela Meta antes do hash: minúsculas, sem acento, sem espaços extras
const limparNome = (valor) => String(valor || '').normalize('NFD').replace(/[̀-ͯ]/g, '')
  .toLowerCase().replace(/[^a-z\s-]/g, '').trim();

function lerCookie(cabecalho, nome) {
  const achado = String(cabecalho || '').split(/;\s*/).find((c) => c.startsWith(nome + '='));
  return achado ? decodeURIComponent(achado.slice(nome.length + 1)) : undefined;
}

// _fbc vem do cookie; se ainda não existir, monta a partir do fbclid do link do anúncio
function obterFbc(cookies, pagina) {
  const doCookie = lerCookie(cookies, '_fbc');
  if (doCookie) return doCookie;
  try {
    const fbclid = new URL(pagina).searchParams.get('fbclid');
    return fbclid ? 'fb.1.' + Date.now() + '.' + fbclid : undefined;
  } catch {
    return undefined;
  }
}

export function metaConfigurada() {
  return Boolean(process.env.META_PIXEL_ID && process.env.META_CAPI_TOKEN);
}

/**
 * Envia a conversão para a Meta. Nunca lança erro: o lead já está salvo na planilha,
 * falha aqui só vai para o log da função.
 */
export async function enviarConversaoMeta(dados, req) {
  const { META_PIXEL_ID, META_CAPI_TOKEN, META_TEST_EVENT_CODE, META_API_VERSION } = process.env;
  if (!META_PIXEL_ID || !META_CAPI_TOKEN) {
    console.log('API de Conversões da Meta: variáveis ausentes', { META_PIXEL_ID: Boolean(META_PIXEL_ID), META_CAPI_TOKEN: Boolean(META_CAPI_TOKEN) });
    return { enviado: false, motivo: 'nao_configurada', pixel: Boolean(META_PIXEL_ID), token: Boolean(META_CAPI_TOKEN) };
  }
  // LGPD: só envia quem aceitou os cookies no site
  if (dados.consentimento !== 'aceito') {
    console.log('API de Conversões da Meta: não enviado (sem consentimento de cookies)');
    return { enviado: false, motivo: 'sem_consentimento' };
  }

  const cookies = req.headers.get('cookie');
  const digitos = String(dados.telefone || '').replace(/\D/g, '');
  const [primeiroNome, ...resto] = limparNome(dados.nome).split(/\s+/);

  const evento = {
    event_name: EVENTOS[dados.tipo] || 'Lead',
    event_time: Math.floor(Date.now() / 1000),
    event_id: dados.event_id || undefined,            // mesmo ID do pixel no navegador → a Meta conta uma vez
    action_source: 'website',
    event_source_url: dados.pagina || undefined,
    user_data: {
      ph: digitos ? [hash('55' + digitos)] : undefined,
      em: dados.email ? [hash(dados.email.trim().toLowerCase())] : undefined,
      fn: primeiroNome ? [hash(primeiroNome)] : undefined,
      ln: resto.length ? [hash(resto[resto.length - 1])] : undefined,
      country: [hash('br')],
      client_ip_address: req.headers.get('x-nf-client-connection-ip') || req.headers.get('x-forwarded-for')?.split(',')[0]?.trim(),
      client_user_agent: req.headers.get('user-agent') || undefined,
      fbp: lerCookie(cookies, '_fbp'),
      fbc: obterFbc(cookies, dados.pagina)
    },
    custom_data: dados.tipo === 'pageview' ? undefined : {
      content_name: dados.interesse || (dados.tipo === 'orcamento' ? 'Orçamento' : 'WhatsApp'),
      lead_source: dados.utm_source || 'direto'
    }
  };

  const corpo = { data: [evento] };
  if (META_TEST_EVENT_CODE) corpo.test_event_code = META_TEST_EVENT_CODE.trim();

  try {
    const url = `https://graph.facebook.com/${META_API_VERSION || VERSAO_PADRAO}/${META_PIXEL_ID.trim()}/events?access_token=${encodeURIComponent(META_CAPI_TOKEN.trim())}`;
    const resposta = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(corpo),
      signal: AbortSignal.timeout(5000)
    });
    const resultado = await resposta.json().catch(() => ({}));
    if (!resposta.ok) {
      const erro = resultado.error || resultado;
      console.error('API de Conversões da Meta recusou:', resposta.status, JSON.stringify(erro));
      return { enviado: false, motivo: 'erro_meta', status: resposta.status, erro: erro.message || erro.error_user_msg || JSON.stringify(erro).slice(0, 300) };
    }
    console.log('API de Conversões da Meta: evento', evento.event_name, evento.event_id, 'recebido', resultado.events_received);
    return { enviado: true, recebidos: resultado.events_received, teste: Boolean(META_TEST_EVENT_CODE),
      ...(META_TEST_EVENT_CODE ? { resposta_meta: resultado, versao: META_API_VERSION || VERSAO_PADRAO, evento_enviado: { ...evento, user_data: Object.keys(evento.user_data).filter((k) => evento.user_data[k]) } } : {}) };
  } catch (erro) {
    console.error('Falha ao enviar para a API de Conversões da Meta:', erro);
    return { enviado: false, motivo: 'falha_rede', erro: String(erro && erro.message || erro) };
  }
}
