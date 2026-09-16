# -*- coding: utf-8 -*-
"""
gerar_dados.py
================

Gera os datasets sintéticos das duas questões de forma REPRODUTÍVEL:
usando `random.seed(SEED)`, onde SEED = número do grupo (ver README).

Uso:
    python gerar_dados.py --seed 1

Saídas:
    data/problema1_pontos.csv
    data/problema1_arestas.csv
    data/problema2.csv
"""

from __future__ import annotations
import argparse
import csv
import random
import math
import os

SAIDA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


# ---------------------------------------------------------------------------
# QUESTÃO 1 — pontos + arestas do grafo
# ---------------------------------------------------------------------------

def gerar_problema1(seed: int, n_pontos: int = 20, n_arestas: int = 40):
    random.seed(seed)

    pontos = []
    # id 0 = centro de distribuição
    pontos.append({
        "id": 0, "nome": "Centro de Distribuicao", "tipo": "centro",
        "x": 0, "y": 0, "pessoas_afetadas": 0, "prioridade": 0,
        "demanda": 0, "beneficio": 0,
    })

    for i in range(1, n_pontos + 1):
        ang = random.uniform(0, 2 * math.pi)
        raio = random.uniform(5, 60)
        x = round(raio * math.cos(ang), 2)
        y = round(raio * math.sin(ang), 2)
        pontos.append({
            "id": i,
            "nome": f"Ponto_{i:02d}",
            "tipo": "atendimento",
            "x": x,
            "y": y,
            "pessoas_afetadas": random.randint(20, 800),
            "prioridade": random.randint(1, 5),
            "demanda": random.randint(2, 12),
            "beneficio": random.randint(10, 100),
        })

    # arestas: garante conectividade básica com uma árvore geradora aleatória
    # e depois adiciona arestas extras até atingir n_arestas, sem tornar o
    # grafo completo (o problema exige um grafo NÃO completamente conectado).
    ids = [p["id"] for p in pontos]
    random.shuffle(ids)
    arestas = []
    conectados = {ids[0]}
    restantes = ids[1:]
    for v in restantes:
        u = random.choice(list(conectados))
        peso = round(dist(pontos, u, v), 2)
        arestas.append((u, v, peso))
        conectados.add(v)

    tentativas = 0
    existentes = {frozenset((u, v)) for u, v, _ in arestas}
    while len(arestas) < n_arestas and tentativas < n_arestas * 20:
        tentativas += 1
        u, v = random.sample(ids, 2)
        chave = frozenset((u, v))
        if chave in existentes:
            continue
        existentes.add(chave)
        peso = round(dist(pontos, u, v), 2)
        arestas.append((u, v, peso))

    # marca ~15% das vias como indisponíveis (bloqueadas por enchente/deslizamento)
    arestas_final = []
    for (u, v, peso) in arestas:
        disponivel = random.random() > 0.15
        arestas_final.append((u, v, peso, disponivel))

    return pontos, arestas_final


def dist(pontos, u, v):
    pu = next(p for p in pontos if p["id"] == u)
    pv = next(p for p in pontos if p["id"] == v)
    return math.hypot(pu["x"] - pv["x"], pu["y"] - pv["y"])


def salvar_problema1(pontos, arestas, seed: int):
    os.makedirs(SAIDA_DIR, exist_ok=True)
    caminho_pontos = os.path.join(SAIDA_DIR, "problema1_pontos.csv")
    caminho_arestas = os.path.join(SAIDA_DIR, "problema1_arestas.csv")

    with open(caminho_pontos, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(pontos[0].keys()))
        w.writeheader()
        w.writerows(pontos)

    with open(caminho_arestas, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["origem", "destino", "peso", "disponivel"])
        for u, v, peso, disponivel in arestas:
            w.writerow([u, v, peso, disponivel])

    print(f"[Q1] seed={seed}: {len(pontos)} pontos, {len(arestas)} arestas -> {caminho_pontos}, {caminho_arestas}")


# ---------------------------------------------------------------------------
# QUESTÃO 2 — série de consumo de energia
# ---------------------------------------------------------------------------

def gerar_problema2(seed: int, n_horas: int = 220, regioes=None):
    random.seed(seed + 1000)  # seed derivada para não repetir os mesmos números da Q1
    if regioes is None:
        regioes = ["Norte", "Nordeste", "Centro-Oeste", "Sudeste", "Sul"]

    linhas = []
    # perfis base por região, para gerar séries plausíveis (não é distribuição real)
    perfil_base = {r: random.uniform(200, 600) for r in regioes}
    capacidade_regiao = {r: perfil_base[r] * random.uniform(1.3, 1.8) for r in regioes}
    prioridade_regiao = {r: random.randint(1, 5) for r in regioes}

    for t in range(n_horas):
        # sazonalidade diária simples (pico por volta das 19h)
        hora_do_dia = t % 24
        fator_hora = 1 + 0.5 * math.sin((hora_do_dia - 6) / 24 * 2 * math.pi)
        for r in regioes:
            ruido = random.uniform(0.85, 1.2)
            # eventos raros de pico (ex.: onda de calor) elevam bastante o consumo
            evento = 1.6 if random.random() < 0.03 else 1.0
            consumo = round(perfil_base[r] * fator_hora * ruido * evento, 2)
            custo = round(random.uniform(0.4, 1.2) * (1.3 if evento > 1 else 1.0), 3)
            linhas.append({
                "timestamp": t,
                "regiao": r,
                "consumo": consumo,
                "capacidade_disponivel": round(capacidade_regiao[r], 2),
                "prioridade": prioridade_regiao[r],
                "custo": custo,
            })

    return linhas


def salvar_problema2(linhas, seed: int):
    os.makedirs(SAIDA_DIR, exist_ok=True)
    caminho = os.path.join(SAIDA_DIR, "problema2.csv")
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    print(f"[Q2] seed={seed}: {len(linhas)} observações -> {caminho}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=1, help="SEED = numero_do_grupo")
    args = parser.parse_args()

    pontos, arestas = gerar_problema1(args.seed)
    salvar_problema1(pontos, arestas, args.seed)

    linhas = gerar_problema2(args.seed)
    salvar_problema2(linhas, args.seed)
