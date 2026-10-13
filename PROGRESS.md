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
| A fazer | Fase 2.9 — Gerador de dados sintéticos (cenário estilo São Paulo) |

## Bloco 2 — @andersonmares (Fases 3, 4 e 5)

| Status | Tarefa |
|---|---|
| A fazer | Fase 3.10 — Gráfico de convergência do GA (Matplotlib) |
| A fazer | Fase 3.11 — Mapa interativo das rotas (Folium) |
| A fazer | Fase 4.12 — Configurar provedor LLM (Groq + fallback Ollama) |
| A fazer | Fase 4.13 — Prompt engineering (instruções, relatórios, Q&A) |
| A fazer | Fase 4.14 — Avaliação da qualidade das respostas da LLM |
| A fazer | Fase 5.15 — Rodar 3+ experimentos do GA com configs diferentes |
| A fazer | Fase 5.16 — Comparar com baseline (nearest-neighbor/guloso) |
| A fazer | Fase 5.17 — Testes automatizados (pytest) |

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
- 2026-10-13 — @caiolsantana — Fase 1 concluída: núcleo VRP-GA implementado em `src/ga_vrp/`
  (`models.py`, `geo.py`, `operators.py`, `split.py`, `fitness.py`, `validators.py`, `ga.py`).
  Demo validada via `python -m src.ga_vrp.ga`: fitness melhora ao longo das gerações, 0 pontos não
  roteados, capacidade/autonomia respeitadas (checado com `validators.py`), pontos `CRITICAL`
  priorizados no início das rotas. `base_code/` continua intocado. Detalhes de arquitetura e como
  plugar a Fase 2 estão no [README.md](README.md#5-arquitetura-do-núcleo-vrp-ga-src_ga_vrp---fase-1-concluída-por-caiolsantana).
- 2026-10-13 — @caiolsantana — Setup do repositório, scaffolding do projeto e tracker de progresso criados.
