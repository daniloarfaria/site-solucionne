#!/usr/bin/env python3
"""Gera as imagens publicadas a partir dos originais (que nunca vão para o ar).

Uso, na raiz do projeto:
  python3 ferramentas/otimizar_imagens.py

  originais/imagens/fotos/*      → public/assets/img/<nome>-<largura>.webp (duas larguras para o srcset)
  originais/imagens/clientes/*   → public/assets/img/clientes/<nome>.webp
  originais/imagens/associacoes/*→ public/assets/img/associacoes/<nome>.webp
  originais/imagens/marca/*      → logo, favicon e imagem de compartilhamento (og-image.jpg)

Trocou uma foto? Dê um NOME NOVO ao arquivo (o site guarda imagens em cache por 1 ano).
Requer: pip install pillow
"""
import json
import os
from PIL import Image, ImageDraw, ImageFont, ImageOps

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ORIG = os.path.join(RAIZ, 'originais', 'imagens')
DEST = os.path.join(RAIZ, 'public', 'assets', 'img')
FAV = os.path.join(RAIZ, 'public', 'assets', 'favicon')
COR_FUNDO = (14, 14, 15)

# nome do original → (larguras geradas). A primeira é a versão de celular.
FOTOS = {
    'imagem-destaque1.jpg': (800, 1600),
    'imagem-destaque2.jpg': (560, 1000),
    'imagem-destaque3.jpg': (560, 1000),
    'projeto.jpg': (560, 1000),
    'award-photo.jpg': (640, 1100),
    # cards de produto (653x723)
    'difusores-acusticos.png': (400, 653),
    'espumas-acusticas.png': (400, 653),
    'forro-acustico-com-amortecedor.png': (400, 653),
    'janelas-acusticas.png': (400, 653),
    'jateamento-termo-acustico.jpg': (400, 653),
    'paineis-de-absorcao-sonora.png': (400, 653),
    'parede-acustica-com-amortecedor.png': (400, 652),
    'pisos-silenciadores.png': (400, 653),
    'portas-acusticas.png': (400, 653),
    'visores-acusticos.png': (400, 653),
    # topo das páginas de produto
    'forro-acustico2.jpg': (640, 1200),
    'jateamento-termo-acustico2.jpg': (640, 1200),
    'painel-acustico2.jpg': (640, 1200),
    'parede-acustica2.jpg': (640, 1200),
    'piso-acustico2.jpg': (640, 850),
    'porta-acustica2.jpg': (640, 1200),
    'visores-acustico2.jpg': (640, 1200),
    # janela acústica
    'janela-linha-basic.png': (400, 595),
    'janela-linha-confort.png': (400, 595),
    'janela-linha-advanced.png': (400, 595),
    'janela-abertura-de-correr.jpg': (560, 1000),
    'janela-abertura-de-giro.jpg': (560, 1000),
    'janela-instalacao-sobreposta.jpg': (560, 1000),
    'janela-instalacao-embutida.jpg': (560, 1000),
}


def abrir(caminho, alfa=False):
    im = ImageOps.exif_transpose(Image.open(caminho))  # fotos de celular vêm "deitadas" sem isso
    return im.convert('RGBA' if alfa else 'RGB')


def salvar_webp(im, saida, qualidade=78):
    os.makedirs(os.path.dirname(saida), exist_ok=True)
    im.save(saida, 'WEBP', quality=qualidade, method=6)


def fotos():
    tamanhos = {}
    for nome, larguras in FOTOS.items():
        im = abrir(os.path.join(ORIG, 'fotos', nome))
        base = os.path.splitext(nome)[0]
        for w in larguras:
            w = min(w, im.width)
            r = im.resize((w, round(im.height * w / im.width)), Image.LANCZOS) if w < im.width else im
            salvar_webp(r, os.path.join(DEST, f'{base}-{w}.webp'))
        tamanhos[base] = {'larguras': [min(w, im.width) for w in larguras], 'proporcao': round(im.height / im.width, 4)}
        print(f'{nome}: {im.width}x{im.height} → {larguras}')
    # O gerador de páginas lê este arquivo para montar srcset/width/height
    with open(os.path.join(RAIZ, 'ferramentas', 'imagens.json'), 'w') as f:
        json.dump(tamanhos, f, indent=1, sort_keys=True)


def logos():
    for pasta in ('clientes', 'associacoes'):
        for nome in sorted(os.listdir(os.path.join(ORIG, pasta))):
            im = abrir(os.path.join(ORIG, pasta, nome), alfa=True)
            im = im.crop(im.getchannel('A').getbbox())  # tira a margem transparente
            if im.width > 320:
                im = im.resize((320, round(im.height * 320 / im.width)), Image.LANCZOS)
            salvar_webp(im, os.path.join(DEST, pasta, os.path.splitext(nome)[0] + '.webp'), 90)
    logo = abrir(os.path.join(ORIG, 'marca', 'logo.png'), alfa=True)
    logo.save(os.path.join(DEST, 'logo.png'), optimize=True)
    print('logos ok')


def favicon():
    os.makedirs(FAV, exist_ok=True)
    simbolo = abrir(os.path.join(ORIG, 'marca', 'logo-quadrada.png'), alfa=True)
    # O original já é o símbolo vermelho sobre preto; recorta as bordas para o símbolo ficar maior
    bbox = Image.eval(simbolo.convert('L'), lambda v: 255 if v > 40 else 0).getbbox()
    s = simbolo.crop(bbox)

    def icone(tam, proporcao, raio=0.0):
        S = tam * 4
        c = Image.new('RGBA', (S, S), (0, 0, 0, 0))
        ImageDraw.Draw(c).rounded_rectangle([0, 0, S - 1, S - 1], radius=int(S * raio), fill=COR_FUNDO + (255,))
        w = int(S * proporcao)
        h = round(s.height * w / s.width)
        c.alpha_composite(s.resize((w, h), Image.LANCZOS), ((S - w) // 2, (S - h) // 2))
        return c.resize((tam, tam), Image.LANCZOS)

    icone(96, .74, .18).save(os.path.join(FAV, 'favicon-96x96.png'))
    icone(180, .62).convert('RGB').save(os.path.join(FAV, 'apple-touch-icon.png'))
    icone(192, .62).save(os.path.join(FAV, 'web-app-manifest-192x192.png'))
    icone(512, .62).save(os.path.join(FAV, 'web-app-manifest-512x512.png'))
    icone(48, .8, .18).save(os.path.join(FAV, 'favicon.ico'), sizes=[(16, 16), (32, 32), (48, 48)])
    with open(os.path.join(FAV, 'site.webmanifest'), 'w') as f:
        json.dump({
            'name': 'Solucionne – Termo Acústico do Brasil', 'short_name': 'Solucionne',
            'icons': [
                {'src': '/assets/favicon/web-app-manifest-192x192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'maskable'},
                {'src': '/assets/favicon/web-app-manifest-512x512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'maskable'}
            ],
            'theme_color': '#0E0E0F', 'background_color': '#0E0E0F', 'display': 'standalone'
        }, f, indent=2, ensure_ascii=False)
    print('favicon ok')


def og_image():
    foto = abrir(os.path.join(ORIG, 'fotos', 'imagem-destaque1.jpg'))
    w, h = foto.size
    th = round(w * 630 / 1200)
    y = (h - th) // 2
    img = foto.crop((0, y, w, y + th)).resize((1200, 630), Image.LANCZOS).convert('RGBA')
    # Escurece da esquerda para a direita para o texto ficar legível
    grad = Image.new('L', (1200, 1))
    for x in range(1200):
        grad.putpixel((x, 0), int(235 - 150 * x / 1200))
    sombra = Image.new('RGBA', (1200, 630), COR_FUNDO + (0,))
    sombra.putalpha(grad.resize((1200, 630)))
    img.alpha_composite(sombra)
    logo = abrir(os.path.join(ORIG, 'marca', 'logo.png'), alfa=True)
    logo = logo.resize((logo.width * 2, logo.height * 2), Image.LANCZOS)
    img.alpha_composite(logo, (72, 72))
    d = ImageDraw.Draw(img)
    fonte = None
    for caminho in ('/System/Library/Fonts/Supplemental/Arial Bold.ttf', '/Library/Fonts/Arial Bold.ttf'):
        if os.path.exists(caminho):
            fonte = ImageFont.truetype(caminho, 58)
            fonte_p = ImageFont.truetype(caminho.replace(' Bold', ''), 30)
            break
    if fonte:
        d.multiline_text((72, 300), 'A solução ideal para seu\nisolamento acústico.', font=fonte, fill='white', spacing=10)
        d.text((72, 470), 'Projetos e obras acústicas em todo o Brasil', font=fonte_p, fill=(220, 220, 220))
        d.rectangle([72, 448, 152, 452], fill=(160, 18, 23))
    img.convert('RGB').save(os.path.join(DEST, 'og-image-2.jpg'), 'JPEG', quality=84, optimize=True, progressive=True)
    print('og-image ok')


if __name__ == '__main__':
    fotos()
    logos()
    favicon()
    og_image()
