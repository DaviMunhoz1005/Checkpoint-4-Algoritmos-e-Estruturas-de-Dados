# -*- coding: utf-8 -*-
"""
dynamic_programming.py — Questão 1, Parte C
=============================================

Escolhe a combinação de pontos de atendimento que MAXIMIZA o benefício
total sem ultrapassar a capacidade C do veículo. É uma instância do
problema da mochila 0/1 (0/1 knapsack).

Modelagem formal
-----------------
1. Estado:
     DP[i][c] = maior benefício total alcançável considerando apenas os
                primeiros `i` pontos candidatos (na ordem em que estão
                na lista) e usando no máximo `c` unidades de capacidade.

2. Decisão em cada passo i (1-indexado, ponto = pontos[i-1]):
     - NÃO atender o ponto i:      DP[i][c] = DP[i-1][c]
     - ATENDER o ponto i (se cabe): DP[i][c] = DP[i-1][c - demanda_i] + beneficio_i
     Tomamos o máximo entre as duas opções.

3. Caso-base:
     DP[0][c] = 0 para todo c  (nenhum ponto considerado -> benefício 0)
     DP[i][0] = 0 para todo i  (sem capacidade nenhuma -> benefício 0)

4. Recorrência:
     DP[i][c] = DP[i-1][c]                                   se demanda_i > c
     DP[i][c] = max(DP[i-1][c], DP[i-1][c-demanda_i] + beneficio_i)  caso contrário

5. Reconstrução da solução:
     Partindo de DP[n][C], andamos de i = n até i = 1:
       - se DP[i][c] == DP[i-1][c]: o ponto i NÃO foi usado, seguimos com (i-1, c)
       - caso contrário: o ponto i FOI usado; adicionamos seu id à solução e
         seguimos com (i-1, c - demanda_i)
     Isso reconstrói exatamente o subconjunto de pontos escolhido, não
     apenas o valor ótimo.

Complexidade
------------
Sejam N = número de pontos candidatos e C = capacidade do veículo
(inteiro). A tabela tem (N+1) x (C+1) células, cada uma calculada em
O(1) a partir de vizinhas já computadas:
    Tempo:  O(N * C)
    Espaço: O(N * C) para a tabela completa (necessária para
            reconstrução exata do subconjunto); pode ser reduzida
            para O(C) se guardarmos apenas o valor ótimo, sem
            reconstrução.
"""

from __future__ import annotations
from dataclasses import dataclass
from estruturas import Ponto


@dataclass
class ResultadoDP:
    beneficio_otimo: int
    selecionados: list[int]     # ids dos pontos escolhidos
    demanda_usada: int
    tabela: list[list[int]]     # DP[i][c], guardada para a Figura 3


def selecao_otima_dp(pontos: list[Ponto], capacidade: int) -> ResultadoDP:
    n = len(pontos)
    C = capacidade
    # DP[i][c]
    dp = [[0] * (C + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        ponto = pontos[i - 1]
        demanda_i = ponto.demanda
        beneficio_i = ponto.beneficio
        linha_anterior = dp[i - 1]
        linha_atual = dp[i]
        for c in range(C + 1):
            sem_i = linha_anterior[c]
            if demanda_i <= c:
                com_i = linha_anterior[c - demanda_i] + beneficio_i
                linha_atual[c] = com_i if com_i > sem_i else sem_i
            else:
                linha_atual[c] = sem_i

    # Reconstrução
    selecionados: list[int] = []
    c = C
    for i in range(n, 0, -1):
        if dp[i][c] != dp[i - 1][c]:
            ponto = pontos[i - 1]
            selecionados.append(ponto.id)
            c -= ponto.demanda

    selecionados.reverse()
    demanda_usada = sum(p.demanda for p in pontos if p.id in selecionados)

    return ResultadoDP(
        beneficio_otimo=dp[n][C],
        selecionados=selecionados,
        demanda_usada=demanda_usada,
        tabela=dp,
    )


def contraexemplo_greedy_vs_dp():
    """
    Contraexemplo MÍNIMO e autoexplicativo (Parte D / defesa 2):
    3 pontos candidatos e capacidade 10.

        ponto | demanda | beneficio | score = beneficio/demanda
        A     |   6      |   11      |  1.833   <- maior razão, Greedy escolhe primeiro
        B     |   5      |    8      |  1.6
        C     |   5      |    8      |  1.6

    Greedy (por razão benefício/demanda) escolhe A primeiro (score mais
    alto). Sobra capacidade 10-6=4, que não é suficiente para B nem C
    (ambos precisam de 5). Resultado guloso: só A -> benefício 11.

    A solução ótima é B + C: demanda 5+5=10 (cabe exatamente),
    benefício 8+8=16 > 11.

    Isso prova que a razão benefício/demanda, que é ótima para a
    mochila FRACIONÁRIA, não garante o ótimo na mochila 0/1: o Greedy
    "gasta" a maior parte da capacidade em um único item de razão alta
    e descarta dois itens que, juntos, cabem perfeitamente e valem mais.
    """
    pontos = [
        Ponto(1, "A", 0, 0, 0, 1, demanda=6, beneficio=11),
        Ponto(2, "B", 0, 0, 0, 1, demanda=5, beneficio=8),
        Ponto(3, "C", 0, 0, 0, 1, demanda=5, beneficio=8),
    ]
    capacidade = 10

    # guloso simples por razão beneficio/demanda (sem distância, para isolar o efeito)
    ordenados = sorted(pontos, key=lambda p: p.beneficio / p.demanda, reverse=True)
    usado, beneficio_greedy, escolhidos_greedy = 0, 0, []
    for p in ordenados:
        if usado + p.demanda <= capacidade:
            usado += p.demanda
            beneficio_greedy += p.beneficio
            escolhidos_greedy.append(p.id)

    resultado_dp = selecao_otima_dp(pontos, capacidade)

    return {
        "capacidade": capacidade,
        "greedy_escolhidos": escolhidos_greedy,
        "greedy_beneficio": beneficio_greedy,
        "dp_escolhidos": resultado_dp.selecionados,
        "dp_beneficio": resultado_dp.beneficio_otimo,
    }


if __name__ == "__main__":
    print(contraexemplo_greedy_vs_dp())
