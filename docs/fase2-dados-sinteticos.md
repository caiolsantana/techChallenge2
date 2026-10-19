# Gerador de Dados Sintéticos (`src/data/`) — Fase 2

> Nota de planejamento/acompanhamento do grupo — não é parte do relatório técnico final. Pode ser
> removido ou incorporado ao relatório na limpeza pré-entrega (ver [PLANO.md](../PLANO.md)).

Documenta o que foi implementado na Fase 2, complementando [fase1-nucleo-vrp-ga.md](fase1-nucleo-vrp-ga.md):
agora `run_ga()` (Fase 1) pode receber cenários gerados automaticamente em vez do
`_demo_scenario()` hardcoded, prontos para @andersonmares plugar nas Fases 3-5
(visualização, LLM, experimentos).

## Ideia central
Um cenário é só os três argumentos que `run_ga()` já esperava (`Depot`, `list[DeliveryPoint]`,
`list[Vehicle]`), gerados aleatoriamente a partir de uma `ScenarioConfig` parametrizável
(YAML/JSON) em vez de escritos à mão. Nenhum módulo da Fase 1 (`models.py`, `split.py`,
`fitness.py`, `ga.py`) precisou mudar — o gerador só produz instâncias desses mesmos tipos.

## Módulos (`src/data/`)
| Arquivo | O que faz |
|---|---|
| `scenario.py` | `ScenarioConfig` (seed, nº de pontos, nº de veículos, faixa de demanda, bounding box etc.), `generate_scenario(config) -> GeneratedScenario`, `load_config`/`save_scenario`/`load_scenario` (serialização YAML de entrada / JSON de saída), e um CLI (`python -m src.data.scenario`). |

## Como rodar a demo
```bash
python -m src.data.scenario --config data/config/scenario_default.yaml --output data/scenarios/sp_default.json
```
Sem argumentos, usa esses mesmos caminhos como padrão. Imprime um resumo (nº de pontos, nº
críticos, frota) e salva o cenário gerado como JSON.

## Cenário gerado
- **Coordenadas**: pontos aleatórios dentro de um bounding box no formato/escala da Região
  Metropolitana de São Paulo (`SAO_PAULO_BBOX` em `scenario.py`), não endereços geocodificados
  reais — consistente com a distância euclidiana (não great-circle) já usada em `geo.py`.
- **Depósito**: fixo por padrão nas coordenadas da Praça da Sé (centro da cidade), configurável via
  `depot_lat`/`depot_lon`.
- **Prioridade**: cada ponto é `CRITICAL` com probabilidade `critical_ratio` (padrão 30%), senão
  `REGULAR`.
- **Demanda**: uniforme entre `demand_min` e `demand_max` por ponto.
- **Frota**: capacidade e autonomia (`max_range`) de cada veículo são, por padrão (quando não
  fixadas explicitamente na config), **calculadas automaticamente** a partir de `n_points`,
  `n_vehicles` e da faixa de demanda — ver `_resolve_vehicle_bounds()` em `scenario.py`:
  - Capacidade alvo = demanda média esperada por veículo (demanda total esperada / nº de veículos),
    com margem de 1.1x-1.6x para o GA ter espaço de explorar divisões desiguais.
  - Autonomia alvo = distância esperada de uma rota com `n_points / n_vehicles` paradas em ordem
    aleatória (~metade da diagonal do bounding box por salto), com margem de 1.3x-2.0x.
  - Isso evita cenários acidentalmente inviáveis (frota pequena demais para a área/demanda) ao
    variar o tamanho do problema nos experimentos da Fase 5 — ver "Decisões e limitações" abaixo.

## Arquivos de configuração e saída
- `data/config/scenario_default.yaml` — config padrão (comentada), ponto de partida para variações
  usadas nos 3+ experimentos da Fase 5 (basta copiar e mudar `n_points`, `n_vehicles`,
  `critical_ratio` etc.).
- `data/scenarios/sp_default.json` — cenário de exemplo já gerado e commitado (saída do comando
  acima com a config padrão), para quem quiser inspecionar o formato sem rodar nada.

## Como rodar o GA com um cenário gerado
```python
from src.data.scenario import generate_scenario, load_scenario
from src.ga_vrp.ga import run_ga, GAConfig

# opção 1: gerar na hora
scenario = generate_scenario()  # ou generate_scenario(ScenarioConfig(n_points=50, ...))
# opção 2: carregar um cenário já salvo (reprodutível, mesmo JSON entre execuções)
scenario = load_scenario("data/scenarios/sp_default.json")

result = run_ga(scenario.delivery_points, scenario.vehicles, scenario.depot, GAConfig())
```

## Validação de viabilidade
Testado manualmente rodando `run_ga()` sobre cenários gerados com sementes e tamanhos
(`n_points`/`n_vehicles`) diferentes: 0 pontos não roteados (`unrouted_points`) em todos os casos
após o ajuste de `_resolve_vehicle_bounds()` (antes dele, cenários com frota maior/menor que o
padrão (30 pontos / 4 veículos) ficavam inviáveis — capacidade e autonomia fixas não escalavam com
o tamanho do problema).

## Decisões e limitações conhecidas (documentado para não serem "descobertas" depois)
- Autonomia/capacidade calculadas automaticamente são uma **estimativa heurística**, não uma
  garantia formal de viabilidade (o split ainda é guloso/sequencial, Fase 1) — cenários muito
  desbalanceados (ex.: `critical_ratio` ou faixa de demanda extremas) ainda podem gerar alguns
  `unrouted_points`; isso é esperado e tratado como penalidade soft pela fitness (Fase 1), não como
  erro do gerador.
- Coordenadas são uniformemente aleatórias no bounding box, sem simular densidade populacional real
  (bairros mais densos vs. periferia) — suficiente para o escopo sintético do projeto.
- `n_vehicles` gera exatamente essa quantidade de veículos "genéricos" (capacidade/autonomia
  sorteadas dentro de uma faixa); não há tipos de frota distintos (ex. moto vs. van) nesta versão.
- Config aceita YAML (`.yaml`/`.yml`) ou JSON (`.json`) de entrada; a saída salva é sempre JSON
  (mais simples de versionar/inspecionar e de recarregar com `load_scenario`).
