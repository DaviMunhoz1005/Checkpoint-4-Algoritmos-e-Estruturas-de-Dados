# -*- coding: utf-8 -*-
"""
Testes da Questão 2: estruturas, Força Bruta e Divide & Conquer.
Execute com:  python -m pytest tests/test_questao2.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import random
import pytest
from estruturas import Registro, SerieTemporal
from brute_force import intervalo_critico_forca_bruta
from divide_conquer import intervalo_critico_divide_conquer


def test_criticidade_zero_capacidade_nao_quebra():
    r = Registro(timestamp=0, regiao="X", consumo=10, capacidade_disponivel=0,
                  prioridade=2, custo=1.0)
    assert r.criticidade() == pytest.approx(2 + 0.05)  # só prioridade + custo, uso=0


def test_serie_temporal_estruturas_basicas():
    registros = [
        Registro(0, "Norte", 100, 200, 3, 1.0),
        Registro(1, "Norte", 120, 200, 3, 1.0),
        Registro(0, "Sul", 80, 150, 2, 0.8),
    ]
    serie = SerieTemporal(registros)
    assert serie.regioes == {"Norte", "Sul"}
    assert len(serie.por_regiao["Norte"]) == 2
    assert serie.consumo_por_regiao("Sul") == [80]


def test_bf_e_dc_concordam_em_series_aleatorias():
    random.seed(7)
    for _ in range(15):
        n = random.randint(1, 60)
        dados = [random.uniform(-10, 10) for _ in range(n)]
        r_bf = intervalo_critico_forca_bruta(dados)
        r_dc = intervalo_critico_divide_conquer(dados)
        assert r_bf.soma_criticidade == pytest.approx(r_dc.soma_criticidade, abs=1e-9)


def test_bf_caso_todos_negativos_escolhe_o_maior_unico():
    dados = [-5, -1, -8, -3]
    resultado = intervalo_critico_forca_bruta(dados)
    assert resultado.inicio == resultado.fim == 1  # -1 é o "menos ruim"
    assert resultado.soma_criticidade == -1


def test_dc_caso_todos_negativos_escolhe_o_maior_unico():
    dados = [-5, -1, -8, -3]
    resultado = intervalo_critico_divide_conquer(dados)
    assert resultado.soma_criticidade == -1


def test_intervalo_vazio_nao_quebra():
    assert intervalo_critico_forca_bruta([]).soma_criticidade == 0.0
    assert intervalo_critico_divide_conquer([]).soma_criticidade == 0.0


def test_dc_intervalo_unico_elemento():
    resultado = intervalo_critico_divide_conquer([42.0])
    assert resultado.inicio == 0
    assert resultado.fim == 0
    assert resultado.soma_criticidade == 42.0
