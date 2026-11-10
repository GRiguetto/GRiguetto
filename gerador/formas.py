"""Formas reutilizáveis: ondas, tentáculo articulado, farol, estrelas e a sincronia
entre o feixe do farol e as mensagens."""
import math

from .svg import n


def poligono(pts):
    return ("M" + n(pts[0][0]) + " " + n(pts[0][1])
            + "".join(f"L{n(x)} {n(y)}" for x, y in pts[1:]) + "Z")


# --- ondas -------------------------------------------------------------------
def onda(lam, amp, y_crista, largura, fundo, x_ini=0):
    """Onda sem emenda: começa em x_ini - 2*lam e cobre largura + 4*lam.

    Um primeiro `q` seguido de vários `t` faz crista e vale se alternarem. O padrão se
    repete a cada `lam`, então animar translateX(±lam) em loop não deixa costura.
    """
    x0 = x_ini - 2 * lam
    meias = math.ceil((largura + 4 * lam) / (lam / 2))
    if meias % 2:
        meias += 1
    y = y_crista + amp
    d = f"M{n(x0)} {n(y)}q{n(lam / 4)} {n(-2 * amp)} {n(lam / 2)} 0"
    d += "t" + " ".join([f"{n(lam / 2)} 0"] * (meias - 1))
    d += f"V{n(fundo)}H{n(x0)}z"
    return d


def css_onda(classe, lam, dur, direcao, atraso=0):
    """CSS de uma onda: direcao = -1 anda para a esquerda, +1 para a direita."""
    nome = f"{classe}k"
    return (f"@keyframes {nome}{{to{{transform:translateX({n(direcao * lam)}px)}}}}"
            f".{classe}{{animation:{nome} {dur}s linear {atraso}s infinite}}")


def neblina(cor="#9fb0ad", opacidade=".045"):
    """Seis elipses largas e baixas, em duas cópias lado a lado (período 1200)."""
    base = [(150, 300, 130, 6), (360, 309, 150, 5), (590, 298, 110, 5),
            (760, 312, 150, 6), (990, 303, 140, 5), (1120, 310, 75, 4)]
    el = []
    for desloc in (0, 1200):
        for cx, cy, rx, ry in base:
            el.append(f'<ellipse cx="{cx + desloc}" cy="{cy}" rx="{rx}" ry="{ry}"/>')
    return f'<g class="nv" fill="{cor}" opacity="{opacidade}">' + "".join(el) + "</g>"


# --- tentáculo articulado ------------------------------------------------------
def tentaculo(x0, y0, comp, w0, wmin, ang0, k0, k1, p=4, passos=90):
    """Integra uma linha central e devolve o contorno cortado em três segmentos.

    ang0 em graus (0 = direita, -90 = cima). A cada passo o rumo gira
    (k0 + k1*(p+1)*s**p)/passos: k0 é a curva suave do corpo e k1 o enrolar da ponta.
    Valores negativos curvam para a esquerda.
    """
    ds = comp / passos
    h = math.radians(ang0)
    x, y = x0, y0
    cl = []
    for i in range(passos + 1):
        s = i / passos
        w = (w0 - wmin) * (1 - s) ** 0.85 + wmin
        cl.append((x, y, h, w))
        h += (k0 + k1 * (p + 1) * s ** p) / passos
        x += ds * math.cos(h)
        y += ds * math.sin(h)

    def lado(i, sinal):
        px, py, hh, w = cl[i]
        return (px - sinal * math.sin(hh) * w / 2, py + sinal * math.cos(hh) * w / 2)

    a, b = passos // 3, 2 * passos // 3

    def contorno(i0, i1):
        i1 = min(i1, passos)
        esq = [lado(i, 1) for i in range(i0, i1 + 1)]
        dir_ = [lado(i, -1) for i in range(i1, i0 - 1, -1)]
        return poligono(esq + dir_)

    polys = [contorno(0, a + 2), contorno(a, b + 2), contorno(b, passos)]
    pivos = [(cl[0][0], cl[0][1]), (cl[a][0], cl[a][1]), (cl[b][0], cl[b][1])]
    juntas = [(cl[a][0], cl[a][1], cl[a][3] / 2 + 0.6), (cl[b][0], cl[b][1], cl[b][3] / 2 + 0.6)]
    todos = [lado(i, 1) for i in range(passos + 1)] + [lado(i, -1) for i in range(passos + 1)]
    xs, ys = [p[0] for p in todos], [p[1] for p in todos]
    return {"polys": polys, "pivos": pivos, "juntas": juntas,
            "caixa": (min(xs), min(ys), max(xs), max(ys)), "ponta": (cl[-1][0], cl[-1][1])}


def tentaculo_svg(t, classes=("t1", "t2", "t3"), fill="#010203"):
    """Três <g> aninhados: cada segmento gira em torno da sua própria junta."""
    c1, c2, c3 = classes
    (jx1, jy1, jr1), (jx2, jy2, jr2) = t["juntas"]
    return (f'<g fill="{fill}"><g class="{c1}"><path d="{t["polys"][0]}"/>'
            f'<g class="{c2}"><circle cx="{n(jx1)}" cy="{n(jy1)}" r="{n(jr1)}"/>'
            f'<path d="{t["polys"][1]}"/>'
            f'<g class="{c3}"><circle cx="{n(jx2)}" cy="{n(jy2)}" r="{n(jr2)}"/>'
            f'<path d="{t["polys"][2]}"/></g></g></g></g>')


def css_tentaculo(t, classes, periodos, atrasos, graus=1.5):
    """Cada segmento balança ±graus em torno da junta, com período e atraso próprios."""
    css = f"@keyframes tk{{0%,100%{{transform:rotate({n(-graus)}deg)}}50%{{transform:rotate({n(graus)}deg)}}}}"
    for cls, (ox, oy), per, atr in zip(classes, t["pivos"], periodos, atrasos):
        css += (f".{cls}{{transform-origin:{n(ox)}px {n(oy)}px;"
                f"animation:tk {per}s ease-in-out {atr}s infinite}}")
    return css


# --- farol -------------------------------------------------------------------
def farol(cx, py, s):
    """Silhueta do farol num único path. py = centro da lanterna (pivô do feixe).

    Devolve (d do corpo, (x, y, w, h) do vidro).
    """
    def P(dx, dy):
        return (cx + dx * s, py + dy * s)

    partes = [
        poligono([P(-9.5, 13), P(9.5, 13), P(15, 109), P(-15, 109)]),          # torre
        poligono([P(-16, 10), P(16, 10), P(16, 13), P(-16, 13)]),              # galeria
        poligono([P(-8, -10), P(8, -10), P(8, 10), P(-8, 10)]),                # sala da lanterna
        poligono([P(-10, -10), P(0, -26), P(10, -10)]),                        # capuz pontudo
        poligono([P(-0.7, -34), P(0.7, -34), P(0.7, -26), P(-0.7, -26)]),      # pináculo
    ]
    gx, gy = P(-5, -7)
    return "".join(partes), (gx, gy, 10 * s, 14 * s)


_ROCHA = [(-98, 30), (-88, 21), (-74, 17), (-60, 14), (-46, 11), (-32, 7), (-20, 3), (-6, 0),
          (8, 1), (21, 4), (32, 5), (44, 9), (55, 13), (66, 16), (78, 21), (90, 25), (98, 30),
          (98, 44), (-98, 44)]


def rocha(cx, y_topo, s):
    return poligono([(cx + dx * s, y_topo + dy * s) for dx, dy in _ROCHA])


# --- estrelas ----------------------------------------------------------------
def estrelas(rng, qtd, x_max, y_max, evitar, margem=14, raio=(0.7, 1.4), op=(0.25, 0.6)):
    """Estrelas determinísticas (rng semeado) fora das caixas de `evitar`."""
    saida = []
    tentativas = 0
    while len(saida) < qtd and tentativas < 5000:
        tentativas += 1
        x, y = rng.uniform(8, x_max - 8), rng.uniform(6, y_max)
        if any(x0 - margem <= x <= x1 + margem and y0 - margem <= y <= y1 + margem
               for x0, y0, x1, y1 in evitar):
            continue
        if any(math.hypot(x - sx, y - sy) < 40 for sx, sy, _, _ in saida):
            continue
        saida.append((round(x, 1), round(y, 1), round(rng.uniform(*raio), 1), round(rng.uniform(*op), 2)))
    return saida


def estrelas_svg(lista, classes, cor="#8a979c"):
    """Divide as estrelas em grupos que piscam em ritmos diferentes."""
    grupos = [[] for _ in classes]
    for i, (x, y, r, o) in enumerate(lista):
        grupos[i % len(classes)].append(
            f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(r)}" opacity="{o:g}"/>')
    return "".join(f'<g class="{c}" fill="{cor}">' + "".join(g) + "</g>"
                   for c, g in zip(classes, grupos))


# --- feixe e mensagens em sincronia -------------------------------------------
def facilita(p):
    """O ease-in-out do CSS, cubic-bezier(.42, 0, .58, 1): tempo p (0..1) -> progresso."""
    if p <= 0:
        return 0.0
    if p >= 1:
        return 1.0
    lo, hi = 0.0, 1.0
    for _ in range(60):
        u = (lo + hi) / 2
        x = 3 * (1 - u) ** 2 * u * 0.42 + 3 * (1 - u) * u * u * 0.58 + u ** 3
        if x < p:
            lo = u
        else:
            hi = u
    u = (lo + hi) / 2
    return 3 * (1 - u) * u * u + u ** 3


def inverte_facilita(f):
    """Tempo p em que o ease-in-out chega ao progresso f (bissecção)."""
    lo, hi = 0.0, 1.0
    for _ in range(60):
        p = (lo + hi) / 2
        if facilita(p) < f:
            lo = p
        else:
            hi = p
    return (lo + hi) / 2


def angulo_do_ponto(px, py, x, y):
    """Direção (graus, positivo = para cima) do ponto (x, y) vista do pivô."""
    return math.degrees(math.atan2(py - y, px - x))


def chaves_mensagem(rumo, th_min, th_max, periodo, pico=0.30, subida=0.5, descida=3.0):
    """Keyframes de opacidade de uma mensagem: acende quando o feixe cruza o `rumo`.

    O feixe passa na subida em t1 = p*T/2 e na descida em t2 = T/2 + q*T/2, com p e q
    achados invertendo o ease-in-out. Em cada passagem a opacidade sobe ao pico em 0,5 s
    e some em ~3 s. Devolve ([(pct, opacidade)], t1, t2).
    """
    f = (rumo - th_min) / (th_max - th_min)
    f = min(max(f, 0.08), 0.92)
    meio = periodo / 2
    t1 = inverte_facilita(f) * meio
    t2 = meio + inverte_facilita(1 - f) * meio

    def tenda(tau):
        g = 0.0
        for t in (t1, t2):
            for k in (-1, 0, 1):
                d = tau - (t + k * periodo)
                if -subida <= d <= 0:
                    v = pico * (1 + d / subida)
                elif 0 < d <= descida:
                    v = pico * (1 - d / descida)
                else:
                    v = 0.0
                g = max(g, v)
        return g

    quebras = {0.0, float(periodo)}
    for t in (t1, t2):
        for k in (-1, 0, 1):
            for d in (-subida, 0, descida):
                tt = t + k * periodo + d
                if 0 < tt < periodo:
                    quebras.add(round(tt, 4))
    quebras = sorted(quebras)
    pontos = []

    def refina(a, b, prof):
        if prof > 6:
            return
        m = (a + b) / 2
        if abs(tenda(m) - (tenda(a) + tenda(b)) / 2) > 0.002:
            refina(a, m, prof + 1)
            pontos.append(m)
            refina(m, b, prof + 1)

    for a, b in zip(quebras, quebras[1:]):
        pontos.append(a)
        refina(a, b, 0)
    pontos.append(float(periodo))
    return [(round(100 * p / periodo, 3), round(tenda(p), 3)) for p in pontos], t1, t2


def css_mensagem(classe, chaves, periodo):
    kf = "".join(f"{p:g}%{{opacity:{v:g}}}" for p, v in chaves)
    return (f"@keyframes {classe}k{{{kf}}}"
            f".{classe}{{animation:{classe}k {periodo}s linear infinite}}")
