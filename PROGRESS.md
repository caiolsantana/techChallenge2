# Progresso — Tech Challenge Fase 2

> Atualize este arquivo (marcar `[x]`, mudar status, adicionar nota) sempre que concluir uma tarefa
> e suba num commit/PR. Plano completo em [PLANO.md](PLANO.md).

Legenda de status: `A fazer` · `Em andamento` · `Concluído` · `Bloqueado`

## Bloco 1 — @caiolsantana (Fases 0, 1 e 2)

| Status | Tarefa |
|---|---|
| Concluído | Fase 0.1 — Estrutura do projeto (venv, requirements.txt, pastas `src/`) |
| Concluído | Fase 0.2 — Importar código base da FIAP para `base_code/` |
| Concluído | Fase 1.4 — Modelar domínio (`DeliveryPoint`, `Vehicle`, `Depot`) — ver `src/ga_vrp/models.py` |
| Concluído | Fase 1.5 — Representação genética de rotas por veículo — giant tour + `split.py` (ver README §5) |
| Concluído | Fase 1.6 — Operadores especializados (seleção, crossover, mutação) — `src/ga_vrp/operators.py` |
| Concluído | Fase 1.7 — Função fitness multi-critério — `src/ga_vrp/fitness.py` |
| Concluído | Fase 1.8 — Validador de restrições (capacidade, autonomia, prioridade) — `src/ga_vrp/validators.py` |
| Concluído | Fase 2.9 — Gerador de dados sintéticos (cenário estilo São Paulo) — ver `src/data/scenario.py` |

## Bloco 2 — @andersonmares (Fases 3, 4 e 5)

| Status | Tarefa |
|---|---|
| Concluído | Fase 3.10 — Gráfico de convergência do GA (Matplotlib) |
| Concluído | Fase 3.11 — Mapa interativo das rotas (Folium) |
| Concluído | Fase 4.12 — Provedor LLM (Groq + fallback Ollama); falta validar chamada real com credencial/servidor |
| Concluído | Fase 4.13 — Prompts para instruções, relatórios e Q&A |
| Concluído | Fase 4.14 — Três respostas reais do Ollama avaliadas e comparadas com a solução do GA |
| Concluído | Fase 5.15 — 3 configurações × 3 sementes, resultados em `results/experiments.*` |
| Concluído | Fase 5.16 — Baseline nearest-neighbor e comparação de distância/fitness |
| Concluído | Fase 5.17 — Testes automatizados (pytest) |

## Bloco 3 — @gabrielle19 (Fases 6, 7 e 8)

| Status | Tarefa |
|---|---|
| A fazer | Fase 6.18 — README final (como rodar, estrutura) |
| A fazer | Fase 6.19 — Diagrama de arquitetura |
| A fazer | Fase 6.20 — Relatório técnico (5 tópicos do enunciado) |
| A fazer | Fase 7.21 — Roteiro do vídeo (≤15 min) |
| A fazer | Fase 7.22 — Gravação e upload do vídeo |
| A fazer | Fase 8.23 — Revisão cruzada entre os 3 integrantes |
| A fazer | Fase 8.24 — Ajustes finais e submissão |

## Log de atualizações

<!-- Adicione uma linha por atualização relevante, mais recente no topo. -->
- 2026-10-25 — @andersonmares — Llama 3.1 local (`llama3.1:latest`) usado para validar os três
  casos da Fase 4. A primeira rodada revelou erros no relatório e no Q&A; prompts revisados
  e segunda rodada conferida com os 30 pontos e nove críticos da solução do GA. Registros,
  notas e limitações em [docs/fase4-avaliacao-llm.md](docs/fase4-avaliacao-llm.md).
- 2026-10-25 — @andersonmares — Fases 3 e 5 implementadas: visualizações em `src/visualization/`,
  nove execuções reproduzíveis e baseline em `src/experiments/`, testes em `tests/`. Fase 4:
  provedores e prompts implementados, com protocolo de avaliação documentado; execução de
  respostas reais pendente de credencial Groq ou servidor Ollama. Detalhes em
  [docs/fase4-avaliacao-llm.md](docs/fase4-avaliacao-llm.md) e
  [docs/fase5-experimentos.md](docs/fase5-experimentos.md).
- 2026-10-19 — @caiolsantana — Fase 2 concluída: gerador de dados sintéticos em `src/data/scenario.py`
  (`ScenarioConfig`, `generate_scenario`, `load_config`/`save_scenario`/`load_scenario`, CLI via
  `python -m src.data.scenario`). Cenário no formato/escala de São Paulo (bounding box de lat/lon,
  depósito na Praça da Sé), com prioridades, demandas e frota geradas aleatoriamente; capacidade e
  autonomia dos veículos são auto-dimensionadas a partir de `n_points`/`n_vehicles`/demanda para o
  cenário permanecer viável em qualquer tamanho (validado rodando `run_ga()` com várias sementes e
  tamanhos: 0 pontos não roteados). Config padrão em `data/config/scenario_default.yaml` e cenário de
  exemplo commitado em `data/scenarios/sp_default.json`. Nenhum módulo da Fase 1 precisou mudar —
  `generate_scenario()` produz exatamente os tipos que `run_ga()` já esperava. Detalhes em
  [docs/fase2-dados-sinteticos.md](docs/fase2-dados-sinteticos.md).
- 2026-10-13 — @caiolsantana — Fase 1 concluída: núcleo VRP-GA implementado em `src/ga_vrp/`
  (`models.py`, `geo.py`, `operators.py`, `split.py`, `fitness.py`, `validators.py`, `ga.py`).
  Demo validada via `python -m src.ga_vrp.ga`: fitness melhora ao longo das gerações, 0 pontos não
  roteados, capacidade/autonomia respeitadas (checado com `validators.py`), pontos `CRITICAL`
  priorizados no início das rotas. `base_code/` continua intocado. Detalhes de arquitetura e como
  plugar a Fase 2 estão em [docs/fase1-nucleo-vrp-ga.md](docs/fase1-nucleo-vrp-ga.md).
- 2026-10-13 — @caiolsantana — Setup do repositório, scaffolding do projeto e tracker de progresso criados.
