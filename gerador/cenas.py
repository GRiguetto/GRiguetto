"""Cenas: banner (costa, farol, feixe e tentáculo), rodapé e as três paisagens."""
import math
import random

from .formas import (angulo_do_ponto, chaves_mensagem, css_mensagem, css_onda, css_tentaculo,
                     estrelas, estrelas_svg, farol, neblina, onda, poligono, rocha, tentaculo,
                     tentaculo_svg)
from .svg import Svg, n

PRETO = "#010203"
PALE_NOME = "#b9c4bf"
CHUMBO = "#55606a"


def _gradientes_base(s):
    """Céu e mar (objectBoundingBox: valem para qualquer retângulo)."""
    s.defs.append(
        '<linearGradient id="ceu" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#04070b"/><stop offset=".55" stop-color="#070d14"/>'
        '<stop offset="1" stop-color="#0b161c"/></linearGradient>'
        '<linearGradient id="mar" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#0a161c"/><stop offset=".5" stop-color="#05090c"/>'
        '<stop offset="1" stop-color="#020405"/></linearGradient>')


def _feixe(px, py, comp, meio_angulo, cor_id):
    """Cunha fina apontando para a esquerda, com vértice no pivô."""
    a = math.radians(meio_angulo)
    fx = px - comp * math.cos(a)
    dy = comp * math.sin(a)
    return poligono([(px, py), (fx, py - dy), (fx, py + dy)])


# =============================================================================
# BANNER 1200 x 420
# =============================================================================
BANNER_PIVO = (930, 226)
FEIXE_MIN, FEIXE_MAX, FEIXE_T = -14, 46, 26

# tentáculo do banner: base escondida pela onda da frente, ponta enrolada para o farol
TENT_BANNER = dict(x0=1090, y0=404, comp=400, w0=56, wmin=1.2, ang0=-97, k0=-0.45, k1=-2.3)


def banner(cfg, F):
    pir, fell = F["pirata"], F["fell"]
    px, py = BANNER_PIVO
    papel = cfg.PAPEL
    s = Svg(
        1200, 420,
        f"Banner: costa noturna em silhueta. Um farol sobre uma rocha varre o céu com um feixe "
        f"de luz pálido e revela mensagens quase invisíveis, enquanto um enorme tentáculo se ergue "
        f"do mar. {cfg.NOME}, {papel[0].lower() + papel[1:]}.",
        f"{cfg.NOME}, {papel}")
    _gradientes_base(s)
    s.defs.append(
        '<linearGradient id="nb" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#12222a" stop-opacity="0"/>'
        '<stop offset=".5" stop-color="#12222a" stop-opacity=".35"/>'
        '<stop offset="1" stop-color="#12222a" stop-opacity="0"/></linearGradient>')
    s.defs.append(
        f'<linearGradient id="fz" gradientUnits="userSpaceOnUse" x1="{px}" y1="{py}" x2="{px - 1100}" y2="{py}">'
        '<stop offset="0" stop-color="#cfdad4" stop-opacity=".14"/>'
        '<stop offset="1" stop-color="#cfdad4" stop-opacity="0"/></linearGradient>')

    # --- medidas para evitar sobreposição ------------------------------------
    w_nome = pir.largura(cfg.NOME, 200)
    w_papel = fell.largura(papel, 28)
    caixa_nome = (60, 66, 60 + w_nome, 232)
    caixa_papel = (64, 250, 64 + w_papel, 280)
    caixas_msg = []
    for txt, x, y in cfg.MENSAGENS:
        caixas_msg.append((x, y - 22, x + fell.largura(txt, 28), y + 8))

    tent = tentaculo(**TENT_BANNER)
    cx0, cy0, cx1, cy1 = tent["caixa"]
    caixa_farol = (px - 20, 190, px + 20, 340)

    # avisos de projeto
    def intersecta(a, b):
        return not (a[2] < b[0] or b[2] < a[0] or a[3] < b[1] or b[3] < a[1])
    for i, cx in enumerate(caixas_msg):
        for nome, outra in (("o nome", caixa_nome), ("o papel", caixa_papel),
                            ("o tentáculo", tent["caixa"]), ("o farol", caixa_farol)):
            if intersecta(cx, outra):
                print(f"AVISO: a mensagem {i + 1} encosta em {nome}")

    # --- fundo -----------------------------------------------------------------
    s.corpo.append('<rect width="1200" height="312" fill="url(#ceu)"/>')
    s.corpo.append('<rect y="312" width="1200" height="108" fill="url(#mar)"/>')

    # --- estrelas (3 grupos piscam em 5, 7 e 9 s) ---------------------------------
    rng = random.Random(11)
    evitar = [caixa_nome, caixa_papel, caixa_farol, tent["caixa"]] + caixas_msg
    lista = estrelas(rng, 28, 1200, 260, evitar)
    s.corpo.append(estrelas_svg(lista, ("s1", "s2", "s3")))
    s.css.append("@keyframes tw{50%{opacity:.65}}"
                 ".s1{animation:tw 5s ease-in-out infinite}"
                 ".s2{animation:tw 7s ease-in-out -2s infinite}"
                 ".s3{animation:tw 9s ease-in-out -5s infinite}")

    # --- neblina junto ao horizonte ---------------------------------------------
    s.corpo.append('<rect y="290" width="1200" height="28" fill="url(#nb)"/>')
    s.corpo.append(neblina())
    s.css.append("@keyframes nvk{to{transform:translateX(-1200px)}}"
                 ".nv{animation:nvk 90s linear infinite}")

    # --- onda de trás (W1) --------------------------------------------------------
    s.corpo.append(f'<path class="w1" fill="#07110f" d="{onda(220, 2.5, 318, 1200, 420)}"/>')
    s.css.append(css_onda("w1", 220, 80, -1, -23))

    # --- rocha e farol -------------------------------------------------------------
    s.corpo.append(f'<path fill="{PRETO}" d="{rocha(px, 322, 1)}"/>')
    corpo_farol, (gx, gy, gw, gh) = farol(px, py, 1)
    s.corpo.append(f'<path fill="{PRETO}" d="{corpo_farol}"/>')
    s.corpo.append(f'<rect class="vd" x="{n(gx)}" y="{n(gy)}" width="{n(gw)}" height="{n(gh)}" '
                   f'fill="#b8c4c0" opacity=".45"/>')
    s.css.append("@keyframes vdk{0%,100%{opacity:.35}50%{opacity:.55}}"
                 ".vd{animation:vdk 7s ease-in-out infinite}")

    # --- onda do meio (W2) ----------------------------------------------------------
    s.corpo.append(f'<path class="w2" fill="#040908" d="{onda(340, 4, 346, 1200, 420)}"/>')
    s.css.append(css_onda("w2", 340, 55, 1, -17))

    # --- feixe -----------------------------------------------------------------------
    meio = (FEIXE_MIN + FEIXE_MAX) / 2
    s.corpo.append(f'<path class="fx" fill="url(#fz)" d="{_feixe(px, py, 1100, 3.2, "fz")}"/>')
    s.css.append(
        f"@keyframes fxk{{0%,100%{{transform:rotate({FEIXE_MIN}deg)}}50%{{transform:rotate({FEIXE_MAX}deg)}}}}"
        f".fx{{transform-origin:{px}px {py}px;transform:rotate({n(meio)}deg);"
        f"animation:fxk {FEIXE_T}s ease-in-out infinite}}")

    # --- mensagens: cada uma acende quando o feixe cruza o seu rumo ---------------------
    for i, (txt, x, y) in enumerate(cfg.MENSAGENS, start=1):
        w = fell.largura(txt, 28)
        rumo = angulo_do_ponto(px, py, x + w / 2, y - 8)
        if not (FEIXE_MIN + 3 <= rumo <= FEIXE_MAX - 3):
            print(f"AVISO: a mensagem {i} ({txt!r}) fica a {rumo:.1f}° do farol, quase fora do "
                  f"alcance do feixe ({FEIXE_MIN}° a {FEIXE_MAX}°)")
        chaves, t1, t2 = chaves_mensagem(rumo, FEIXE_MIN, FEIXE_MAX, FEIXE_T)
        s.css.append(css_mensagem(f"m{i}", chaves, FEIXE_T))
        s.corpo.append(s.texto(fell, txt, 28, x, y, "#8fa1a8", attrs=f' class="m{i}" opacity="0"'))

    # --- tentáculo: três segmentos aninhados, ondulação que viaja pela ponta ------------
    s.corpo.append(tentaculo_svg(tent))
    s.css.append(css_tentaculo(tent, ("t1", "t2", "t3"), (13, 15, 17), (-3, -7, -11)))

    # --- onda da frente (W3), esconde a base do tentáculo ----------------------------------
    s.corpo.append(f'<path class="w3" fill="#010202" d="{onda(520, 5.5, 380, 1200, 420)}"/>')
    s.css.append(css_onda("w3", 520, 38, -1, -9))

    # --- nome e papel -------------------------------------------------------------------------
    s.corpo.append(s.texto(pir, cfg.NOME, 200, 60, 228, PALE_NOME, attrs=' class="nome"'))
    s.corpo.append(s.texto(fell, papel, 28, 64, 272, "#6f7c83"))
    s.css.append("@keyframes apk{from{opacity:0}to{opacity:1}}"
                 ".nome{animation:apk 2.4s ease-out both}")
    return s.render()


# =============================================================================
# RODAPÉ 1200 x 220
# =============================================================================
RODAPE_PIVO = (1062, 108)
RODAPE_MIN, RODAPE_MAX, RODAPE_T = -5, 16, 22
TENT_RODAPE = dict(x0=70, y0=198, comp=96, w0=20, wmin=1.2, ang0=-86, k0=0.12, k1=0.9)


def rodape(cfg, F):
    fell = F["fell"]
    px, py = RODAPE_PIVO
    frase = cfg.RODAPE_FRASE
    s = Svg(1200, 220,
            f"Cena de encerramento: um pequeno farol à direita varre o céu com um feixe suave e a ponta "
            f"de um tentáculo desponta do mar à esquerda. Frase: {frase}",
            "Rodapé")
    _gradientes_base(s)
    s.defs.append(
        f'<linearGradient id="fz" gradientUnits="userSpaceOnUse" x1="{px}" y1="{py}" x2="{px - 800}" y2="{py}">'
        '<stop offset="0" stop-color="#cfdad4" stop-opacity=".10"/>'
        '<stop offset="1" stop-color="#cfdad4" stop-opacity="0"/></linearGradient>')

    larg = fell.largura(frase, 34)
    caixa_txt = (600 - larg / 2, 52, 600 + larg / 2, 96)
    tent = tentaculo(**TENT_RODAPE)
    evitar = [caixa_txt, (px - 70, 70, px + 70, 190), tent["caixa"]]

    s.corpo.append('<rect width="1200" height="150" fill="url(#ceu)"/>')
    s.corpo.append('<rect y="150" width="1200" height="70" fill="url(#mar)"/>')
    rng = random.Random(23)
    s.corpo.append(estrelas_svg(estrelas(rng, 12, 1200, 130, evitar, margem=16), ("s1", "s2")))
    s.css.append("@keyframes tw{50%{opacity:.65}}"
                 ".s1{animation:tw 6s ease-in-out infinite}"
                 ".s2{animation:tw 8s ease-in-out -3s infinite}")

    s.corpo.append(f'<path class="w1" fill="#07110f" d="{onda(160, 2, 154, 1200, 220)}"/>')
    s.css.append(css_onda("w1", 160, 70, -1, -19))

    # farol pequeno sobre a rocha
    s.corpo.append(f'<path fill="{PRETO}" d="{rocha(px, 156, 0.5)}"/>')
    corpo, (gx, gy, gw, gh) = farol(px, py, 0.5)
    s.corpo.append(f'<path fill="{PRETO}" d="{corpo}"/>')
    s.corpo.append(f'<rect class="vd" x="{n(gx)}" y="{n(gy)}" width="{n(gw)}" height="{n(gh)}" '
                   f'fill="#b8c4c0" opacity=".45"/>')
    s.css.append("@keyframes vdk{0%,100%{opacity:.35}50%{opacity:.55}}"
                 ".vd{animation:vdk 8s ease-in-out infinite}")

    # ponta de tentáculo à esquerda (a base some atrás da onda)
    s.corpo.append(tentaculo_svg(tent))
    s.css.append(css_tentaculo(tent, ("t1", "t2", "t3"), (14, 14, 14), (0, -4, -9), graus=1.2))

    s.corpo.append(f'<path class="w2" fill="#020405" d="{onda(300, 3.5, 184, 1200, 220)}"/>')
    s.css.append(css_onda("w2", 300, 45, 1, -11))

    # feixe suave (varre um ângulo estreito) — fica atrás do texto
    meio = (RODAPE_MIN + RODAPE_MAX) / 2
    s.corpo.append(f'<path class="fx" fill="url(#fz)" d="{_feixe(px, py, 800, 2.4, "fz")}"/>')
    s.css.append(
        f"@keyframes fxk{{0%,100%{{transform:rotate({RODAPE_MIN}deg)}}50%{{transform:rotate({RODAPE_MAX}deg)}}}}"
        f".fx{{transform-origin:{px}px {py}px;transform:rotate({n(meio)}deg);"
        f"animation:fxk {RODAPE_T}s ease-in-out infinite}}")

    # frase: respira em 9 s e dá um apagão rápido a cada 14 s
    s.corpo.append('<g class="fl">' + s.texto(fell, frase, 34, 600, 84, "#7d8a92", ancora="middle",
                                              attrs=' class="tx" opacity=".5"') + "</g>")
    s.css.append("@keyframes txk{0%,100%{opacity:.35}50%{opacity:.6}}"
                 ".tx{animation:txk 9s ease-in-out infinite}"
                 "@keyframes flk{0%,92%,100%{opacity:1}93.5%{opacity:.3}95%{opacity:1}96.5%{opacity:.55}98%{opacity:1}}"
                 ".fl{animation:flk 14s linear infinite}")
    return s.render()


# =============================================================================
# PAISAGENS 1200 x 400 — três janelas
# =============================================================================
JANELAS_X = (60, 430, 800)
JAN_Y, JAN_W, JAN_H = 40, 340, 236


def _pontos_abs(ox, oy, pts):
    return poligono([(ox + x, oy + y) for x, y in pts])


def _estrelas_fixas(ox, oy, pts):
    c = "".join(f'<circle cx="{n(ox + x)}" cy="{n(oy + y)}" r="{r:g}" opacity="{o:g}"/>' for x, y, r, o in pts)
    return f'<g fill="#8a979c">{c}</g>'


def _cena_casa(s, ox, oy):
    X = lambda v: n(ox + v)
    Y = lambda v: n(oy + v)
    o = [f'<rect x="{X(0)}" y="{Y(0)}" width="{JAN_W}" height="{JAN_H}" fill="url(#ceu)"/>',
         _estrelas_fixas(ox, oy, [(24, 22, 1, .4), (66, 48, .8, .3), (118, 16, 1.2, .5), (176, 38, .9, .35),
                                  (232, 20, 1, .45), (284, 52, .8, .3), (310, 18, 1.1, .5), (205, 68, .8, .25)]),
         f'<rect x="{X(0)}" y="{Y(150)}" width="{JAN_W}" height="86" fill="url(#mar)"/>',
         f'<path class="wa" fill="#07110f" d="{onda(120, 2, oy + 156, JAN_W, oy + JAN_H, x_ini=ox)}"/>',
         # colina de musgo escuro à direita
         f'<path fill="#111b14" d="M{X(190)} {Y(170)}Q{X(245)} {Y(100)} {X(340)} {Y(130)}V{Y(236)}H{X(190)}Z"/>',
         # costa rochosa em primeiro plano
         f'<path fill="{PRETO}" d="{_pontos_abs(ox, oy, [(0, 236), (0, 196), (24, 188), (52, 181), (84, 177), (116, 176), (150, 177), (186, 181), (222, 190), (262, 203), (300, 214), (340, 222), (340, 236)])}"/>',
         # a casa: corpo, telhado de duas águas e chaminé num só path
         f'<path fill="{PRETO}" d="M{X(100)} {Y(178)}V{Y(142)}H{X(156)}V{Y(178)}Z'
         f'M{X(94)} {Y(144)}L{X(128)} {Y(118)}L{X(162)} {Y(144)}Z'
         f'M{X(142)} {Y(111)}H{X(150)}V{Y(133)}H{X(142)}Z"/>',
         f'<rect class="jn" x="{X(124)}" y="{Y(152)}" width="8" height="10" fill="#b8c4c0" opacity=".5"/>']
    for i in (1, 2, 3):
        o.append(f'<ellipse class="f{i}" cx="{X(148)}" cy="{Y(106)}" rx="6" ry="4" fill="#2a3138" opacity="0"/>')
    s.css.append(css_onda("wa", 120, 90, -1, -31))
    s.css.append("@keyframes jnk{0%,100%{opacity:.45}12%{opacity:.6}20%{opacity:.38}34%{opacity:.52}"
                 "47%{opacity:.35}58%{opacity:.6}72%{opacity:.42}86%{opacity:.55}}"
                 ".jn{animation:jnk 6s linear infinite}"
                 "@keyframes fuk{0%{opacity:0;transform:translate(0,0)}15%{opacity:.4}"
                 "100%{opacity:0;transform:translate(16px,-40px)}}"
                 ".f1{animation:fuk 10.5s linear infinite}"
                 ".f2{animation:fuk 10.5s linear -3.5s infinite}"
                 ".f3{animation:fuk 10.5s linear -7s infinite}")
    return "".join(o)


def _cena_cais(s, ox, oy):
    X = lambda v: n(ox + v)
    Y = lambda v: n(oy + v)
    pilares = "".join(f"M{X(2 + 28 * i)} {Y(154)}h2v26h-2z" for i in range(10))
    o = [f'<rect x="{X(0)}" y="{Y(0)}" width="{JAN_W}" height="{JAN_H}" fill="url(#ceu)"/>',
         _estrelas_fixas(ox, oy, [(20, 20, 1, .4), (70, 52, .8, .3), (140, 28, 1.2, .5), (200, 60, .8, .28),
                                  (262, 24, 1, .45), (312, 46, .9, .35)]),
         f'<rect x="{X(0)}" y="{Y(122)}" width="{JAN_W}" height="114" fill="url(#mar)"/>',
         # promontório baixo à esquerda
         f'<path fill="#0c130f" d="M{X(0)} {Y(124)}V{Y(98)}Q{X(40)} {Y(84)} {X(82)} {Y(104)}L{X(132)} {Y(124)}Z"/>',
         f'<path class="wb1" fill="#07110f" d="{onda(110, 2, oy + 130, JAN_W, oy + JAN_H, x_ini=ox)}"/>',
         # o cais: tabuleiro fino, dez estacas, poste com lâmpada
         f'<path fill="{PRETO}" d="M{X(0)} {Y(150)}H{X(258)}V{Y(154)}H{X(0)}Z{pilares}'
         f'M{X(251)} {Y(121)}h2v29h-2z"/>',
         f'<rect class="lp" x="{X(249)}" y="{Y(115)}" width="6" height="6" fill="#b8c4c0" opacity=".45"/>',
         f'<g class="rf" fill="#b8c4c0" opacity=".16"><rect x="{X(246)}" y="{Y(162)}" width="12" height="1.5"/>'
         f'<rect x="{X(247.5)}" y="{Y(170)}" width="9" height="1.5"/>'
         f'<rect x="{X(249)}" y="{Y(179)}" width="6" height="1.5"/></g>',
         f'<path class="wb2" fill="#020405" d="{onda(170, 3, oy + 190, JAN_W, oy + JAN_H, x_ini=ox)}"/>']
    s.css.append(css_onda("wb1", 110, 80, -1, -17))
    s.css.append(css_onda("wb2", 170, 55, 1, -23))
    s.css.append("@keyframes lpk{0%,100%{opacity:.3}50%{opacity:.55}}"
                 ".lp{animation:lpk 8s ease-in-out infinite}"
                 "@keyframes rfk{0%,100%{transform:translateX(-4px)}50%{transform:translateX(4px)}}"
                 ".rf{animation:rfk 6s ease-in-out infinite}")
    return "".join(o)


def _cena_poco(s, ox, oy):
    X = lambda v: n(ox + v)
    Y = lambda v: n(oy + v)
    hx, hy = ox + 258, oy + 84      # cubo do moinho
    bx, by = ox + 89, oy + 149      # viga do poço (pivô da corda)
    o = [f'<rect x="{X(0)}" y="{Y(0)}" width="{JAN_W}" height="{JAN_H}" fill="url(#ceu)"/>',
         _estrelas_fixas(ox, oy, [(22, 24, 1, .4), (78, 50, .8, .3), (132, 18, 1.2, .5), (190, 44, .9, .35),
                                  (240, 20, 1, .45), (306, 36, .9, .3)]),
         # colina distante, que leva o moinho
         f'<path fill="#0c130f" d="M{X(160)} {Y(180)}Q{X(250)} {Y(104)} {X(340)} {Y(138)}V{Y(236)}H{X(160)}Z"/>',
         # torre do moinho + capuz (as pás giram à parte)
         f'<path fill="{PRETO}" d="{_pontos_abs(ox, oy, [(252, 133), (264, 133), (261.5, 86), (254.5, 86)])}'
         f'{_pontos_abs(ox, oy, [(253, 87), (258, 79), (263, 87)])}"/>',
         # colina de musgo que atravessa a cena
         f'<path fill="#111b14" d="M{X(0)} {Y(176)}Q{X(90)} {Y(150)} {X(190)} {Y(172)}T{X(340)} {Y(176)}V{Y(236)}H{X(0)}Z"/>',
         # chão preto do primeiro plano
         f'<path fill="{PRETO}" d="M{X(0)} {Y(236)}V{Y(198)}Q{X(60)} {Y(190)} {X(130)} {Y(196)}T{X(260)} {Y(200)}'
         f'Q{X(300)} {Y(202)} {X(340)} {Y(206)}V{Y(236)}Z"/>',
         # o poço: corpo, aro, dois postos, telhado, manivela
         f'<path fill="{PRETO}" d="M{X(66)} {Y(204)}V{Y(176)}H{X(112)}V{Y(204)}Z'
         f'M{X(63)} {Y(177)}V{Y(172)}H{X(115)}V{Y(177)}Z'
         f'M{X(70)} {Y(173)}V{Y(146)}h2.5V{Y(173)}Z'
         f'M{X(105.5)} {Y(173)}V{Y(146)}h2.5V{Y(173)}Z'
         f'{_pontos_abs(ox, oy, [(62, 148), (89, 134), (116, 148)])}'
         f'M{X(108)} {Y(153)}h9v2h-9zM{X(116)} {Y(153)}h2v10h-2z"/>',
         # moinho: duas hastes cruzadas giram uma volta a cada 60 s
         f'<path class="pa" fill="{PRETO}" d="M{n(hx - 34)} {n(hy - 1.2)}h68v2.4h-68z'
         f'M{n(hx - 1.2)} {n(hy - 34)}h2.4v68h-2.4z"/>',
         # corda e balde balançam ±3° em torno da viga
         f'<g class="bk" fill="{PRETO}"><path d="M{n(bx - 0.5)} {n(by)}h1v15h-1z"/>'
         f'<rect x="{n(bx - 3.5)}" y="{n(by + 15)}" width="7" height="7"/></g>']
    s.css.append("@keyframes pak{to{transform:rotate(360deg)}}"
                 f".pa{{transform-origin:{n(hx)}px {n(hy)}px;animation:pak 60s linear infinite}}"
                 "@keyframes bkk{0%,100%{transform:rotate(-3deg)}50%{transform:rotate(3deg)}}"
                 f".bk{{transform-origin:{n(bx)}px {n(by)}px;animation:bkk 7s ease-in-out infinite}}")
    return "".join(o)


def paisagens(cfg, F):
    pir, fell = F["pirata"], F["fell"]
    desc = "; ".join(f'{p["cena"].lower()} ({p["titulo"]}: {p["tecnologias"]})' for p in cfg.PAISAGENS)
    s = Svg(1200, 400, f"Três paisagens noturnas em silhueta, uma para cada área: {desc}.", "Paisagens")
    _gradientes_base(s)
    s.corpo.append('<rect x=".5" y=".5" width="1199" height="399" rx="14" fill="#05080c" stroke="#141a1f"/>')
    cenas = (_cena_casa, _cena_cais, _cena_poco)
    for i, (ox, cena, p) in enumerate(zip(JANELAS_X, cenas, cfg.PAISAGENS)):
        cid = f"j{i}"
        s.defs.append(f'<clipPath id="{cid}"><rect x="{ox}" y="{JAN_Y}" width="{JAN_W}" height="{JAN_H}" rx="10"/></clipPath>')
        s.corpo.append(f'<g clip-path="url(#{cid})">{cena(s, ox, JAN_Y)}</g>')
        s.corpo.append(f'<rect x="{ox + .5}" y="{JAN_Y + .5}" width="{JAN_W - 1}" height="{JAN_H - 1}" rx="10" '
                       f'fill="none" stroke="#1b2126"/>')
        s.corpo.append(s.texto(pir, p["titulo"], 34, ox, 326, PALE_NOME))
        tam = min(21, 21 * (JAN_W + 8) / fell.largura(p["tecnologias"], 21))
        s.corpo.append(s.texto(fell, p["tecnologias"], tam, ox, 358, CHUMBO))
    return s.render()
