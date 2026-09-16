# -*- coding: utf-8 -*-
"""
analise_q2.py — roda o pipeline completo da Questão 2 e gera:
  figures/questao2/fig1_serie_temporal.png
  figures/questao2/fig2_divide_conquer.png
  figures/questao2/fig3_escalabilidade.png
e o experimento de escalabilidade (Parte D) salvo em data/escalabilidade.csv.
"""
from __future__ import annotations
import csv
import os
import random
import time
import tracemalloc

import matplotlib.pyplot as plt

from estruturas import Registro, SerieTemporal
from brute_force import intervalo_critico_forca_bruta
from divide_conquer import intervalo_critico_divide_conquer, _caso_cruzado

BASE = os.path.dirname(__file__)
DATA_DIR = os.path.join(BASE, "..", "data")
FIG_DIR = os.path.join(BASE, "..", "figures", "questao2")


def carregar_serie() -> SerieTemporal:
    registros = []
    with open(os.path.join(DATA_DIR, "problema2.csv"), encoding="utf-8") as f:
        for row in csv.DictReader(f):
            registros.append(Registro(
                timestamp=int(row["timestamp"]), regiao=row["regiao"],
                consumo=float(row["consumo"]), capacidade_disponivel=float(row["capacidade_disponivel"]),
                prioridade=int(row["prioridade"]), custo=float(row["custo"]),
            ))
    return SerieTemporal(registros)


def serie_agregada_por_timestamp(serie: SerieTemporal) -> list[float]:
    """Agrega (soma) a criticidade de todas as regiões em cada timestamp,
    produzindo uma série 1D — é essa série que os algoritmos de intervalo
    crítico (Força Bruta / D&C) processam."""
    max_t = max(r.timestamp for r in serie.registros)
    agregada = [0.0] * (max_t + 1)
    for r in serie.registros:
        c = r.criticidade()
        agregada[r.timestamp] += c
        serie.registrar_pico(c, r.timestamp)
    return agregada


def centralizar_para_intervalo(agregada: list[float]) -> list[float]:
    """
    A criticidade agregada é sempre >= 0 (soma de termos não negativos),
    então o "intervalo de maior soma" trivialmente seria a série inteira
    -- o que não ajuda a localizar um PERÍODO crítico específico.

    Por isso, para o problema de "maximum subarray" (Partes B e C),
    trabalhamos com a série CENTRALIZADA na média:

        centralizada[t] = agregada[t] - media(agregada)

    Assim, apenas os períodos ACIMA da média contribuem positivamente
    para a soma, e o intervalo contínuo de maior soma passa a
    identificar de fato um período anormalmente crítico (e não o
    intervalo inteiro). Essa é uma técnica padrão para adaptar o
    "maximum subarray" à detecção de períodos de anomalia/pico.
    """
    media = sum(agregada) / len(agregada)
    return [x - media for x in agregada]


def fig1_serie_temporal(serie: SerieTemporal, agregada: list[float], resultado):
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)

    for regiao in sorted(serie.regioes):
        idxs = serie.por_regiao[regiao]
        ts = [serie.registros[i].timestamp for i in idxs]
        consumo = [serie.registros[i].consumo for i in idxs]
        axes[0].plot(ts, consumo, label=regiao, linewidth=1)
    axes[0].set_ylabel("Consumo")
    axes[0].set_title("Figura 1 — Consumo × tempo (por região) e intervalo crítico")
    axes[0].legend(loc="upper right", fontsize=8, ncol=3)
    axes[0].axvspan(resultado.inicio, resultado.fim, color="red", alpha=0.15)

    axes[1].plot(range(len(agregada)), agregada, color="black", linewidth=1,
                 label="Criticidade agregada")
    axes[1].axvspan(resultado.inicio, resultado.fim, color="red", alpha=0.2,
                     label=f"Intervalo crítico [{resultado.inicio}, {resultado.fim}]")
    axes[1].set_xlabel("timestamp (hora)")
    axes[1].set_ylabel("Criticidade agregada")
    axes[1].legend(loc="upper right", fontsize=8)

    fig.tight_layout()
    os.makedirs(FIG_DIR, exist_ok=True)
    fig.savefig(os.path.join(FIG_DIR, "fig1_serie_temporal.png"), dpi=150)
    plt.close(fig)


def fig2_divide_conquer(agregada: list[float]):
    """Desenha 3 níveis da árvore de decomposição do Divide & Conquer
    sobre os dados reais (mostra os intervalos [lo,hi] de cada nó)."""
    n = len(agregada)

    def dividir(lo, hi, nivel, max_nivel, nós):
        nós.setdefault(nivel, []).append((lo, hi))
        if nivel >= max_nivel or lo == hi:
            return
        mid = (lo + hi) // 2
        dividir(lo, mid, nivel + 1, max_nivel, nós)
        dividir(mid + 1, hi, nivel + 1, max_nivel, nós)

    nós = {}
    dividir(0, n - 1, 0, 3, nós)

    fig, ax = plt.subplots(figsize=(11, 5))
    cores = ["#1565c0", "#2e7d32", "#ef6c00", "#c62828"]
    for nivel, intervalos in nós.items():
        y = -nivel
        for (lo, hi) in intervalos:
            ax.plot([lo, hi], [y, y], "-", color=cores[nivel % len(cores)], linewidth=6,
                    solid_capstyle="butt", alpha=0.85)
            ax.annotate(f"[{lo},{hi}]", ((lo + hi) / 2, y), ha="center", va="bottom", fontsize=7)
        mid_marks = [((lo + hi) // 2) for (lo, hi) in intervalos]

    ax.set_yticks([-l for l in nós.keys()])
    ax.set_yticklabels([f"nível {l}\n({'problema' if l==0 else 'subproblemas'})" for l in nós.keys()])
    ax.set_xlabel("índice de tempo (posição no vetor de criticidade)")
    ax.set_title("Figura 2 — Divide and Conquer: decomposição em subintervalos (3 níveis)")
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig2_divide_conquer.png"), dpi=150)
    plt.close(fig)


def medir(func, dados):
    tracemalloc.start()
    t0 = time.perf_counter()
    func(dados)
    t1 = time.perf_counter()
    _, pico = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return (t1 - t0), pico


def experimento_escalabilidade():
    tamanhos = [100, 250, 500, 1000, 2000, 5000]
    linhas = []
    random.seed(42)
    for n in tamanhos:
        dados = [random.uniform(-5, 15) for _ in range(n)]

        t_bf, mem_bf = medir(intervalo_critico_forca_bruta, dados)
        t_dc, mem_dc = medir(intervalo_critico_divide_conquer, dados)

        ops_bf = n * (n + 1) // 2       # nº de pares (i,j) explicitamente testados
        import math
        ops_dc = int(n * math.log2(n)) if n > 1 else 1

        linhas.append({
            "n": n,
            "tempo_forca_bruta_s": round(t_bf, 6),
            "tempo_divide_conquer_s": round(t_dc, 6),
            "operacoes_forca_bruta_aprox": ops_bf,
            "operacoes_divide_conquer_aprox": ops_dc,
            "memoria_forca_bruta_bytes": mem_bf,
            "memoria_divide_conquer_bytes": mem_dc,
        })
        print(f"n={n:5d}  BF={t_bf:.5f}s  D&C={t_dc:.5f}s  "
              f"(ops BF~{ops_bf:,}, ops D&C~{ops_dc:,})")

    caminho = os.path.join(DATA_DIR, "escalabilidade.csv")
    with open(caminho, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0].keys()))
        w.writeheader()
        w.writerows(linhas)
    print(f"Resultados salvos em {caminho}")
    return linhas


def fig3_escalabilidade(linhas):
    ns = [l["n"] for l in linhas]
    t_bf = [l["tempo_forca_bruta_s"] for l in linhas]
    t_dc = [l["tempo_divide_conquer_s"] for l in linhas]

    fig, ax = plt.subplots(figsize=(9, 6))
    ax.plot(ns, t_bf, "o-", color="#c62828", label="Força Bruta O(n²)")
    ax.plot(ns, t_dc, "o-", color="#1565c0", label="Divide & Conquer O(n log n)")
    ax.set_xlabel("tamanho da entrada (n)")
    ax.set_ylabel("tempo de execução (s)")
    ax.set_title("Figura 3 — Escalabilidade: tempo × tamanho da entrada")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG_DIR, "fig3_escalabilidade.png"), dpi=150)
    plt.close(fig)

    # versão log-log, útil para visualizar o crescimento assintótico
    fig2, ax2 = plt.subplots(figsize=(9, 6))
    ax2.plot(ns, t_bf, "o-", color="#c62828", label="Força Bruta O(n²)")
    ax2.plot(ns, t_dc, "o-", color="#1565c0", label="Divide & Conquer O(n log n)")
    ax2.set_xscale("log"); ax2.set_yscale("log")
    ax2.set_xlabel("tamanho da entrada (n) [log]")
    ax2.set_ylabel("tempo de execução (s) [log]")
    ax2.set_title("Figura 3b — Escalabilidade (escala log-log)")
    ax2.legend()
    ax2.grid(alpha=0.3, which="both")
    fig2.tight_layout()
    fig2.savefig(os.path.join(FIG_DIR, "fig3b_escalabilidade_loglog.png"), dpi=150)
    plt.close(fig2)


def main():
    serie = carregar_serie()
    agregada = serie_agregada_por_timestamp(serie)
    agregada_centrada = centralizar_para_intervalo(agregada)

    resultado_bf = intervalo_critico_forca_bruta(agregada_centrada)
    resultado_dc = intervalo_critico_divide_conquer(agregada_centrada)

    print("=== QUESTÃO 2 — Intervalo crítico (série agregada) ===")
    print(f"Força Bruta       -> [{resultado_bf.inicio}, {resultado_bf.fim}] "
          f"soma={resultado_bf.soma_criticidade:.2f}")
    print(f"Divide & Conquer  -> [{resultado_dc.inicio}, {resultado_dc.fim}] "
          f"soma={resultado_dc.soma_criticidade:.2f}")
    assert resultado_bf.soma_criticidade - resultado_dc.soma_criticidade < 1e-6, \
        "BF e D&C deveriam concordar no valor ótimo!"
    print("-> BF e D&C concordam no valor ótimo (verificação cruzada OK).")

    print("\nTop 5 picos de criticidade (heap):")
    for crit, ts in serie.top_picos()[:5]:
        print(f"  timestamp={ts}  criticidade={crit:.2f}")

    fig1_serie_temporal(serie, agregada, resultado_dc)
    fig2_divide_conquer(agregada_centrada)

    print("\n=== Experimento de escalabilidade (Parte D) ===")
    linhas = experimento_escalabilidade()
    fig3_escalabilidade(linhas)


if __name__ == "__main__":
    main()
