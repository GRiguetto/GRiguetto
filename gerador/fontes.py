"""Fontes: lê os .woff, transforma glifos em contornos e mede texto.

A IM Fell English tem contornos muito irregulares (uns 2,7 KB por letra), então ela
passa por simplificação: curvas viram segmentos curtos e o Douglas-Peucker tira os
pontos que não fazem diferença. Pirata One e Courier Prime são limpas e ficam como são.
"""
import math
import os

from fontTools.pens.basePen import BasePen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.ttLib import TTFont


class _PenPoligono(BasePen):
    """Guarda cada contorno como lista de pontos, achatando as curvas em segmentos."""

    def __init__(self, glyph_set, passos=8):
        super().__init__(glyph_set)
        self.contornos = []
        self._atual = None
        self.passos = passos

    def _moveTo(self, pt):
        self._atual = [pt]

    def _lineTo(self, pt):
        self._atual.append(pt)

    def _curveToOne(self, p1, p2, p3):
        p0 = self._getCurrentPoint()
        for i in range(1, self.passos + 1):
            t = i / self.passos
            a, b, c, d = (1 - t) ** 3, 3 * t * (1 - t) ** 2, 3 * t * t * (1 - t), t ** 3
            self._atual.append((
                a * p0[0] + b * p1[0] + c * p2[0] + d * p3[0],
                a * p0[1] + b * p1[1] + c * p2[1] + d * p3[1],
            ))

    def _qCurveToOne(self, p1, p2):
        p0 = self._getCurrentPoint()
        for i in range(1, self.passos + 1):
            t = i / self.passos
            a, b, c = (1 - t) ** 2, 2 * t * (1 - t), t * t
            self._atual.append((
                a * p0[0] + b * p1[0] + c * p2[0],
                a * p0[1] + b * p1[1] + c * p2[1],
            ))

    def _closePath(self):
        if self._atual:
            self.contornos.append(self._atual)
        self._atual = None

    _endPath = _closePath


def _douglas_peucker(pts, tol):
    if len(pts) < 3:
        return pts
    manter = [False] * len(pts)
    manter[0] = manter[-1] = True
    pilha = [(0, len(pts) - 1)]
    while pilha:
        a, b = pilha.pop()
        (ax, ay), (bx, by) = pts[a], pts[b]
        dx, dy = bx - ax, by - ay
        comp = math.hypot(dx, dy)
        dmax, idx = -1.0, None
        for i in range(a + 1, b):
            px, py = pts[i]
            if comp == 0:
                d = math.hypot(px - ax, py - ay)
            else:
                d = abs(dy * (px - ax) - dx * (py - ay)) / comp
            if d > dmax:
                dmax, idx = d, i
        if idx is not None and dmax > tol:
            manter[idx] = True
            pilha.append((a, idx))
            pilha.append((idx, b))
    return [p for p, m in zip(pts, manter) if m]


def _poligono_para_d(pts):
    """Polígono em coordenadas relativas (menor): M x y l dx,dy dx,dy ... z"""
    pts = [(round(x), round(y)) for x, y in pts]
    limpo = [pts[0]]
    for p in pts[1:]:
        if p != limpo[-1]:
            limpo.append(p)
    if len(limpo) > 1 and limpo[0] == limpo[-1]:
        limpo.pop()
    if len(limpo) < 3:
        return ""
    prev = limpo[0]
    passos = []
    for p in limpo[1:]:
        passos.append(f"{p[0] - prev[0]},{p[1] - prev[1]}")
        prev = p
    return f"M{limpo[0][0]} {limpo[0][1]}l" + " ".join(passos) + "z"


class Fonte:
    def __init__(self, nome, caminho, simplificar=False, tolerancia=8):
        self.nome = nome
        self._t = TTFont(caminho)
        self._gs = self._t.getGlyphSet()
        self._cmap = self._t.getBestCmap()
        self.upem = self._t["head"].unitsPerEm
        self.simplificar = simplificar
        self.tolerancia = tolerancia
        self._cache = {}
        self.avisados = set()

    def _glifo(self, ch):
        nome = self._cmap.get(ord(ch))
        if nome is None and ch not in self.avisados:
            self.avisados.add(ch)
            print(f"AVISO: a fonte {self.nome} não tem glifo para {ch!r} (U+{ord(ch):04X})")
        return nome

    def avanco(self, ch):
        nome = self._glifo(ch)
        if nome is None:
            esp = self._cmap.get(32)
            return self._gs[esp].width if esp else self.upem * 0.25
        return self._gs[nome].width

    def largura(self, txt, tam, espaco=0.0):
        k = tam / self.upem
        return sum(self.avanco(c) * k for c in txt) + espaco * max(len(txt) - 1, 0)

    def caminho(self, ch):
        if ch in self._cache:
            return self._cache[ch]
        nome = self._glifo(ch)
        if nome is None:
            d = ""
        elif self.simplificar:
            pen = _PenPoligono(self._gs)
            self._gs[nome].draw(pen)
            partes = []
            for c in pen.contornos:
                if len(c) > 1 and c[0] == c[-1]:
                    c = c[:-1]
                if len(c) < 3:
                    continue
                s = _douglas_peucker(c + [c[0]], self.tolerancia)[:-1]
                partes.append(_poligono_para_d(s))
            d = "".join(partes)
        else:
            pen = SVGPathPen(self._gs, ntos=lambda v: str(round(v)))
            self._gs[nome].draw(pen)
            d = pen.getCommands()
        self._cache[ch] = d
        return d


def carregar(pasta):
    """Carrega as três fontes usadas: pirata, fell (itálico) e mono (Courier Prime)."""
    return {
        "pirata": Fonte("pirata", os.path.join(pasta, "pirata.woff")),
        "fell": Fonte("fell", os.path.join(pasta, "fell-italic.woff"), simplificar=True, tolerancia=8),
        "mono": Fonte("mono", os.path.join(pasta, "typewriter.woff")),
    }
