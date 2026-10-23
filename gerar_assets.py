# Gera os SVGs (banner, títulos, divisor, rodapé) com o texto convertido em contorno.
# Edite as variáveis abaixo e rode: python3 gerar_assets.py
import random, html
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen

NOME = "Gabriel"
PAPEL = "Desenvolvedor web, dados e automação"
SUSSURROS = ["ele observa", "não olhe para trás", "as estrelas estão erradas", "o código sabe seu nome"]
TITULOS = {"sobre": "Sobre", "arquivos": "Arquivos", "bestiario": "Bestiário", "diario": "Diário", "invocacao": "Invocação"}
RODAPE = "Se você chegou até aqui, ele também chegou."
OSSO, SANGUE, LUA, ABISMO = "#d8d0bf", "#8c1d2b", "#9a93c4", "#060509"

_c = {}
def tp(k, t, tam, x=0, y=0):
    if k not in _c:
        f = TTFont({"d": "fontes/pirata.woff", "i": "fontes/fell-italic.woff"}[k])
        _c[k] = (f.getGlyphSet(), f.getBestCmap(), f["head"].unitsPerEm)
    gs, cm, upm = _c[k]; s = tam / upm; cx = x; ds = []
    for ch in t:
        g = cm.get(ord(ch))
        if g is None: cx += tam * .3; continue
        p = SVGPathPen(gs, ntos=lambda v: ('%.1f' % v).rstrip('0').rstrip('.')); gs[g].draw(TransformPen(p, (s, 0, 0, -s, cx, y))); ds.append(p.getCommands()); cx += gs[g].width * s
    return " ".join(ds), cx - x

def svg(w, h, corpo, css=""):
    open(corpo[0], "w", encoding="utf-8").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{corpo[2]}">'
        f'<style>@media(prefers-reduced-motion:reduce){{*{{animation:none!important}}}}{css}</style>{corpo[1]}</svg>')

# Banner
random.seed(7); W, H = 1200, 420
_, w100 = tp("d", NOME, 100); tam = min(250, 1080 * 100 / w100)
dn, _ = tp("d", NOME, tam, 60, 290)
FI = "font-family=\"'IM Fell English',Georgia,'Times New Roman',serif\" font-style=\"italic\""
def tx(t, x, y, z, c): return f'<text x="{x}" y="{y}" {FI} font-size="{z}" fill="{c}">{html.escape(t)}</text>'
xs, ys = [700, 150, 880, 420], [90, 160, 60, 125]
sus = "".join(tx(s, x, y, 30, SANGUE) for s, x, y in zip(SUSSURROS, xs, ys))
part = "".join(
    f'<circle cx="{random.randint(0,W)}" r="{random.uniform(.8,2.2):.1f}" fill="{OSSO}" opacity="{random.uniform(.15,.5):.2f}">'
    f'<animate attributeName="cy" from="{H+5}" to="-5" dur="{random.randint(12,26)}s" begin="-{random.randint(0,20)}s" repeatCount="indefinite"/></circle>' for _ in range(22))
mov = f'values="150;1050;150" dur="16s" repeatCount="indefinite"'
css = (f".r{{animation:gr 7s steps(1) infinite}}.l{{animation:gl 7s steps(1) infinite}}"
       "@keyframes gr{0%,90%,100%{transform:translate(-3px,0)}93%{transform:translate(-10px,2px)}96%{transform:translate(4px,-2px)}}"
       "@keyframes gl{0%,90%,100%{transform:translate(3px,0)}93%{transform:translate(10px,-2px)}96%{transform:translate(-4px,2px)}}")
corpo = ("assets/banner.svg",
  f'<defs><radialGradient id="mg"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></radialGradient>'
  f'<radialGradient id="gl"><stop offset="0" stop-color="{LUA}" stop-opacity=".2"/><stop offset="1" stop-color="{LUA}" stop-opacity="0"/></radialGradient>'
  f'<mask id="m"><rect width="{W}" height="{H}" fill="#000"/><circle cy="200" r="170" fill="url(#mg)"><animate attributeName="cx" {mov}/></circle></mask>'
  f'<filter id="b"><feGaussianBlur stdDeviation="0"><animate attributeName="stdDeviation" values="18;0" dur="3s" fill="freeze"/></feGaussianBlur></filter></defs>'
  f'<rect width="{W}" height="{H}" fill="{ABISMO}"/><circle cy="200" r="280" fill="url(#gl)"><animate attributeName="cx" {mov}/></circle>'
  f'<g mask="url(#m)">{sus}</g>{part}'
  f'<path id="n" d="{dn}" fill="none"/><g filter="url(#b)"><use href="#n" class="r" fill="{SANGUE}" opacity=".8"/><use href="#n" class="l" fill="{LUA}" opacity=".55"/><use href="#n" fill="{OSSO}"/>'
  + tx(PAPEL, 66, 355, 34, LUA) + f'</g><rect x="60" y="392" width="1080" height="2" fill="{SANGUE}" opacity=".7"/>',
  f"{NOME}, {PAPEL}")
svg(W, H, corpo, css)

# Títulos das seções
for k, t in TITULOS.items():
    d, w = tp("d", t, 60, 0, 58)
    svg(int(w) + 8, 80, (f"assets/h-{k}.svg", f'<path d="{d}" fill="{OSSO}"/><rect y="68" width="{int(w)}" height="2" fill="{SANGUE}"/>', t))

# Divisor
svg(800, 24, ("assets/divisor.svg",
  f'<defs><linearGradient id="g"><stop offset="0" stop-color="{SANGUE}" stop-opacity="0"/><stop offset=".5" stop-color="{SANGUE}"/><stop offset="1" stop-color="{SANGUE}" stop-opacity="0"/></linearGradient></defs>'
  f'<rect y="11" width="800" height="2" fill="url(#g)"/><rect x="394" y="6" width="12" height="12" fill="{SANGUE}" transform="rotate(45 400 12)">'
  f'<animate attributeName="opacity" values=".4;1;.4" dur="3s" repeatCount="indefinite"/></rect>', ""))

# Rodapé
svg(int(len(RODAPE) * 14) + 8, 56, ("assets/rodape.svg", tx(RODAPE, 0, 36, 28, LUA).replace("</text>", '<animate attributeName="opacity" values="1;1;.25;1;.6;1" keyTimes="0;.8;.84;.88;.92;1" dur="7s" repeatCount="indefinite"/></text>'), RODAPE))
print("ok")
