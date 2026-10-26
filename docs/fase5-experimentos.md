# Experimentos e comparação — Fase 5

## Método

O cenário fixo `data/scenarios/sp_default.json` tem 30 pontos de entrega e quatro veículos.
Cada configuração do GA rodou com sementes 42, 73 e 101, totalizando nove execuções. O baseline
é uma heurística de vizinho mais próximo, que escolhe a parada viável mais próxima para cada
veículo. Ambas as abordagens usam a mesma frota e respeitam capacidade e autonomia.

| Configuração | População | Gerações | Crossover | Mutação | Operador |
|---|---:|---:|---:|---:|---|
| `small_swap` | 40 | 50 | 0,6 | 0,1 | Troca adjacente |
| `medium_swap` | 70 | 80 | 0,8 | 0,3 | Troca adjacente |
| `large_inversion` | 100 | 100 | 1,0 | 0,5 | Inversão de trecho |

O fitness minimiza distância total + penalidade para entregas críticas tardias + penalidade
alta para pontos sem rota. As distâncias são unidades euclidianas de latitude/longitude, não km.
Os tempos de execução dependem do computador. As métricas completas por semente estão em
`results/experiments.json` e `results/experiments.csv`. `convergence_generation` indica a
primeira geração em que o melhor fitness final já havia sido alcançado.

## Resultados

| Método | Fitness médio | Distância média | Pontos sem rota |
|---|---:|---:|---:|
| Vizinho mais próximo | 264,69 | 2,31 | 0 |
| `small_swap` | 51,92 | 4,63 | 0 |
| `medium_swap` | 52,09 | 4,37 | 0 |
| `large_inversion` | 58,72 | 4,90 | 0 |

Todos os nove resultados do GA e o baseline contabilizaram os 30 pontos sem violações de
capacidade ou autonomia. O GA reduziu o fitness em aproximadamente 78% a 80% contra o baseline,
porque a função objetivo dá peso às entregas críticas no início das rotas. O baseline percorreu
menos distância; portanto, o resultado não deve ser descrito como economia de quilômetros.
As três variantes do GA têm médias próximas, e três sementes são insuficientes para afirmar
que uma delas é consistentemente superior.

## Reproduzir

```bash
python -m src.experiments
python -m pytest -q
```
