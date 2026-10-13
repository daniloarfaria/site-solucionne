// Domínios que podem chamar as funções: o site, as prévias da Netlify e testes locais
export const ORIGEM_PERMITIDA = /^https?:\/\/(([a-z0-9-]+\.)*solucionne\.com\.br|[a-z0-9-]+\.netlify\.app|localhost(:\d+)?|127\.0\.0\.1(:\d+)?)$/i;

export function origemValida(req) {
  const origem = req.headers.get('origin');
  return !origem || ORIGEM_PERMITIDA.test(origem);
}

// A URL informada precisa ser de uma página do próprio site
export function paginaDoSite(url) {
  try {
    const u = new URL(url);
    return ORIGEM_PERMITIDA.test(u.origin) ? u.toString().slice(0, 2000) : '';
  } catch {
    return '';
  }
}
