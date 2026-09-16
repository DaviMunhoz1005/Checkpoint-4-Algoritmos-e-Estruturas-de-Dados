# -*- coding: utf-8 -*-
"""
estruturas.py
=============

Estruturas de dados usadas nas Questões 1 e 2, implementadas "na mão"
(sem bibliotecas de alto nível que resolvam o núcleo do problema).

Cada estrutura é justificada pela operação em que ela é vantajosa dentro
dos algoritmos deste projeto (ver docstring de cada classe/função).
"""

from __future__ import annotations
import heapq
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# QUESTÃO 1 — Grafo da Defesa Civil
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Ponto:
    """
    Representa um ponto de atendimento.

    Usamos uma tupla imutável (via dataclass frozen, que se comporta como
    uma tupla nomeada) porque um "ponto" é um registro que não deve ser
    alterado depois de criado: id, prioridade, demanda e benefício são
    lidos por vários algoritmos (Greedy, DP, plot) e a imutabilidade evita
    bugs de estado compartilhado, além de permitir usar Ponto como chave
    de dict/set caso necessário (é hashável).
    """
    id: int
    nome: str
    x: float
    y: float
    pessoas_afetadas: int
    prioridade: int          # 1 (baixa) .. 5 (altíssima)
    demanda: int             # unidades de recurso necessárias (peso no knapsack)
    beneficio: int           # benefício esperado ao atender o ponto (valor no knapsack)


class Grafo:
    """
    Grafo ponderado, não necessariamente conexo, representado como lista
    de adjacência baseada em `dict[int, list[tuple[int, float, bool]]]`.

    Por que dict + list de adjacência (e não matriz de adjacência)?
    -----------------------------------------------------------------
    - O grafo é esparso (35 arestas para ~21 nós, bem menos que os ~210
      pares possíveis de um grafo completo). Uma matriz gastaria O(V^2)
      de memória e a maior parte seria zero/ausente.
    - `dict` dá acesso O(1) amortizado à lista de vizinhos de um nó,
      que é exatamente a operação repetida no Dijkstra (relaxar arestas
      de um nó retirado da fila de prioridade).
    - `list` de tuplas (vizinho, peso, disponível) é compacta e permite
      marcar uma via como indisponível sem removê-la fisicamente do
      grafo (mantém o dado bruto, útil para a Figura 1 e para o cenário
      "o professor altera uma conexão").
    """

    def __init__(self):
        self.adj: dict[int, list[tuple[int, float, bool]]] = {}
        self.pontos: dict[int, Ponto] = {}

    def add_ponto(self, ponto: Ponto) -> None:
        self.pontos[ponto.id] = ponto
        self.adj.setdefault(ponto.id, [])

    def add_aresta(self, u: int, v: int, peso: float, disponivel: bool = True) -> None:
        self.adj.setdefault(u, []).append((v, peso, disponivel))
        self.adj.setdefault(v, []).append((u, peso, disponivel))

    def vizinhos_disponiveis(self, u: int):
        return [(v, w) for (v, w, disp) in self.adj.get(u, []) if disp]

    def dijkstra(self, origem: int) -> dict[int, float]:
        """
        Implementação própria de Dijkstra usando um heap binário (heapq)
        como fila de prioridade.

        Por que heap?
        -------------
        O algoritmo precisa repetidamente extrair o nó não visitado com
        MENOR distância provisória. Um heap binário faz
        extract-min em O(log V) e inserir/relaxar em O(log V), contra
        O(V) de uma busca linear por mínimo em uma lista. Isso é o que
        garante a complexidade O((V + E) log V) do algoritmo.
        """
        dist = {no: float("inf") for no in self.adj}
        dist[origem] = 0.0
        visitado: set[int] = set()
        fila: list[tuple[float, int]] = [(0.0, origem)]

        while fila:
            d_atual, u = heapq.heappop(fila)
            if u in visitado:
                continue
            visitado.add(u)
            if d_atual > dist[u]:
                continue
            for v, w, disponivel in self.adj.get(u, []):
                if not disponivel:
                    continue
                novo = d_atual + w
                if novo < dist.get(v, float("inf")):
                    dist[v] = novo
                    heapq.heappush(fila, (novo, v))
        return dist


# ---------------------------------------------------------------------------
# QUESTÃO 2 — Séries de consumo de energia
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Registro:
    """
    Um registro horário de consumo (imutável — ver justificativa em Ponto).
    """
    timestamp: int          # índice/hora sequencial (0, 1, 2, ...)
    regiao: str
    consumo: float
    capacidade_disponivel: float
    prioridade: int
    custo: float

    def criticidade(self, w_uso: float = 10.0, w_prioridade: float = 1.0,
                     w_custo: float = 0.05) -> float:
        """
        Função de criticidade adotada pelo grupo:

            criticidade = w_uso * (consumo / capacidade_disponivel)
                          + w_prioridade * prioridade
                          + w_custo * custo

        Justificativa: o termo `consumo/capacidade_disponivel` captura o
        quão perto do limite a região está (um consumo alto só é grave se
        a capacidade for pequena); o termo de prioridade eleva regiões
        sensíveis (hospitais, etc.); o termo de custo penaliza levemente
        períodos caros. Os pesos foram calibrados empiricamente para que
        nenhum termo domine sozinho a métrica.
        """
        uso = self.consumo / self.capacidade_disponivel if self.capacidade_disponivel > 0 else 0.0
        return w_uso * uso + w_prioridade * self.prioridade + w_custo * self.custo


class SerieTemporal:
    """
    Container para os registros de consumo, organizado com QUATRO
    estruturas de dados distintas, cada uma vantajosa para uma consulta:

    1. `self.registros`  -> LIST, ordenada por timestamp.
       Vantagem: os algoritmos de intervalo crítico (Força Bruta e
       Divide & Conquer) precisam de acesso indexado e sequencial
       (registros[i], registros[i+1], slices [lo:hi]) em O(1)/O(k).
       Isso não é possível em O(1) com um dict ou set.

    2. `self.por_regiao` -> DICT[str, list[int]] mapeando região -> lista
       de índices (posições em `registros`).
       Vantagem: "consumo por região" exige agrupar rapidamente todos os
       registros de uma região; com o dict isso é O(1) para localizar o
       balde da região, em vez de varrer a lista inteira (O(n)) a cada
       consulta.

    3. `self.regioes` -> SET[str] com as regiões distintas.
       Vantagem: existência/unicidade ("quais regiões existem?",
       "região X já apareceu?") em O(1), sem duplicar nomes e sem
       precisar varrer `por_regiao.keys()` convertendo tipos.

    4. `self.heap_picos` -> HEAP (heapq) com os k maiores picos de
       criticidade observados.
       Vantagem: identificar os "top-k períodos críticos" a qualquer
       momento é uma operação de fila de prioridade; manter um heap de
       tamanho k dá inserção O(log k) e evita reordenar a lista inteira
       (O(n log n)) toda vez que se quer o ranking de picos.
    """

    def __init__(self, registros: list[Registro]):
        self.registros: list[Registro] = sorted(registros, key=lambda r: r.timestamp)

        self.por_regiao: dict[str, list[int]] = {}
        self.regioes: set[str] = set()
        for idx, r in enumerate(self.registros):
            self.por_regiao.setdefault(r.regiao, []).append(idx)
            self.regioes.add(r.regiao)

        self.heap_picos: list[tuple[float, int]] = []  # (criticidade, timestamp)

    def registrar_pico(self, criticidade: float, timestamp: int, k: int = 10) -> None:
        """Mantém um heap (min-heap) com os k maiores picos de criticidade."""
        item = (criticidade, timestamp)
        if len(self.heap_picos) < k:
            heapq.heappush(self.heap_picos, item)
        elif criticidade > self.heap_picos[0][0]:
            heapq.heapreplace(self.heap_picos, item)

    def top_picos(self) -> list[tuple[float, int]]:
        return sorted(self.heap_picos, reverse=True)

    def consumo_por_regiao(self, regiao: str) -> list[float]:
        return [self.registros[i].consumo for i in self.por_regiao.get(regiao, [])]
