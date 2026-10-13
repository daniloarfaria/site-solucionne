// PageView pela API de Conversões da Meta (complementa o pixel do navegador, com o mesmo event_id).
// Só envia para quem aceitou os cookies. Não grava nada na planilha.
import { enviarConversaoMeta } from '../lib/meta-capi.mjs';
import { origemValida, paginaDoSite } from '../lib/origem.mjs';

export default async (req) => {
  if (req.method !== 'POST') return new Response('Método não permitido', { status: 405, headers: { Allow: 'POST' } });
  if (!origemValida(req)) return resposta({ ok: false }, 403);

  let bruto;
  try { bruto = await req.json(); } catch { return resposta({ ok: false }, 400); }

  const pagina = paginaDoSite(bruto.pagina);
  const eventId = String(bruto.event_id || '').slice(0, 100);
  if (!pagina || !eventId) return resposta({ ok: false }, 400);

  const meta = await enviarConversaoMeta({
    tipo: 'pageview',
    event_id: eventId,
    pagina,
    consentimento: bruto.consentimento
  }, req);
  return resposta({ ok: true, enviado: meta.enviado });
};

export const config = { path: '/api/evento' };

function resposta(corpo, status = 200) {
  return new Response(JSON.stringify(corpo), {
    status,
    headers: { 'Content-Type': 'application/json; charset=utf-8', 'Cache-Control': 'no-store' }
  });
}
