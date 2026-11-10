# -*- coding: utf-8 -*-
# Seu usuário do GitHub (o Action usa o dono do repositório; isto é só o plano B).
USUARIO = "GRiguetto"

# Banner
NOME = "Gabriel"
PAPEL = "Desenvolvedor web, front-end em formação"

# As três mensagens que o feixe do farol revela: (texto, x, y).
# x e y são a posição do começo do texto (y = linha de base), na grade de 1200 px do banner.
# O gerador avisa se alguma ficar fora do alcance do feixe ou em cima do nome.
MENSAGENS = [
    ("Ph'nglui mglw'nafh ", 72, 56),
    ("Cthulhu R'lyeh ", 640, 96),
    ("wgah'nagl fhtagn", 110, 372),
]

# Frase do rodapé
RODAPE_FRASE = "Ph'nglui mglw'nafh Cthulhu R'lyeh wgah'nagl fhtagn"

# As três janelas de "Paisagens": título e tecnologias de cada uma.
# "cena" só entra no texto alternativo (leitores de tela).
PAISAGENS = [
    {"titulo": "Front-end", "tecnologias": "HTML, CSS, JavaScript, Bootstrap", "cena": "A casa"},
    {"titulo": "Back-end", "tecnologias": "Java, Spring Boot, PHP", "cena": "O cais"},
    {"titulo": "Dados e automação", "tecnologias": "MySQL, SQL Server, Planilhas, Apps Script",
     "cena": "O poço e o moinho"},
]

# Os cinco projetos (as faixas). "status" é opcional: deixe "" se não houver.
PROJETOS = [
    {"titulo": "ROOM 237", "ano": "2026", "status": ""},
    {"titulo": "Controle de Plantões", "ano": "2026", "status": ""},
    {"titulo": "Movimentação de Servidores", "ano": "2026", "status": ""},
    {"titulo": "Afinador de Violão Acessível", "ano": "2026", "status": "em andamento"},
    {"titulo": "AR Ecológico", "ano": "2026", "status": ""},
]

# Legenda de cada botão de contato
CONTATO = {"email": "escreva", "linkedin": "conecte"}
