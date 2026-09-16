# -*- coding: utf-8 -*-
"""
divide_conquer.py — Questão 2, Parte C
=========================================

Resolve o MESMO problema de brute_force.py (intervalo contíguo de maior
soma de criticidade) usando Divide and Conquer — a versão clássica do
"maximum subarray problem" (Bentley/CLRS), implementada do zero.

    DIVIDE
      -> parte o vetor de criticidades ao meio: [lo, mid] e [mid+1, hi]
    SOLVE LEFT
      -> resolve recursivamente o subproblema na metade esquerda
    SOLVE RIGHT
      -> resolve recursivamente o subproblema na metade direita
    SOLVE CROSSING CASE
      -> resolve o caso em que o intervalo ótimo ATRAVESSA o meio
         (começa na metade esquerda e termina na direita)
    COMBINE
      -> compara as três soluções (esquerda, direita, cruzando) e
         devolve a de maior soma

Caso-base
---------
Quando o subvetor tem exatamly 1 elemento (lo == hi), o único intervalo
possível é [lo, lo], com soma = criticidades[lo].

Caso que atravessa a divisão (crossing case)
---------------------------------------------
Fixamos o "mid" como fronteira. Caminhamos de `mid` para a ESQUERDA
acumulando soma, guardando o melhor ponto de início `i` que maximiza a
soma da metade esquerda que termina em `mid`. Fazemos o mesmo de
`mid+1` para a DIREITA, guardando o melhor fim `j`. O intervalo
cruzado ótimo é [i, j], com soma = soma_esquerda_max + soma_direita_max.
Isso é O(n) para cada chamada (não precisa testar todos os pares, só
duas varreduras lineares a partir do meio).

Complexidade
------------
T(n) = 2*T(n/2) + O(n)   (duas chamadas recursivas de tamanho n/2, mais
                            O(n) para resolver o caso cruzado e combinar)

Pelo Teorema Mestre (a=2, b=2, f(n)=O(n) => f(n) = Θ(n^log_b(a)) = Θ(n)):
    T(n) = Θ(n log n)

Espaço:
    - Profundidade da recursão: O(log n) (árvore balanceada, divide ao meio)
    - Pilha de chamadas: O(log n)
    - Não alocamos cópias do vetor a cada chamada (usamos índices
      lo/hi sobre o mesmo vetor), então o espaço auxiliar total é
      S(n) = O(log n).
"""

from __future__ import annotations
from dataclasses import dataclass
from brute_force import ResultadoIntervalo


def _caso_cruzado(criticidades: list[float], lo: int, mid: int, hi: int) -> ResultadoIntervalo:
    soma_esq = float("-inf")
    soma = 0.0
    melhor_i = mid
    for i in range(mid, lo - 1, -1):
        soma += criticidades[i]
        if soma > soma_esq:
            soma_esq = soma
            melhor_i = i

    soma_dir = float("-inf")
    soma = 0.0
    melhor_j = mid + 1
    for j in range(mid + 1, hi + 1):
        soma += criticidades[j]
        if soma > soma_dir:
            soma_dir = soma
            melhor_j = j

    return ResultadoIntervalo(melhor_i, melhor_j, soma_esq + soma_dir)


def _resolver(criticidades: list[float], lo: int, hi: int) -> ResultadoIntervalo:
    # CASO-BASE
    if lo == hi:
        return ResultadoIntervalo(lo, hi, criticidades[lo])

    mid = (lo + hi) // 2

    # SOLVE LEFT
    esquerda = _resolver(criticidades, lo, mid)
    # SOLVE RIGHT
    direita = _resolver(criticidades, mid + 1, hi)
    # SOLVE CROSSING CASE
    cruzado = _caso_cruzado(criticidades, lo, mid, hi)

    # COMBINE
    melhor = max([esquerda, direita, cruzado], key=lambda r: r.soma_criticidade)
    return melhor


def intervalo_critico_divide_conquer(criticidades: list[float]) -> ResultadoIntervalo:
    n = len(criticidades)
    if n == 0:
        return ResultadoIntervalo(0, -1, 0.0)
    return _resolver(criticidades, 0, n - 1)
