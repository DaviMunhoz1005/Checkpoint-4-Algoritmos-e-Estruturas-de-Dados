# -*- coding: utf-8 -*-
"""
greedy.py — Questão 1, Parte B
===============================

Estratégia gulosa para decidir a ORDEM de atendimento dos pontos e,
em seguida, selecionar quais pontos entram no veículo de capacidade
limitada C (para comparação direta com a Programação Dinâmica).

Função de prioridade (score)
-----------------------------
Para cada ponto p, definimos:

    score(p) = (beneficio(p) + PESO_PESSOAS * pessoas_afetadas(p) * prioridade(p))
               / (demanda(p) * (1 + dist(p) / DIST_REF))

Justificativa matemática (por que essa decisão é "localmente vantajosa"):
    - O numerador mede o "ganho" de atender o ponto: benefício direto
      declarado + um termo que cresce com pessoas afetadas ponderadas
      pela prioridade da região (uma região de prioridade 5 com muitas
      pessoas pesa mais que uma de prioridade 1 com poucas pessoas).
    - O denominador mede o "custo" de atender o ponto: quanto de
      capacidade do veículo ele consome (demanda) e quão longe está do
      centro de distribuição (dist), normalizado por uma distância de
      referência DIST_REF para manter as duas grandezas na mesma ordem
      de magnitude.
    - `score` é, portanto, uma razão benefício-por-unidade-de-recurso-e-
      distância — a mesma lógica do algoritmo guloso clássico para a
      mochila fracionária (kanpsack fracionário), que é comprovadamente
      ótimo quando os itens podem ser fracionados. Como aqui os itens
      são 0/1 (atende-se o ponto inteiro ou não), essa razão deixa de
      ser garantidamente ótima — e é exatamente essa lacuna que a
      Parte C (Programação Dinâmica) resolve de forma exata, e que a
      Parte D explora com um contraexemplo.
    - Escolher o maior `score` primeiro é localmente vantajoso porque,
      a cada passo, maximiza o benefício marginal obtido por unidade de
      capacidade ainda disponível — é a escolha gulosa clássica
      "melhor razão valor/peso primeiro".
"""

from __future__ import annotations
import heapq
from dataclasses import dataclass
from estruturas import Grafo, Ponto

PESO_PESSOAS = 0.05
DIST_REF = 50.0


@dataclass
class ResultadoGreedy:
    ordem_score: list[tuple[int, float]]   # (id_ponto, score) na ordem de prioridade
    selecionados: list[int]                # ids escolhidos dentro da capacidade
    demanda_usada: int
    beneficio_total: int


def calcular_score(ponto: Ponto, distancia: float) -> float:
    if distancia == float("inf") or ponto.demanda <= 0:
        return -1.0  # ponto inalcançável ou com demanda inválida nunca é escolhido
    numerador = ponto.beneficio + PESO_PESSOAS * ponto.pessoas_afetadas * ponto.prioridade
    denominador = ponto.demanda * (1 + distancia / DIST_REF)
    return numerador / denominador


def atendimento_guloso(grafo: Grafo, origem: int, capacidade: int) -> ResultadoGreedy:
    """
    1) Calcula a distância do centro de distribuição a cada ponto
       (Dijkstra, implementado em estruturas.Grafo).
    2) Usa um HEAP (fila de prioridade) para ordenar os pontos por score
       decrescente em O(n log n) — não é uma simples chamada a
       `sorted`, para deixar explícito o uso de heap pedido pelo
       enunciado.
    3) Varre a ordem resultante e vai "empacotando" pontos no veículo
       enquanto a demanda acumulada não ultrapassa a capacidade
       (decisão gulosa: nunca reconsidera uma escolha já feita).
    """
    distancias = grafo.dijkstra(origem)

    heap: list[tuple[float, int]] = []
    for pid, ponto in grafo.pontos.items():
        if pid == origem:
            continue
        s = calcular_score(ponto, distancias.get(pid, float("inf")))
        if s < 0:
            continue
        heapq.heappush(heap, (-s, pid))  # heap de mínimo -> negativo = maior score primeiro

    ordem_score: list[tuple[int, float]] = []
    selecionados: list[int] = []
    demanda_usada = 0
    beneficio_total = 0

    while heap:
        neg_score, pid = heapq.heappop(heap)
        score = -neg_score
        ordem_score.append((pid, score))
        ponto = grafo.pontos[pid]
        if demanda_usada + ponto.demanda <= capacidade:
            selecionados.append(pid)
            demanda_usada += ponto.demanda
            beneficio_total += ponto.beneficio

    return ResultadoGreedy(
        ordem_score=ordem_score,
        selecionados=selecionados,
        demanda_usada=demanda_usada,
        beneficio_total=beneficio_total,
    )
