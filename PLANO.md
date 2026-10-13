# Plano: Tech Challenge Fase 2 — Projeto 2 (Otimização de Rotas Médicas, GA + LLM)

## Contexto
- Pós-graduação, Tech Challenge Fase 2, Projeto 2: otimização de rotas para distribuição de
  medicamentos e insumos (TSP/VRP) com Algoritmo Genético + LLM para instruções/relatórios.
- Grupo de 3 pessoas. Prazo: 03/11/2026 (~25 dias a partir de 09/10/2026).
- Código base fornecido: https://github.com/FIAP/genetic_algorithm_tsp
  - Arquivos: `genetic_algorithm.py` (GA core: população, fitness, crossover, mutação, ordenação),
    `tsp.py` (loop principal + visualização Pygame), `draw_functions.py` (desenho Pygame),
    `benchmark_att48.py`, `demo_crossover.py`, `demo_mutation.py`.
  - Dependência única: Pygame. Sem testes, sem VRP, sem restrições, sem LLM.

## Decisões tomadas
- Sem implementação em nuvem/IaC — foco só no núcleo obrigatório.
- Dados sintéticos, no formato/escala de São Paulo (sem geocoding real nem endereços reais).
- LLM: **Groq API** (tier gratuito, modelos Llama 3.x) como provedor principal, com **Ollama** local
  como fallback offline caso o tier gratuito seja insuficiente.
- Repositório novo e separado (este, `posfiap/techChallenge2`).

## Visão geral da solução

Transformar o TSP solver (Pygame) do código base da FIAP em um sistema de **VRP (Vehicle Routing
Problem)** com algoritmo genético, restrições realistas (prioridade, capacidade, autonomia, múltiplos
veículos), visualização em mapa (Folium/Plotly) e camada de LLM para gerar instruções de entrega,
relatórios periódicos e responder perguntas em linguagem natural sobre as rotas.

**Stack recomendada:** Python 3.11+, Poetry, GA próprio (reaproveitando a lógica do código base),
Folium + Matplotlib para visualização, Groq API para a camada de LLM (fallback Ollama local), pytest
para testes.

## Divisão de papéis

RESOLVIDO (divisão por blocos de fases, não por tipo de trabalho):
- **@caiolsantana — Fases 0, 1 e 2:** setup do projeto, núcleo VRP-GA (modelo de domínio,
  representação genética, operadores, fitness multi-critério, validador de restrições) e gerador de
  dados sintéticos.
- **@andersonmares — Fases 3, 4 e 5:** visualização (gráfico de convergência + mapa interativo),
  integração com LLM (Groq/Ollama, prompts, avaliação de qualidade) e experimentos/testes
  automatizados.
- **@gabrielle19 — Fases 6, 7 e 8:** documentação (README, diagrama de arquitetura, relatório
  técnico), roteiro e gravação do vídeo de demonstração, revisão cruzada e entrega final.
- Todos os três participam do relatório técnico (cada um escreve a seção da sua frente) e aparecem no
  vídeo explicando sua parte.
- Acompanhamento do progresso: ver [PROGRESS.md](PROGRESS.md).

## Fases e cronograma (25 dias, 09/10/2026 → 03/11/2026)

### Fase 0 — Setup (dias 1-2, até 11/10)
1. Criar estrutura do projeto (Poetry, `pyproject.toml`, `.gitignore`, pastas:
   `src/ga_vrp/` para o algoritmo, `src/data/` para geração sintética, `src/visualization/`,
   `src/llm/`, `tests/`, `notebooks/` para demos, `docs/`).
2. Importar e revisar o código base da FIAP (`genetic_algorithm.py`, `tsp.py`,
   `draw_functions.py`) como ponto de partida; manter Pygame só para demo opcional ao vivo, e migrar
   a visualização "oficial" do relatório para Folium/Matplotlib (mapas e gráficos estáticos são mais
   adequados ao relatório/vídeo do que uma janela Pygame).

### Fase 1 — Núcleo VRP-GA (dias 3-8, até 17/10) — depende da Fase 0
4. Modelar o domínio: `DeliveryPoint` (id, coordenadas, prioridade, demanda), `Vehicle` (capacidade,
   autonomia/alcance máximo), `Depot` (ponto de origem/hospital central).
5. Adaptar a representação genética do código base de "permutação de cidades" para "conjunto de
   rotas por veículo" (particionamento de pontos entre veículos + ordem dentro de cada rota).
6. Implementar operadores especializados: crossover que preserva viabilidade de rotas (ex.: Order
   Crossover por rota), mutação (swap/inversion dentro e entre rotas), seleção (torneio/roleta,
   reaproveitando `genetic_algorithm.py` como base).
7. Função fitness multi-critério: distância total + penalidade por violar capacidade/autonomia +
   bônus/penalidade por atraso em entregas prioritárias.
8. Validador de restrições (capacidade do veículo, autonomia máxima, prioridade) como função pura,
   testável isoladamente.

### Fase 2 — Dados sintéticos (dias 4-8, paralelo à Fase 1)
9. Gerador de cenário: N unidades hospitalares + M pontos de entrega com coordenadas (lat/long
   plausíveis dentro do bounding box de São Paulo), prioridades (crítico/regular), demandas, e frota
   de veículos com capacidade/autonomia variadas. Parametrizável via arquivo de config (YAML/JSON)
   para facilitar os 3+ experimentos.

### Fase 3 — Visualização (dias 9-13, até 22/10) — depende das Fases 1 e 2
10. Gráfico de convergência do GA (fitness por geração) com Matplotlib.
11. Mapa interativo das rotas otimizadas por veículo (Folium, uma cor por veículo, marcadores de
    prioridade) exportável como HTML para o repositório/vídeo.

### Fase 4 — Integração LLM (dias 10-16, até 25/10) — pode iniciar em paralelo à Fase 3, depende dos dados de saída do GA (Fase 1)
12. Provedor: **Groq API** (gratuito, modelos Llama 3.x, latência baixa) como principal; alternativa
    100% offline/sem limite de cota: **Ollama** local (ex.: `llama3.1`) como fallback caso o tier
    gratuito da Groq seja insuficiente durante testes/gravação do vídeo. Chave de API via variável de
    ambiente (nunca hardcoded).
13. Prompt engineering para 3 casos de uso: (a) gerar instruções de entrega por rota/motorista a
    partir do resultado do GA, (b) gerar relatório periódico (distância total, tempo estimado,
    economia vs. baseline), (c) responder perguntas livres sobre as rotas (Q&A simples via contexto
    injetado — não precisa de RAG/vector DB, dado o escopo).
14. Avaliação da qualidade das respostas (rubrica simples: clareza, correção factual vs. dados reais
    do GA, utilidade) documentada no relatório técnico.

### Fase 5 — Experimentos e testes (dias 14-19, até 28/10) — depende da Fase 1
15. Rodar os 3+ experimentos obrigatórios variando parâmetros do GA (tamanho de população, taxa de
    mutação, taxa de crossover, nº de gerações) e registrar métricas (distância total, tempo de
    convergência, violações de restrição).
16. Comparar contra baseline simples (nearest-neighbor / heurística gulosa) para evidenciar o ganho do
    GA, conforme pedido no enunciado ("comparativo de desempenho com outras abordagens").
17. Testes automatizados (pytest) para: operadores genéticos, função fitness, validador de
    restrições, gerador de dados sintéticos — mock de chamadas à LLM nos testes (sem custo/API real).

### Fase 6 — Documentação (dias 18-22, até 30/10) — depende das Fases 1-5
18. README do repositório: como rodar, estrutura do projeto, ambiente virtual (Poetry).
19. Diagrama de arquitetura (Mermaid exportado para imagem, ou draw.io) mostrando o fluxo: Gerador
    de Dados → Motor GA/VRP → Resultados → Visualização + Camada LLM.
20. Relatório técnico (seguindo exatamente a lista de tópicos exigida no enunciado para o Projeto 2:
    implementação do GA a partir do código base, estratégias para restrições, integração com LLM,
    comparativo de desempenho, visualizações/análises).

### Fase 7 — Vídeo (dias 21-24, até 01/11) — depende de tudo funcionando (Fases 1-4)
21. Roteiro (≤15 min): demo do sistema rodando, explicação dos componentes, resultados do GA,
    demonstração da integração LLM — cada integrante narra sua parte.
22. Gravação e upload (YouTube/Vimeo, não listado).

### Fase 8 — Buffer e entrega final (dias 23-25, até 03/11)
23. Revisão cruzada entre os 3 integrantes (ler relatório, rodar o código do zero, assistir vídeo).
24. Ajustes finais e submissão (link do repo + relatório + vídeo).

## Entregáveis mapeados aos requisitos do enunciado
- Repositório Git completo (código, docs, notebooks/scripts de demo) — Fases 0-6.
- Relatório técnico com os 5 tópicos exigidos para o Projeto 2 — Fase 6.
- Vídeo de demonstração ≤15 min — Fase 7.
- Sem implementação em nuvem (decisão do grupo) — a seção "Arquitetura da solução" do relatório pode
  mencionar brevemente por que ficou fora do escopo (tempo/prioridade), sem necessidade de IaC.
