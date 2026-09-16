# -*- coding: utf-8 -*-
"""
analise_q1.py — roda o pipeline completo da Questão 1 e gera:
  figures/questao1/fig1_grafo.png
  figures/questao1/fig2_solucao.png
  figures/questao1/fig3_dp_heatmap.png
e imprime a comparação Greedy x DP (Parte D) + contraexemplo.
"""
from __future__ import annotations
import csv
import os
import matplotlib.pyplot as plt
import numpy as np

from estruturas import Grafo, Ponto
from greedy import atendimento_guloso
from dynamic_programming import selecao_otima_dp, contraexemplo_greedy_vs_dp

BASE = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE, "..", "data")
FIG_DIR = os.path.join(BASE, "..", "figures", "questao1")
CAPACIDADE_VEICULO = 30


def carregar_grafo():
    g = Grafo()
    with open(os.path.join(DATA_DIR, "problema1_pontos.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            g.add_ponto(Ponto(
                id=int(row["id"]), nome=row["nome"], x=float(row["x"]), y=float(row["y"]),
                pessoas_afetadas=int(row["pessoas_afetadas"]), prioridade=int(row["prioridade"]),
                demanda=int(row["demanda"]), beneficio=int(row["beneficio"]),
            ))
    with open(os.path.join(DATA_DIR, "problema1_arestas.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            g.add_aresta(int(row["origem"]), int(row["destino"]), float(row["peso"]),
                         row["disponivel"] == "True")
    return g


def fig1_grafo(g: Grafo):
    os.makedirs(FIG_DIR, exist_ok=True)
    fig, ax = plt.subplots(figsize=(9, 8))
    desenhadas = set()
    for u, viz in g.adj.items():
        for v, w, disp in viz:
            chave = frozenset((u, v))
            if chave in desenhadas:
                continue
            desenhadas.add(chave)
            pu, pv = g.pontos[u], g.pontos[v]
            cor = "#2e7d32" if disp else "#c62828"
            estilo = "-" if disp else "--"
            ax.plot([pu.x, pv.x], [pu.y, pv.y], estilo, color=cor, linewidth=1, alpha=0.6, zorder=1)

    xs = [p.x for p in g.pontos.values() if p.id != 0]
    ys = [p.y for p in g.pontos.values() if p.id != 0]
    prioridades = [p.prioridade for p in g.pontos.values() if p.id != 0]
    sc = ax.scatter(xs, ys, c=prioridades, cmap="YlOrRd", s=160, edgecolor="black", zorder=2,
                     vmin=1, vmax=5)
    centro = g.pontos[0]
    ax.scatter([centro.x], [centro.y], c="blue", marker="*", s=500, edgecolor="black",
               zorder=3, label="Centro de distribuição")
    for p in g.pontos.values():
        ax.annotate(str(p.id), (p.x, p.y), textcoords="offset points", xytext=(5, 5), fontsize=8)

    plt.colorbar(sc, ax=ax, label="Prioridade (1-5)")
    ax.plot([], [], "-", color="#2e7d32", label="Via disponível")
    ax.plot([], [], "--", color="#c62828", label="Via bloqueada")
    ax.set_title("Figura 1 — Rede de atendimento (Defesa Civil)")
    ax.set_xlabel("x (km)"); ax.set_ylabel("y (km)")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig1_grafo.png"), dpi=150)
    plt.close(fig)


def fig2_solucao(g: Grafo, selecionados_dp: list[int], ordem_greedy: list[tuple[int, float]]):
    fig, ax = plt.subplots(figsize=(9, 8))
    for u, viz in g.adj.items():
        for v, w, disp in viz:
            if not disp:
                continue
            pu, pv = g.pontos[u], g.pontos[v]
            ax.plot([pu.x, pv.x], [pu.y, pv.y], "-", color="lightgray", linewidth=0.8, zorder=1)

    atendidos = set(selecionados_dp)
    for p in g.pontos.values():
        if p.id == 0:
            continue
        cor = "#2e7d32" if p.id in atendidos else "#9e9e9e"
        marcador = "o" if p.id in atendidos else "x"
        ax.scatter([p.x], [p.y], c=cor, marker=marcador, s=150, edgecolor="black", zorder=2)
        ax.annotate(str(p.id), (p.x, p.y), textcoords="offset points", xytext=(5, 5), fontsize=8)

    centro = g.pontos[0]
    ax.scatter([centro.x], [centro.y], c="blue", marker="*", s=500, edgecolor="black", zorder=3)

    # sequência gulosa dos 8 primeiros pontos, para ilustrar a ordem de atendimento
    ordem_ids = [pid for pid, _ in ordem_greedy[:8]]
    xs = [centro.x] + [g.pontos[i].x for i in ordem_ids]
    ys = [centro.y] + [g.pontos[i].y for i in ordem_ids]
    ax.plot(xs, ys, ":", color="orange", linewidth=1.5, zorder=1,
            label="Sequência Greedy (8 primeiros)")

    ax.scatter([], [], c="#2e7d32", marker="o", label="Atendido (solução DP ótima)")
    ax.scatter([], [], c="#9e9e9e", marker="x", label="Não atendido")
    ax.set_title(f"Figura 2 — Solução ótima (DP), capacidade={CAPACIDADE_VEICULO}")
    ax.set_xlabel("x (km)"); ax.set_ylabel("y (km)")
    ax.legend(loc="upper left")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig2_solucao.png"), dpi=150)
    plt.close(fig)


def fig3_dp_heatmap(tabela: list[list[int]]):
    arr = np.array(tabela)
    fig, ax = plt.subplots(figsize=(10, 6))
    im = ax.imshow(arr, aspect="auto", cmap="viridis", origin="lower")
    plt.colorbar(im, ax=ax, label="Benefício acumulado DP[i][c]")
    ax.set_xlabel("capacidade disponível (c)")
    ax.set_ylabel("pontos considerados (i)")
    ax.set_title("Figura 3 — Evolução da tabela de Programação Dinâmica")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig3_dp_heatmap.png"), dpi=150)
    plt.close(fig)


def main():
    g = carregar_grafo()
    origem = 0

    resultado_greedy = atendimento_guloso(g, origem, CAPACIDADE_VEICULO)

    pontos_candidatos = [p for pid, p in g.pontos.items() if pid != origem]
    resultado_dp = selecao_otima_dp(pontos_candidatos, CAPACIDADE_VEICULO)

    fig1_grafo(g)
    fig2_solucao(g, resultado_dp.selecionados, resultado_greedy.ordem_score)
    fig3_dp_heatmap(resultado_dp.tabela)

    print("=== QUESTÃO 1 — Comparação Greedy x Programação Dinâmica ===")
    print(f"Capacidade do veículo: {CAPACIDADE_VEICULO}")
    print(f"Greedy   -> pontos: {resultado_greedy.selecionados}")
    print(f"           demanda usada: {resultado_greedy.demanda_usada}, "
          f"benefício total: {resultado_greedy.beneficio_total}")
    print(f"DP       -> pontos: {resultado_dp.selecionados}")
    print(f"           demanda usada: {resultado_dp.demanda_usada}, "
          f"benefício total: {resultado_dp.beneficio_otimo}")
    gap = resultado_dp.beneficio_otimo - resultado_greedy.beneficio_total
    print(f"Gap (DP - Greedy): {gap} "
          f"({'DP encontrou solução superior' if gap > 0 else 'Greedy também foi ótimo nesta instância'})")

    print("\n=== Contraexemplo mínimo (Greedy != ótimo) ===")
    print(contraexemplo_greedy_vs_dp())


if __name__ == "__main__":
    main()
