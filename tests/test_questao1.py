# -*- coding: utf-8 -*-
"""
Testes da Questão 1: estruturas, Dijkstra, Greedy e Programação Dinâmica.
Execute com:  python -m pytest tests/test_questao1.py -v
(rodar a partir da raiz do repositório, com src/ no PYTHONPATH — ver conftest)
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest
from estruturas import Grafo, Ponto
from greedy import atendimento_guloso, calcular_score
from dynamic_programming import selecao_otima_dp, contraexemplo_greedy_vs_dp


def montar_grafo_simples() -> Grafo:
    g = Grafo()
    g.add_ponto(Ponto(0, "Centro", 0, 0, 0, 0, 0, 0))
    g.add_ponto(Ponto(1, "A", 3, 0, 100, 5, 4, 40))
    g.add_ponto(Ponto(2, "B", 0, 4, 50, 2, 6, 20))
    g.add_ponto(Ponto(3, "C", 6, 8, 200, 4, 3, 50))
    g.add_aresta(0, 1, 3.0)
    g.add_aresta(0, 2, 4.0)
    g.add_aresta(1, 3, 6.0)
    return g


def test_dijkstra_distancia_direta():
    g = montar_grafo_simples()
    dist = g.dijkstra(0)
    assert dist[1] == pytest.approx(3.0)
    assert dist[2] == pytest.approx(4.0)


def test_dijkstra_via_indisponivel_bloqueia_caminho():
    g = Grafo()
    g.add_ponto(Ponto(0, "Centro", 0, 0, 0, 0, 0, 0))
    g.add_ponto(Ponto(1, "A", 1, 0, 10, 1, 1, 1))
    g.add_aresta(0, 1, 5.0, disponivel=False)
    dist = g.dijkstra(0)
    assert dist[1] == float("inf")


def test_ponto_e_imutavel():
    p = Ponto(1, "A", 0, 0, 10, 1, 1, 1)
    with pytest.raises(Exception):
        p.demanda = 999  # dataclass frozen deve impedir alteração


def test_score_ponto_inalcancavel_e_negativo():
    p = Ponto(1, "A", 0, 0, 10, 1, 5, 20)
    assert calcular_score(p, float("inf")) < 0


def test_greedy_respeita_capacidade():
    g = montar_grafo_simples()
    resultado = atendimento_guloso(g, origem=0, capacidade=5)
    assert resultado.demanda_usada <= 5


def test_dp_nao_ultrapassa_capacidade():
    pontos = [
        Ponto(1, "A", 0, 0, 0, 1, demanda=6, beneficio=11),
        Ponto(2, "B", 0, 0, 0, 1, demanda=5, beneficio=8),
        Ponto(3, "C", 0, 0, 0, 1, demanda=5, beneficio=8),
    ]
    resultado = selecao_otima_dp(pontos, capacidade=10)
    assert resultado.demanda_usada <= 10


def test_dp_e_otimo_no_contraexemplo():
    saida = contraexemplo_greedy_vs_dp()
    assert saida["dp_beneficio"] >= saida["greedy_beneficio"]
    assert saida["dp_beneficio"] == 16
    assert saida["greedy_beneficio"] == 11


def test_dp_sem_pontos_retorna_zero():
    resultado = selecao_otima_dp([], capacidade=10)
    assert resultado.beneficio_otimo == 0
    assert resultado.selecionados == []


def test_dp_capacidade_zero_nao_seleciona_nada():
    pontos = [Ponto(1, "A", 0, 0, 0, 1, demanda=3, beneficio=10)]
    resultado = selecao_otima_dp(pontos, capacidade=0)
    assert resultado.selecionados == []
    assert resultado.beneficio_otimo == 0
