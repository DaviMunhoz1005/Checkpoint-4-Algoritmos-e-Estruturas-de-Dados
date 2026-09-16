# Checkpoint 4 — Algoritmos e Estruturas de Dados (Turma W)

**Integrantes do grupo:**

| Nome | RM |
|---|---|
| _Davi Munhoz_ | _566223_ |
| _Diogo Oliveira_ | _562559_ |
| _Leandro Simoneli_ | _566539_ |
| _Lucas Aquino_ | _562414_ |
| _Lucas Bonato_ | _565356_ |

**SEED do grupo (reprodutibilidade):** `SEED = 566223`

---

## 1. Problema

O repositório resolve dois problemas independentes exigidos pelo Checkpoint 4:

- **Questão 1 — Logística de emergência:** uma equipe de Defesa Civil tem um centro de distribuição e vários pontos de atendimento conectados por um grafo ponderado (com vias indisponíveis). É preciso decidir *quais* pontos atender e *em que ordem*, respeitando a capacidade limitada do veículo.
- **Questão 2 — Consumo de energia:** uma série temporal com medições horárias de consumo por região precisa ser analisada para encontrar o **intervalo contínuo de tempo mais crítico** (maior criticidade acumulada).

## 2. Modelo adotado

### Questão 1
- Grafo ponderado `G = (V, E)`, não completo, com um nó especial (centro de distribuição, id 0) e demais nós = pontos de atendimento.
- Cada ponto tem: `pessoas_afetadas`, `prioridade` (1–5), `demanda` (peso da mochila) e `beneficio` (valor da mochila).
- O problema "escolher pontos dentro da capacidade do veículo, maximizando benefício" foi modelado como **mochila 0/1** (0/1 knapsack).
- A **ordem** de atendimento é decidida por uma função de prioridade gulosa baseada na razão benefício/(demanda × distância normalizada).

### Questão 2
- Cada observação `(timestamp, região, consumo, capacidade_disponivel, prioridade, custo)` gera uma métrica derivada `criticidade`.
- As séries de todas as regiões são agregadas por `timestamp` (soma) e depois **centralizadas na média**, para que o problema de "achar o intervalo de maior soma acumulada" (maximum subarray) não trivialmente retorne a série inteira (ver justificativa em `src/analise_q2.py::centralizar_para_intervalo`).
- O problema foi modelado como **maximum subarray problem** (subvetor contíguo de soma máxima).

## 3. Estruturas de dados

Todas justificadas por operação (não "porque funcionou") em `src/estruturas.py`:

| Estrutura | Onde | Por quê |
|---|---|---|
| `dataclass(frozen=True)` (`Ponto`, `Registro`) | Q1 e Q2 | Registro imutável, evita mutação acidental de estado compartilhado entre algoritmos |
| `dict[int, list[tuple]]` (lista de adjacência) | Q1 | Grafo esparso: acesso O(1) aos vizinhos de um nó, sem gastar O(V²) de uma matriz |
| `heap` (`heapq`) | Q1 (Dijkstra e Greedy), Q2 (top-k picos) | Extração do mínimo/máximo em O(log n), essencial para Dijkstra e para o ranking de prioridades |
| `list` ordenada por timestamp | Q2 | Acesso sequencial/indexado O(1)/O(k), necessário para Força Bruta e Divide & Conquer |
| `dict[str, list[int]]` | Q2 | Agrupar registros por região em O(1) em vez de O(n) por consulta |
| `set[str]` | Q2 | Testar existência/unicidade de região em O(1) |

## 4. Algoritmos

| Arquivo | Algoritmo | Questão |
|---|---|---|
| `src/greedy.py` | Guloso (ordem de atendimento + seleção greedy) | Q1 – Parte B |
| `src/dynamic_programming.py` | Programação Dinâmica (mochila 0/1) + contraexemplo | Q1 – Parte C/D |
| `src/brute_force.py` | Força Bruta (intervalo crítico, O(n²)) | Q2 – Parte B |
| `src/divide_conquer.py` | Divide and Conquer (maximum subarray, O(n log n)) | Q2 – Parte C |
| `src/estruturas.py` | Estruturas de dados e `Grafo.dijkstra` (auxiliar) | Q1 e Q2 |
| `src/gerar_dados.py` | Geração reprodutível dos datasets sintéticos (`SEED`) | Q1 e Q2 |
| `src/analise_q1.py` / `src/analise_q2.py` | Pipelines completos (rodar algoritmos + gerar figuras) | Q1 e Q2 |

Nenhum destes algoritmos usa funções prontas que resolvam o núcleo do problema (sem `networkx.shortest_path`, `scipy.optimize`, etc.) — bibliotecas são usadas apenas para leitura de dados (`csv`), gráficos (`matplotlib`/`numpy`) e testes (`pytest`).

## 5. Como executar

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Gerar os dados (reprodutível via SEED = número do grupo)
python src/gerar_dados.py --seed 566223

# 3. Rodar os pipelines completos (gera as figuras em figures/)
python src/analise_q1.py
python src/analise_q2.py

# 4. Rodar os testes
python -m pytest tests/ -v

# 5. (opcional) Abrir e executar os notebooks
jupyter notebook notebooks/questao1.ipynb
jupyter notebook notebooks/questao2.ipynb
```

## 6. Resultados (seed = 566223)

**Questão 1** (capacidade do veículo = 30):
- Greedy: benefício total = 426
- Programação Dinâmica (ótimo): benefício total = 517
- Contraexemplo mínimo (3 pontos, capacidade 10): Greedy = 11, DP = 16 → Greedy não é ótimo.

**Questão 2:**
- Intervalo crítico encontrado por Força Bruta e por Divide & Conquer: **idêntico** em todas as instâncias testadas (verificação cruzada automática em `analise_q2.py` e em `tests/test_questao2.py`).
- Experimento de escalabilidade (`data/escalabilidade.csv`): em `n = 5.000`, Força Bruta ≈ 0,99 s contra Divide & Conquer ≈ 0,022 s.

## 7. Complexidade

Resumo (detalhamento completo em `docs/analise_complexidade.md`):

| Algoritmo | Tempo | Espaço |
|---|---|---|
| Dijkstra | `O((V+E) log V)` | `O(V+E)` |
| Greedy (Q1) | `O((V+E) log V + N log N)` | `O(V+E+N)` |
| Programação Dinâmica (Q1) | `O(N·C)` | `O(N·C)` |
| Força Bruta (Q2) | `O(n²)` | `O(1)` auxiliar |
| Divide and Conquer (Q2) | `O(n log n)` | `O(log n)` |

## 8. Limitações

- Os dados da Q1 e Q2 são sintéticos (documentados e reprodutíveis via `SEED`), não medições reais da Defesa Civil ou do sistema elétrico brasileiro.
- A função de prioridade Greedy (Q1) e a função de criticidade (Q2) são escolhas do grupo, calibradas empiricamente; outras ponderações são possíveis e mudariam os resultados numéricos (mas não a estrutura dos algoritmos).
- A Programação Dinâmica da Q1 é pseudo-polinomial: seu tempo depende do valor de `C` (capacidade), não apenas do número de itens — para capacidades muito grandes, a tabela pode ficar cara em memória.
- O Divide & Conquer da Q2 assume que a métrica de criticidade é aditiva ao longo do tempo; se a definição de "período crítico" exigir critérios não aditivos (ex.: picos isolados, não intervalos contínuos), o modelo precisaria ser revisto.

---

## Pergunta final obrigatória

> **Qual foi a decisão algorítmica mais importante tomada pelo grupo? Apresente uma alternativa que vocês descartaram e explique, considerando tempo, memória e qualidade da solução, por que a abordagem escolhida foi considerada mais adequada.**

A decisão mais importante foi modelar a seleção de pontos de atendimento sob capacidade limitada (Questão 1) como mochila 0/1 resolvida por Programação Dinâmica, em vez de confiar apenas na heurística gulosa por razão benefício/demanda/distância. A alternativa descartada foi usar somente o Greedy como solução final: é mais rápido (`O(N log N)` contra `O(N·C)` da DP) e usa menos memória (`O(N)` contra `O(N·C)`), mas não garante otimalidade. Construímos um contraexemplo mínimo (três pontos, capacidade 10) em que o Greedy escolhe o item de maior razão valor/peso (benefício 11) e descarta dois itens que, juntos, cabem exatamente na capacidade e valem mais (benefício 16) — perda de 31% de benefício só pela ordem gulosa. No dataset completo (21 pontos, capacidade 30), o mesmo padrão se repetiu: a DP superou o Greedy em 91 unidades de benefício (517 contra 426), equivalente a atender mais pessoas do que o Greedy deixaria de fora.

Como o número de pontos é pequeno (dezenas, não milhões) e a capacidade do veículo é um inteiro moderado, o custo `O(N·C)` da DP é tratável (tabela com poucas centenas de células) e a garantia de otimalidade compensa a perda de velocidade. Mantivemos o Greedy no pipeline como uma primeira passada rápida para ORDENAR o atendimento (útil operacionalmente: dá para começar a despachar recursos antes de terminar de calcular o subconjunto ótimo), mas a decisão final de "quais pontos entram no veículo" usa a DP. Essa combinação — Greedy para velocidade de decisão em campo, DP para a alocação final de recursos escassos — equilibra tempo de resposta e qualidade da solução, exatamente o tipo de escolha que uma operação real de Defesa Civil precisaria fazer sob pressão de tempo e recursos limitados.
