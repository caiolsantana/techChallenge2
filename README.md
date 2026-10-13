# Tech Challenge – Fase 2: Otimização de Rotas Médicas (VRP + Algoritmo Genético + LLM)

Sistema de otimização de rotas para distribuição de medicamentos e insumos entre unidades
hospitalares, usando um Algoritmo Genético para resolver um VRP (Vehicle Routing Problem) com
restrições realistas, e uma LLM para gerar instruções de entrega, relatórios e responder perguntas
em linguagem natural sobre as rotas. Desenvolvido como parte do Tech Challenge (Fase 2) da Pós-Tech
FIAP.

Veja o plano completo de execução em [PLANO.md](PLANO.md).

## 1. Sobre o projeto

O hospital enfrenta desafios logísticos na distribuição eficiente de medicamentos e insumos entre
suas unidades e para atendimento domiciliar. Este projeto resolve o problema do "caixeiro viajante
médico" (TSP/VRP) com múltiplos veículos, prioridades de entrega, capacidade de carga e autonomia,
e usa uma LLM para traduzir os resultados em instruções e relatórios acionáveis.

## 2. Código base

Ponto de partida fornecido pela FIAP: https://github.com/FIAP/genetic_algorithm_tsp — uma
implementação simples de Algoritmo Genético para TSP com visualização em Pygame. Uma cópia de
referência (não modificada) está em [base_code/](base_code/); o algoritmo evoluído para VRP vive em
`src/ga_vrp/`.

## 3. Estrutura do repositório

```
techChallenge2/
├── README.md                  # este arquivo
├── PLANO.md                   # plano de execução detalhado (fases, cronograma, papéis)
├── requirements.txt            # bibliotecas necessárias
├── relatorio_tecnico.md       # relatório técnico (preenchido na Fase 6)
├── .env.example                # variáveis de ambiente necessárias (chave da LLM)
├── base_code/                  # código base da FIAP, como referência (não modificado)
├── notebooks/                   # notebooks de demonstração
├── src/
│   ├── ga_vrp/                 # modelo de domínio + algoritmo genético para VRP
│   ├── data/                   # geração de cenários sintéticos
│   ├── visualization/          # gráficos de convergência e mapas de rotas
│   └── llm/                    # integração com a LLM (instruções, relatórios, Q&A)
├── tests/                       # testes automatizados (pytest)
├── data/                        # cenários gerados (config/saída)
└── results/
    └── figures/                 # gráficos e mapas gerados
```

## 4. Como executar

### Pré-requisitos
- Python 3.12 (ou 3.11+)

### Passo a passo

```bash
# 1. Clonar o repositório
git clone <URL_DO_SEU_REPOSITORIO>
cd techChallenge2

# 2. Criar e ativar um ambiente virtual
python3 -m venv venv
source venv/bin/activate        # Linux/Mac
# venv\Scripts\activate         # Windows

# 3. Instalar as dependências
pip install -r requirements.txt

# 4. Configurar a chave da LLM
cp .env.example .env
# edite .env e preencha GROQ_API_KEY (gratuita em https://console.groq.com/keys)
```

## 5. Arquitetura do Núcleo VRP-GA (`src/ga_vrp/`) — Fase 1, concluída por @caiolsantana

Esta seção documenta o que foi implementado na Fase 1, para quem for construir em cima dele nas
Fases 3-5 (@andersonmares: visualização, LLM, experimentos/testes).

### Ideia central
O algoritmo genético continua trabalhando exatamente como no código base da FIAP
(`base_code/genetic_algorithm.py`, **não modificado**): o cromossomo é **uma única lista com a
ordem de todos os pontos de entrega** (sem informação de veículo/rota embutida). O que torna isso um
VRP (múltiplos veículos, capacidade, autonomia) é uma função nova, `split.py`, que **decodifica**
essa lista em rotas por veículo. Isso permite reaproveitar quase sem alteração os operadores de
crossover e mutação do código base.

### Módulos (`src/ga_vrp/`)
| Arquivo | O que faz |
|---|---|
| `models.py` | Dataclasses: `DeliveryPoint`, `Vehicle`, `Depot`, `Route`, `Solution`, enum `Priority` (`CRITICAL`/`REGULAR`). |
| `geo.py` | Distância euclidiana entre dois pontos (plano x/y, não great-circle — suficiente para o cenário sintético). |
| `operators.py` | `generate_random_population`, `order_crossover` e `swap_mutate` — portados de `base_code/genetic_algorithm.py` adaptados para `DeliveryPoint`. Inclui também `inversion_mutate` (melhoria sobre o TODO do código base) e `roulette_wheel_selection` (seleção por `1/fitness`, igual ao `tsp.py` original). |
| `split.py` | `split_into_routes(giant_tour, vehicles, depot) -> Solution` — decodifica a permutação em rotas, respeitando capacidade e autonomia (algoritmo guloso sequencial; pontos que não cabem em nenhum veículo disponível viram `unrouted_points`, não travam a execução). |
| `fitness.py` | `evaluate(solution) -> float` = distância total + penalidade de prioridade (pontos `CRITICAL` atendidos tarde na rota) + penalidade alta por ponto não roteado. |
| `validators.py` | Funções puras `is_capacity_respected`, `is_autonomy_respected`, `all_points_visited_once` — prontas para a suíte pytest da Fase 5. |
| `ga.py` | `run_ga(delivery_points, vehicles, depot, config: GAConfig) -> GAResult` — o loop principal (elitismo + seleção + crossover + mutação, mesmo esqueleto do `tsp.py` original). `GAResult.best_fitness_history` é a lista de fitness por geração que a Fase 3 vai plotar no gráfico de convergência. |

### Como rodar a demo (sem esperar os dados reais da Fase 2)
```bash
python -m src.ga_vrp.ga
```
Isso roda um cenário fixo (8 pontos, 2 veículos, ver `_demo_scenario()` em `ga.py`) e imprime a
melhora do fitness geração a geração, as rotas finais e a carga/distância de cada veículo.

### Para integrar com a Fase 2 (dados sintéticos)
`run_ga()` só espera `list[DeliveryPoint]`, `list[Vehicle]` e um `Depot` — não importa como foram
gerados. Quando o gerador de cenários da Fase 2 estiver pronto, basta chamar
`run_ga(pontos_gerados, frota_gerada, deposito_gerado, GAConfig(...))` no lugar de
`_demo_scenario()`; nenhuma mudança é necessária em `split.py`, `fitness.py` ou `ga.py`.

### Para integrar com a Fase 3 (visualização) e Fase 4 (LLM)
- Gráfico de convergência: plotar `GAResult.best_fitness_history`.
- Mapa de rotas: `GAResult.best_solution.routes` — cada `Route` tem `vehicle`, `points` (em ordem de
  visita) e `distance`/`load` já calculados.
- Para a LLM gerar instruções/relatórios, a mesma estrutura `GAResult.best_solution` tem tudo que é
  necessário (rotas, pontos, prioridades, cargas) sem precisar tocar no GA.

### Decisões e limitações conhecidas (documentado para não serem "descobertas" depois)
- O split é guloso/sequencial (primeira opção que cabe), não o algoritmo ótimo de Prins
  (shortest-path sobre os cortes possíveis). Mais simples de manter; troca por uma versão ótima no
  futuro não exige mudar o resto do pipeline.
- Fila sem frota suficiente não trava o programa: os pontos que sobram viram `unrouted_points` e
  entram como penalidade alta na fitness (restrição soft, não hard-reject do indivíduo).
- `base_code/` não foi alterado — serve só de referência; todo o código de produção vive em
  `src/ga_vrp/`.

## 6. Status

Projeto em desenvolvimento — ver [PLANO.md](PLANO.md) para o cronograma e [PROGRESS.md](PROGRESS.md)
para o progresso atualizado por bloco de fases.
