"""Base para montar os SVGs: números curtos, escape e registro de glifos.

Todo texto vira contorno (<path> em <defs> + <use>), porque SVG dentro de <img>
não carrega fontes da web.
"""
from xml.sax.saxutils import escape

NS = "http://www.w3.org/2000/svg"
REDUZIR = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"


def n(v):
    """Número curto: no máximo 1 casa decimal, sem zeros sobrando."""
    s = f"{v:.1f}"
    if s.endswith(".0"):
        s = s[:-2]
    if s in ("-0", ""):
        s = "0"
    if s.startswith("0."):
        s = s[1:]
    elif s.startswith("-0."):
        s = "-" + s[2:]
    return s


def attr(valor):
    return escape(str(valor), {'"': "&quot;"})


class Svg:
    def __init__(self, largura, altura, rotulo, titulo=None):
        self.w, self.h = largura, altura
        self.rotulo = rotulo
        self.titulo = titulo or rotulo
        self.css = []        # trechos de CSS (animações)
        self.defs = []       # gradientes, clipPaths
        self.corpo = []      # elementos desenhados, de trás para frente
        self._glifos = {}    # (fonte, caractere) -> id ou None
        self._def_glifos = []

    # --- texto como contorno -------------------------------------------------
    def _glifo(self, fonte, ch):
        chave = (fonte.nome, ch)
        if chave not in self._glifos:
            d = fonte.caminho(ch)
            if not d:
                self._glifos[chave] = None
            else:
                gid = f"g{len(self._def_glifos)}"
                self._def_glifos.append(f'<path id="{gid}" d="{d}"/>')
                self._glifos[chave] = gid
        return self._glifos[chave]

    def texto(self, fonte, txt, tam, x, y, fill, ancora="start", espaco=0.0, attrs=""):
        """Devolve um <g> com o texto desenhado letra a letra (x, y = linha de base)."""
        k = tam / fonte.upem
        kk = f"{k:.5g}"
        if kk.startswith("0."):
            kk = kk[1:]
        larg = fonte.largura(txt, tam, espaco)
        if ancora == "middle":
            x -= larg / 2
        elif ancora == "end":
            x -= larg
        usos = []
        cx = x
        for ch in txt:
            gid = self._glifo(fonte, ch)
            if gid:
                usos.append(
                    f'<use href="#{gid}" transform="matrix({kk} 0 0 -{kk} {n(cx)} {n(y)})"/>'
                )
            cx += fonte.avanco(ch) * k + espaco
        return f'<g fill="{fill}"{attrs}>' + "".join(usos) + "</g>"

    # --- montagem ------------------------------------------------------------
    def render(self):
        css = REDUZIR + "".join(self.css)
        defs = "".join(self.defs) + "".join(self._def_glifos)
        return (
            f'<svg xmlns="{NS}" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}" role="img" aria-label="{attr(self.rotulo)}">'
            f"<title>{escape(self.titulo)}</title>"
            f"<style>{css}</style>"
            f"<defs>{defs}</defs>"
            f'{"".join(self.corpo)}</svg>'
        )
