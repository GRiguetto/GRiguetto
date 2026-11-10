"""Peças pequenas: faixas dos projetos, botões de contato e títulos das seções."""
import math

from .svg import Svg

PALE_NOME = "#b9c4bf"
NUMERO = "#aeb9b4"
CHUMBO = "#55606a"


def projeto(p, F):
    """Faixa de 1200 x 64 usada como <summary>. Sem animação."""
    pir, fell = F["pirata"], F["fell"]
    status = p.get("status") or ""
    rotulo = f'Projeto {p["titulo"]}, {p["ano"]}' + (f", {status}" if status else "")
    s = Svg(1200, 64, rotulo)
    s.corpo.append('<rect x=".5" y=".5" width="1199" height="63" rx="8" fill="#06090d" stroke="#1b2126"/>')
    s.corpo.append(s.texto(pir, p["titulo"], 34, 28, 43, PALE_NOME))
    s.corpo.append(s.texto(fell, p["ano"], 22, 1172, 40, CHUMBO, ancora="end"))
    if status:
        x = 1172 - fell.largura(p["ano"], 22) - 20
        s.corpo.append(s.texto(fell, status, 22, x, 40, CHUMBO, ancora="end"))
    return s.render()


def botao(palavra, legenda, F):
    """Botão de contato 560 x 76: palavra à esquerda, legenda à direita, borda que pulsa."""
    pir, fell = F["pirata"], F["fell"]
    s = Svg(560, 76, f"Botão {palavra}: {legenda}")
    s.corpo.append('<rect width="560" height="76" rx="8" fill="#06090d"/>')
    s.corpo.append('<rect class="bd" x=".5" y=".5" width="559" height="75" rx="8" fill="none" '
                   'stroke="#2a3138" opacity=".7"/>')
    s.corpo.append(s.texto(pir, palavra, 36, 28, 50, NUMERO))
    s.corpo.append(s.texto(fell, legenda, 20, 532, 50, CHUMBO, ancora="end"))
    s.css.append("@keyframes bdk{0%,100%{opacity:.55}50%{opacity:.9}}"
                 ".bd{animation:bdk 12s ease-in-out infinite}")
    return s.render()


def titulo(texto, F, claro=False):
    """Título de seção: só texto, fundo transparente. claro=True usa o texto escuro (tema claro)."""
    pir = F["pirata"]
    larg = math.ceil(pir.largura(texto, 46)) + 8
    s = Svg(larg, 64, texto)
    s.corpo.append(s.texto(pir, texto, 46, 4, 46, "#1b2126" if claro else PALE_NOME))
    return s.render()
