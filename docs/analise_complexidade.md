# Análise de Complexidade

Notação usada:
- **Questão 1:** `V` = número de vértices (pontos + centro), `E` = número de arestas, `N` = número de pontos candidatos considerados pela DP, `C` = capacidade do veículo.
- **Questão 2:** `n` = número de observações na série temporal (após agregação por timestamp).

---

## Questão 1 — Logística de emergência

### Dijkstra (`estruturas.Grafo.dijkstra`)
Usado para calcular a distância do centro de distribuição a cada ponto (entrada do score do Greedy).

- Cada vértice é inserido/atualizado no heap no máximo uma vez por aresta relaxada → no máximo `E` operações de heap.
- `heappush`/`heappop` custam `O(log V)`.
- **Tempo:** `O((V + E) log V)`.
- **Espaço:** `O(V + E)` — lista de adjacência (`O(V+E)`), dicionário de distâncias (`O(V)`) e heap (`O(E)` no pior caso, pois pode conter entradas obsoletas).

### Greedy (`greedy.atendimento_guloso`)
1. Roda Dijkstra: `O((V+E) log V)`.
2. Constrói o heap de scores: `N` inserções `O(log N)` cada → `O(N log N)`.
3. Esvazia o heap somando demandas: `N` extrações `O(log N)` cada → `O(N log N)`.

- **Tempo total:** `O((V+E) log V + N log N)`.
- **Espaço:** `O(V + E + N)` (grafo + heap de scores).

### Programação Dinâmica — mochila 0/1 (`dynamic_programming.selecao_otima_dp`)
A tabela `DP[i][c]` tem `(N+1) × (C+1)` células, cada uma calculada em tempo constante a partir de duas células já computadas (a linha anterior).

- **Tempo:** `O(N · C)` — dois laços aninhados, o externo percorre os `N` pontos e o interno percorre as `C+1` capacidades possíveis.
- **Espaço:** `O(N · C)` para a tabela completa, necessária porque a reconstrução da solução (Parte C, item 5) percorre a tabela de trás para frente comparando `DP[i][c]` com `DP[i-1][c]`. Se apenas o valor ótimo (sem reconstrução) fosse necessário, bastaria guardar a linha anterior, reduzindo o espaço para `O(C)`.

### Comparação Greedy × DP
O Greedy é assintoticamente mais rápido (`O(N log N)` vs `O(N·C)`), mas não garante otimalidade (ver contraexemplo em `dynamic_programming.contraexemplo_greedy_vs_dp`, Parte D do relatório). A DP é exata, mas seu custo cresce com a capacidade `C`, o que a torna impraticável se `C` for um número muito grande (pseudo-polinomial, não polinomial no tamanho da entrada em bits).

---

## Questão 2 — Consumo de energia

### Força Bruta (`brute_force.intervalo_critico_forca_bruta`)
Dois laços aninhados: o externo escolhe o início `i` (`n` valores), o interno estende o fim `j` de `i` até `n-1`, com soma acumulada incremental (evita recomputar a soma do zero, mas ainda examina explicitamente todo par `(i,j)` com `i ≤ j`).

- Número de pares examinados: `n + (n-1) + ... + 1 = n(n+1)/2`.
- **Tempo:** `O(n²)`.
- **Espaço:** `O(1)` de memória auxiliar além do vetor de entrada (apenas variáveis escalares de soma e índices).

### Divide and Conquer (`divide_conquer.intervalo_critico_divide_conquer`)
Recorrência de divisão ao meio, com um passo de combinação linear:

```
T(n) = 2 T(n/2) + Θ(n)
```

O termo `Θ(n)` vem da resolução do caso que atravessa a divisão (`_caso_cruzado`), que faz duas varreduras lineares (uma para a esquerda do meio, outra para a direita), e da combinação (comparação de 3 resultados, `O(1)`).

Pelo **Teorema Mestre** com `a = 2`, `b = 2`, `f(n) = Θ(n)`:
`n^(log_b a) = n^(log_2 2) = n^1 = Θ(n) = f(n)` → caso 2 do Teorema Mestre:

```
T(n) = Θ(n log n)
```

- **Tempo:** `O(n log n)`.
- **Espaço:**
  - Profundidade da recursão: a árvore de chamadas é balanceada e divide o problema ao meio a cada nível, logo tem `O(log n)` níveis.
  - Cada chamada usa `O(1)` de memória própria (apenas índices `lo, mid, hi` e variáveis de soma — não copiamos sub-vetores).
  - **Espaço auxiliar total (pilha de recursão):** `O(log n)`.

### Verificação cruzada
`analise_q2.py` executa Força Bruta e Divide & Conquer sobre os mesmos dados e faz um `assert` de que os dois valores ótimos coincidem — essa é a evidência empírica de que a decomposição (divide/solve/combine) está correta.

### Experimento de escalabilidade (Parte D)
Ver `data/escalabilidade.csv` e Figura 3/3b, geradas por `analise_q2.experimento_escalabilidade`. Os tempos medidos com `time.perf_counter()` (tempo de parede) e o pico de memória medido com `tracemalloc` confirmam o comportamento assintótico esperado: a curva da Força Bruta cresce quadraticamente (visível na escala linear) e a do Divide & Conquer cresce quase linearmente (as duas retas aparecem paralelas na escala log-log, com inclinação próxima de 1 para D&C e próxima de 2 para Força Bruta).

### E se os dados crescerem de 1.000 para 1.000.000 de registros?
- **Força Bruta `O(n²)`:** o tempo cresceria por um fator de `(1.000.000/1.000)² = 1.000.000×`. Extrapolando a partir do tempo medido para `n=5.000` (~0,99 s), a Força Bruta se tornaria **inviável** em produção (estimativa da ordem de ~275 horas, mais de uma semana).
- **Divide & Conquer `O(n log n)`:** o fator de crescimento é `(1.000.000 · log₂(1.000.000)) / (1.000 · log₂(1.000)) ≈ (1.000.000 · 20) / (1.000 · 10) ≈ 2.000×`. Extrapolando a partir do tempo medido para `n=5.000` (~0,022 s), o D&C continuaria **viável**, na ordem de segundos a poucos minutos.
- **Conclusão:** apenas o Divide & Conquer escala para o cenário de 1 milhão de registros; a Força Bruta deixa de ser praticável bem antes disso (já em `n` da ordem de dezenas de milhares, no hardware usado nos testes).
