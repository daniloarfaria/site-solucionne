// Recebe o formulário "Solicite um orçamento" e o popup do WhatsApp (tipo "whatsapp"),
// grava no Google Planilhas (Apps Script) e envia a conversão para a API de Conversões da Meta.
// Variáveis de ambiente da Netlify:
//   APPS_SCRIPT_URL      → URL /exec do app da Web
//   FORM_SECRET          → mesma senha cadastrada nas propriedades do Apps Script
//   META_*               → ver netlify/lib/meta-capi.mjs (opcional; sem elas, a Meta é ignorada)
import { enviarConversaoMeta } from '../lib/meta-capi.mjs';
import { origemValida } from '../lib/origem.mjs';

const CAMPOS = [
  'tipo', 'interesse', 'nome', 'email', 'telefone', 'mensagem', 'empresa', 'pagina',
  'utm_source', 'utm_medium', 'utm_campaign', 'utm_content', 'utm_term',
  'event_id', 'consentimento'
];
// Campos que só servem para o rastreamento e não vão para a planilha
const SO_RASTREAMENTO = ['event_id', 'consentimento'];
const OBRIGATORIOS = {
  orcamento: ['nome', 'email', 'telefone', 'mensagem'],
  whatsapp: ['nome', 'telefone']
};
const LIMITE_TEXTO = 2000;

// Telefone: mesma regra de public/assets/js/main.js → guarda "(DD) 9XXXX-XXXX" ou "(DD) XXXX-XXXX"
function normalizarTelefone(valor) {
  let d = String(valor || '').replace(/\D/g, '');
  if (d.startsWith('55') && (String(valor).trim().startsWith('+') || d.length > 11)) d = d.slice(2);
  if (d.startsWith('0')) {
    d = d.replace(/^0+/, '');
    if (d.length > 11) d = d.slice(2);
  }
  const valido = /^[1-9][1-9]9\d{8}$/.test(d) || /^[1-9][1-9][2-5]\d{7}$/.test(d);
  if (!valido) return null;
  const corte = d.length === 11 ? 7 : 6;
  return '(' + d.slice(0, 2) + ') ' + d.slice(2, corte) + '-' + d.slice(corte);
}


export default async (req) => {
  if (req.method !== 'POST') {
    return new Response('Método não permitido', { status: 405, headers: { Allow: 'POST' } });
  }

  if (!origemValida(req)) {
    return json({ ok: false, mensagem: 'Origem não permitida.' }, 403);
  }

  // JavaScript do site manda JSON; sem JavaScript, o navegador manda o formulário comum
  const tipo = req.headers.get('content-type') || '';
  const veioDoJs = tipo.includes('application/json');

  let bruto;
  try {
    bruto = veioDoJs ? await req.json() : Object.fromEntries(await req.formData());
  } catch {
    return responder(veioDoJs, false, 'Dados inválidos.', 400);
  }

  const dados = {};
  for (const campo of CAMPOS) {
    dados[campo] = String(bruto[campo] ?? '').trim().slice(0, LIMITE_TEXTO);
  }

  // Campo "empresa" é invisível no site: se veio preenchido, é robô. Finge sucesso e descarta.
  if (dados.empresa) return responder(veioDoJs, true);

  if (dados.tipo !== 'whatsapp') dados.tipo = 'orcamento';
  if (OBRIGATORIOS[dados.tipo].some((campo) => !dados[campo])) {
    const aviso = dados.tipo === 'whatsapp' ? 'Preencha nome e telefone.' : 'Preencha nome, e-mail, telefone e mensagem.';
    return responder(veioDoJs, false, aviso, 400);
  }
  const telefoneOk = normalizarTelefone(dados.telefone);
  if (!telefoneOk) return responder(veioDoJs, false, 'Telefone inválido. Informe DDD + número.', 400);
  dados.telefone = telefoneOk;

  if (!dados.pagina) dados.pagina = req.headers.get('referer') || '';

  // Diagnóstico da Meta: só existe enquanto META_TEST_EVENT_CODE estiver cadastrada (modo de teste).
  // Envia só para a Meta (não grava na planilha) e devolve a resposta dela.
  if (bruto.diagnostico === true && process.env.META_TEST_EVENT_CODE) {
    const codigo = process.env.META_TEST_EVENT_CODE;
    return json({
      ok: true, diagnostico: true,
      codigo_de_teste: codigo, codigo_tem_espacos: codigo !== codigo.trim(),
      pixel: process.env.META_PIXEL_ID,
      meta: await enviarConversaoMeta(dados, req)
    });
  }

  const { APPS_SCRIPT_URL, FORM_SECRET } = process.env;
  if (!APPS_SCRIPT_URL || !FORM_SECRET) {
    console.error('Faltam as variáveis APPS_SCRIPT_URL e/ou FORM_SECRET na Netlify.');
    return responder(veioDoJs, false, 'Formulário indisponível no momento.', 500);
  }

  const paraPlanilha = { ...dados, segredo: FORM_SECRET };
  SO_RASTREAMENTO.forEach((campo) => delete paraPlanilha[campo]);

  // Planilha e Meta em paralelo; a resposta ao visitante depende só da planilha
  const meta = enviarConversaoMeta(dados, req);
  try {
    // O Apps Script responde com um redirecionamento; o fetch segue e lê o JSON final
    const resposta = await fetch(APPS_SCRIPT_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'text/plain;charset=utf-8' },
      body: JSON.stringify(paraPlanilha),
      signal: AbortSignal.timeout(9000)
    });
    const resultado = await resposta.json();
    if (!resultado.ok) throw new Error(resultado.mensagem || 'Apps Script recusou o envio');
    await meta;
    return responder(veioDoJs, true);
  } catch (erro) {
    console.error('Falha ao gravar na planilha:', erro);
    return responder(veioDoJs, false, 'Erro ao enviar. Tente novamente ou chame no WhatsApp.', 502);
  }
};

export const config = { path: '/api/orcamento' };

function json(corpo, status = 200) {
  return new Response(JSON.stringify(corpo), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' }
  });
}

function responder(veioDoJs, ok, mensagem = '', status = 200) {
  if (veioDoJs) return json({ ok, mensagem }, status);
  // Sem JavaScript: leva para a página de obrigado ou de volta ao formulário
  return new Response(null, {
    status: 303,
    headers: { Location: ok ? '/obrigado.html' : '/#contato' }
  });
}
