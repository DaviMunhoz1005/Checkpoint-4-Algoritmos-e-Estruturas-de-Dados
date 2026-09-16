# -*- coding: utf-8 -*-
"""
brute_force.py — Questão 2, Parte B
======================================

Encontra o intervalo contínuo de tempo [i, j] que maximiza a soma
acumulada de criticidade, examinando EXPLICITAMENTE os intervalos
possíveis (nada de biblioteca pronta).

criticidade(i) já foi definida em estruturas.Registro.criticidade().

Estratégia de força bruta adotada
----------------------------------
Para cada início `i`, mantemos uma soma corrente e vamos estendendo o
fim `j` de i até n-1, acumulando `soma += criticidade[j]` a cada passo
(em vez de recalcular a soma do zero, o que seria O(n^3)). Ainda assim
o algoritmo é força bruta porque testa EXPLICITAMENTE todo par (i, j)
com i <= j, sem nenhuma poda ou divisão do problema.

Complexidade
------------
- Dois laços aninhados (i de 0..n-1, j de i..n-1): O(n^2) pares testados.
- Cada par é avaliado em O(1) (soma incremental), então o tempo total
  é O(n^2).
- Espaço extra: O(1) além do vetor de entrada (apenas variáveis
  escalares), logo S(n) = O(1) (fora do vetor de criticidades, que é
  a própria entrada).
"""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class ResultadoIntervalo:
    inicio: int
    fim: int
    soma_criticidade: float


def intervalo_critico_forca_bruta(criticidades: list[float]) -> ResultadoIntervalo:
    n = len(criticidades)
    if n == 0:
        return ResultadoIntervalo(0, -1, 0.0)

    melhor_soma = float("-inf")
    melhor_i, melhor_j = 0, 0

    for i in range(n):
        soma = 0.0
        for j in range(i, n):
            soma += criticidades[j]          # examina explicitamente o intervalo [i, j]
            if soma > melhor_soma:
                melhor_soma = soma
                melhor_i, melhor_j = i, j

    return ResultadoIntervalo(melhor_i, melhor_j, melhor_soma)
