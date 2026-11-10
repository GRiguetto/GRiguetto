#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Gera todos os SVGs do README em assets/.

Uso:
    python3 gerar_assets.py            gera tudo (registros.svg só é refeito se houver token)
    python3 gerar_assets.py --exemplo  força o registros.svg de exemplo

Só precisa de `pip install fonttools`. O resultado é determinístico: rodar de novo
reproduz exatamente os mesmos arquivos (o registros.svg só muda quando os números mudam).
"""
import os
import sys

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)

import config  # noqa: E402
from gerador import cenas, fontes, paineis, stats  # noqa: E402

ASSETS = os.path.join(AQUI, "assets")

TITULOS = [("sobre", "Sobre"), ("paisagens", "Paisagens"), ("projetos", "Projetos"),
           ("registros", "Registros"), ("contato", "Contato")]


def gravar(nome, conteudo):
    with open(os.path.join(ASSETS, nome), "w", encoding="utf-8", newline="\n") as f:
        f.write(conteudo)
    print(f"  {nome:34s}{len(conteudo.encode('utf-8')) / 1024:6.1f} KB")


def gerar_estaticos(F):
    gravar("banner.svg", cenas.banner(config, F))
    gravar("paisagens.svg", cenas.paisagens(config, F))
    for i, p in enumerate(config.PROJETOS, start=1):
        gravar(f"projeto-{i}.svg", paineis.projeto(p, F))
    gravar("btn-email.svg", paineis.botao("E-mail", config.CONTATO["email"], F))
    gravar("btn-linkedin.svg", paineis.botao("LinkedIn", config.CONTATO["linkedin"], F))
    gravar("rodape.svg", cenas.rodape(config, F))
    for chave, texto in TITULOS:
        gravar(f"h-{chave}.svg", paineis.titulo(texto, F, claro=False))
        gravar(f"h-{chave}-tema-claro.svg", paineis.titulo(texto, F, claro=True))


def gerar_registros(F, forcar_exemplo):
    destino = os.path.join(ASSETS, "registros.svg")
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    usuario = os.environ.get("GITHUB_USER") or config.USUARIO
    if forcar_exemplo:
        gravar("registros.svg", stats.registros(stats.dados_exemplo(), F))
    elif token:
        try:
            dados = stats.buscar_dados(usuario, token)
        except Exception as e:  # com token, erro NUNCA vira dado de exemplo
            print(f"ERRO ao buscar os dados de {usuario}: {e}")
            print("O registros.svg não foi alterado.")
            sys.exit(1)
        gravar("registros.svg", stats.registros(dados, F))
    elif os.path.exists(destino):
        print("  registros.svg                  mantido (sem token, nada a atualizar)")
    else:
        gravar("registros.svg", stats.registros(stats.dados_exemplo(), F))


def main():
    os.makedirs(ASSETS, exist_ok=True)
    F = fontes.carregar(os.path.join(AQUI, "fontes"))
    print("Gerando assets...")
    gerar_estaticos(F)
    gerar_registros(F, "--exemplo" in sys.argv)
    print("Pronto.")


if __name__ == "__main__":
    main()
