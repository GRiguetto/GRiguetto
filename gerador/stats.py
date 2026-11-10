"""Registros: busca os números no GitHub (GraphQL) e desenha o painel registros.svg."""
import json
import random
import statistics
import urllib.error
import urllib.request
from datetime import date, datetime, timedelta, timezone

from .svg import Svg, n

NUMERO = "#aeb9b4"
CHUMBO = "#55606a"
RISCADO = "#3a424a"
NIVEIS = ["#0c1218", "#16241b", "#22351f", "#33492b", "#4d6b3f"]
MESES = ["jan", "fev", "mar", "abr", "mai", "jun", "jul", "ago", "set", "out", "nov", "dez"]

CONSULTA = """
query($login:String!){
  user(login:$login){
    repositories(ownerAffiliations:OWNER, isFork:false, first:100){
      totalCount
      nodes{ languages(first:8, orderBy:{field:SIZE, direction:DESC}){ edges{ size node{ name } } } }
    }
    contributionsCollection{
      totalCommitContributions
      totalPullRequestContributions
      contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount weekday } } }
    }
  }
}
"""


# --- datas e formatação -----------------------------------------------------------
def hoje_sp():
    """Data de hoje no fuso America/Sao_Paulo."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("America/Sao_Paulo")).date()
    except Exception:
        return (datetime.now(timezone.utc) - timedelta(hours=3)).date()


def milhar(v):
    """1041 -> '1.041'"""
    return f"{int(v):,}".replace(",", ".")


def data_br(d):
    return d.strftime("%d/%m/%Y")


def dia_da_semana(d):
    """0 = domingo ... 6 = sábado"""
    return (d.weekday() + 1) % 7


# --- dados -----------------------------------------------------------------------------
def dados_exemplo():
    """Amostra determinística (não depende da data de hoje): o resultado é sempre o mesmo."""
    fim = date(2026, 11, 9)
    rng = random.Random(237)
    dom_fim = fim - timedelta(days=dia_da_semana(fim))
    d = dom_fim - timedelta(weeks=52)
    dias = []
    while d <= fim:
        wd = dia_da_semana(d)
        semana = (d - (dom_fim - timedelta(weeks=52))).days // 7
        if 17 <= semana <= 19:                      # umas férias
            c = 0
        elif rng.random() < (0.8 if 1 <= wd <= 5 else 0.28):
            c = 1 + int(rng.random() ** 2.2 * 14)
        else:
            c = 0
        if (fim - d).days <= 6:                      # sequência atual garantida
            c = max(c, 1 + rng.randint(0, 3))
        dias.append((d, c))
        d += timedelta(days=1)
    total = sum(c for _, c in dias)
    return {
        "exemplo": True, "data": fim, "dias": dias,
        "contribuicoes": total, "commits": round(total * 0.74), "prs": round(total * 0.05),
        "repos": 14,
        "linguagens": [("JavaScript", 38.0), ("Java", 26.0), ("PHP", 19.0), ("HTML", 11.0)],
    }


def buscar_dados(usuario, token):
    """Pergunta tudo ao GitHub. Qualquer erro vira exceção (nada de dados falsos no lugar)."""
    corpo = json.dumps({"query": CONSULTA, "variables": {"login": usuario}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql", data=corpo,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json",
                 "User-Agent": "readme-silhuetas"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            resp = json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"GitHub respondeu HTTP {e.code}: {e.read()[:300]!r}") from e
    if resp.get("errors") or not (resp.get("data") or {}).get("user"):
        raise RuntimeError(f"A API devolveu erro: {json.dumps(resp.get('errors') or resp)[:400]}")
    u = resp["data"]["user"]
    cc = u["contributionsCollection"]
    cal = cc["contributionCalendar"]
    dias = []
    for sem in cal["weeks"]:
        for dd in sem["contributionDays"]:
            dias.append((date.fromisoformat(dd["date"]), dd["contributionCount"]))
    dias.sort()
    bytes_por_lang = {}
    for repo in u["repositories"]["nodes"]:
        for e in repo["languages"]["edges"]:
            nome = e["node"]["name"]
            bytes_por_lang[nome] = bytes_por_lang.get(nome, 0) + e["size"]
    total_bytes = sum(bytes_por_lang.values()) or 1
    top = sorted(bytes_por_lang.items(), key=lambda kv: -kv[1])[:4]
    return {
        "exemplo": False, "data": hoje_sp(), "dias": dias,
        "contribuicoes": cal["totalContributions"],
        "commits": cc["totalCommitContributions"], "prs": cc["totalPullRequestContributions"],
        "repos": u["repositories"]["totalCount"],
        "linguagens": [(nm, 100.0 * b / total_bytes) for nm, b in top],
    }


# --- contas ------------------------------------------------------------------------------------
def niveis(dias):
    """Nível 0 para zero; 1 a 4 pelos quartis dos dias com contribuição."""
    nao_zero = sorted(c for _, c in dias if c > 0)
    if len(nao_zero) >= 2:
        q1, q2, q3 = statistics.quantiles(nao_zero, n=4, method="inclusive")
    else:
        q1 = q2 = q3 = nao_zero[0] if nao_zero else 0
    saida = {}
    for d, c in dias:
        if c == 0:
            saida[d] = 0
        elif c <= q1:
            saida[d] = 1
        elif c <= q2:
            saida[d] = 2
        elif c <= q3:
            saida[d] = 3
        else:
            saida[d] = 4
    return saida


def sequencias(dias, hoje):
    """(sequência atual, maior sequência). A atual termina hoje, ou ontem se hoje ainda é zero."""
    por_data = dict(dias)
    d = hoje if hoje in por_data else max(por_data)
    if por_data.get(d, 0) == 0:
        d -= timedelta(days=1)
    atual = 0
    while por_data.get(d, 0) > 0:
        atual += 1
        d -= timedelta(days=1)
    recorde = corrente = 0
    anterior = None
    for dia in sorted(por_data):
        if por_data[dia] > 0:
            corrente = corrente + 1 if anterior and (dia - anterior).days == 1 else 1
            recorde = max(recorde, corrente)
            anterior = dia
        else:
            corrente = 0
            anterior = None
    return atual, recorde


def colunas(dias):
    """53 colunas de semana (domingo no topo). Cada coluna: {linha: data}."""
    cols = {}
    for d, _ in dias:
        dom = d - timedelta(days=dia_da_semana(d))
        cols.setdefault(dom, {})[dia_da_semana(d)] = d
    domingos = sorted(cols)[-53:]
    return [cols[dm] for dm in domingos]


def _celula(x, y, c, r=3):
    """Quadrado de cantos arredondados (raio r) como subpath; cantos em curva quadrática,
    que a 3 px é indistinguível de um arco e custa bem menos bytes."""
    i = n(c - 2 * r)
    return (f"M{n(x + r)} {n(y)}h{i}q{r} 0 {r} {r}v{i}q0 {r}-{r} {r}"
            f"h-{i}q-{r} 0-{r}-{r}v-{i}q0-{r} {r}-{r}z")


def plural(v, singular, plural_):
    return singular if v == 1 else plural_


# --- desenho -------------------------------------------------------------------------------------
def registros(dados, F):
    pir, fell, mono = F["pirata"], F["fell"], F["mono"]
    dias = dados["dias"]
    atual, recorde = sequencias(dias, dados["data"])
    lv = niveis(dias)
    cols = colunas(dias)
    cont = dados["contribuicoes"]

    langs = ", ".join(f"{nm} {round(p)}%" for nm, p in dados["linguagens"])
    rotulo = (f"Registros do GitHub: {milhar(cont)} contribuições no último ano, {milhar(dados['commits'])} "
              f"commits, {milhar(dados['prs'])} pull requests, {milhar(dados['repos'])} repositórios. "
              f"Linguagens principais: {langs}. Sequência atual de {atual} {plural(atual, 'dia', 'dias')}; "
              f"recorde de {recorde} {plural(recorde, 'dia', 'dias')}."
              + (" Dados de exemplo." if dados["exemplo"] else ""))
    s = Svg(1200, 466, rotulo, "Registros")
    s.corpo.append('<rect x=".5" y=".5" width="1199" height="465" rx="14" fill="#05080c" stroke="#141a1f"/>')

    # coluna 1: números
    linhas = [("Contribuições (ano)", cont), ("Commits", dados["commits"]),
              ("Pull requests", dados["prs"]), ("Repositórios", dados["repos"])]
    bases = (84, 128, 172, 216)
    for (rot, val), y in zip(linhas, bases):
        s.corpo.append(s.texto(fell, rot, 22, 60, y, CHUMBO))
        s.corpo.append(s.texto(pir, milhar(val), 38, 400, y, NUMERO, ancora="end"))
        s.corpo.append(f'<path d="M60 {y + 14}H400" stroke="#141a1f" fill="none"/>')

    # coluna 2: as quatro linguagens com mais bytes
    for (nome, pct), y in zip(dados["linguagens"], bases):
        s.corpo.append(s.texto(fell, nome, 22, 470, y, CHUMBO))
        largura = max(2.0, 160 * pct / 100) if pct > 0 else 0
        s.corpo.append(f'<rect x="600" y="{y - 10}" width="160" height="6" rx="3" fill="#0f161b"/>')
        s.corpo.append(f'<rect x="600" y="{y - 10}" width="{n(largura)}" height="6" rx="3" fill="#3a4d30"/>')
        s.corpo.append(s.texto(mono, f"{round(pct)}%", 17, 830, y, CHUMBO, ancora="end"))

    # coluna 3: sequência
    s.corpo.append(s.texto(pir, str(atual), 110, 1040, 170, NUMERO, ancora="middle"))
    s.corpo.append(s.texto(fell, plural(atual, "dia seguido", "dias seguidos"), 22, 1040, 206, CHUMBO,
                           ancora="middle"))
    s.corpo.append(s.texto(mono, f"recorde: {recorde} {plural(recorde, 'dia', 'dias')}", 18, 1040, 240,
                           RISCADO, ancora="middle"))

    # mapa de calor: 53 colunas x 7 linhas
    x0, y0 = 60, 268
    passo = 1080 / 53
    cel = passo - 5
    todas = []   # (x, y, nível, coluna)
    for j, col in enumerate(cols):
        for linha, d in col.items():
            todas.append((x0 + j * passo, y0 + linha * passo, lv[d], j))
    candidatas = sorted((t for t in todas if t[2] >= 2), key=lambda t: (t[3], t[1]))
    rng = random.Random(4)
    escolhidas = []
    for t in rng.sample(candidatas, len(candidatas)):
        if all(abs(t[3] - e[3]) >= 8 for e in escolhidas):
            escolhidas.append(t)
        if len(escolhidas) == 4:
            break
    chave_resp = {(round(t[0], 3), round(t[1], 3)) for t in escolhidas}
    for nivel in range(5):
        d = "".join(_celula(x, y, cel) for x, y, lvl, _ in todas
                    if lvl == nivel and (round(x, 3), round(y, 3)) not in chave_resp)
        if d:
            s.corpo.append(f'<path fill="{NIVEIS[nivel]}" d="{d}"/>')
    periodos = (7, 8.5, 10, 11)
    for i, (x, y, lvl, _) in enumerate(sorted(escolhidas, key=lambda t: t[3])):
        s.corpo.append(f'<rect class="b{i}" x="{n(x)}" y="{n(y)}" width="{n(cel)}" height="{n(cel)}" rx="3" '
                       f'fill="{NIVEIS[lvl]}"/>')
        s.css.append(f".b{i}{{animation:brk {periodos[i]}s ease-in-out -{i * 2.3:g}s infinite}}")
    s.css.append("@keyframes brk{0%,100%{opacity:1}50%{opacity:.55}}")

    # nomes dos meses sob a grade
    marcas = []
    for j, col in enumerate(cols):
        primeiro = col[min(col)]
        if j == 0 or primeiro.month != cols[j - 1][min(cols[j - 1])].month:
            marcas.append((j, primeiro.month))
    if len(marcas) > 1 and marcas[1][0] - marcas[0][0] < 3:
        marcas.pop(0)
    for j, mes in marcas:
        s.corpo.append(s.texto(mono, MESES[mes - 1], 15, x0 + j * passo, 432, RISCADO))

    # legenda e data
    xl = 60
    s.corpo.append(s.texto(mono, "menos", 15, xl, 454, RISCADO))
    xl += mono.largura("menos", 15) + 10
    for i in range(5):
        s.corpo.append(f'<rect x="{n(xl)}" y="443" width="11" height="11" rx="2" fill="{NIVEIS[i]}"/>')
        xl += 15
    s.corpo.append(s.texto(mono, "mais", 15, xl + 3, 454, RISCADO))
    rodape = ("dados de exemplo, o Action troca pelos seus" if dados["exemplo"]
              else f"atualizado em {data_br(dados['data'])}")
    s.corpo.append(s.texto(fell, rodape, 20, 1140, 454, RISCADO, ancora="end"))
    return s.render()
