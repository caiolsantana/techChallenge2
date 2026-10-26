# Relatório Técnico — Tech Challenge Fase 2
## Otimização de Rotas para Distribuição de Medicamentos e Insumos (VRP + GA + LLM)

> Rascunho inicial — seções a preencher na Fase 6 (ver [PLANO.md](PLANO.md)).

---

## 1. Implementação do algoritmo genético para roteamento a partir do código base fornecido

<!-- Representação genética, operadores (seleção, crossover, mutação), função fitness. -->

## 2. Estratégias para lidar com restrições adicionais

<!-- Prioridades de entrega, capacidade de carga, autonomia dos veículos, múltiplos veículos. -->

## 3. Integração com LLMs para geração de instruções e relatórios

O módulo `src/llm/` oferece três funções: instruções de entrega por veículo, relatório
operacional e perguntas sobre as rotas. Os prompts recebem somente os dados estruturados de
`GAResult.best_solution`, incluindo ordem das paradas, prioridades, carga, distância e pontos
sem rota. O prompt de sistema proíbe inferir endereços, tempos de viagem, quilômetros ou
economia sem dados correspondentes. A Groq API é o provedor principal quando há
`GROQ_API_KEY`; o Ollama local funciona como alternativa e fallback. A rubrica de avaliação
considera correção factual, clareza e utilidade (0 a 2 em cada dimensão), conforme
[`docs/fase4-avaliacao-llm.md`](docs/fase4-avaliacao-llm.md). A avaliação com respostas reais
depende de configurar um dos provedores; ainda não há resultados de qualidade a reportar.

## 4. Comparativo de desempenho com outras abordagens de roteamento

Foram executadas três configurações do GA com três sementes cada, sobre o mesmo cenário de
30 pontos e quatro veículos, e comparadas a uma heurística gulosa de vizinho mais próximo.
Todas as soluções visitaram os 30 pontos sem violar capacidade ou autonomia. O baseline teve
distância 2,31 e fitness 264,69; as variantes do GA tiveram fitness médio entre 51,92 e 58,72,
porém distância média maior (4,37 a 4,90). A função objetivo do GA penaliza a entrega tardia
de itens críticos, o que explica o menor fitness apesar da maior distância. Esses valores
estão em unidades euclidianas das coordenadas e não representam quilômetros reais.
Configurações, resultados por semente e limitações estão em
[`docs/fase5-experimentos.md`](docs/fase5-experimentos.md).

## 5. Visualizações e análises das rotas otimizadas

O gráfico `results/figures/convergence.png` mostra o melhor fitness de cada geração do GA.
O mapa interativo `results/figures/routes.html` desenha uma cor por veículo, a ordem das
paradas, destaque para entregas críticas e marcadores para pontos sem rota. Os arquivos são
gerados com `python -m src.visualization` a partir do cenário JSON versionado.
