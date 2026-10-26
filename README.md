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
├── docs/                        # notas de arquitetura/planejamento por fase (acompanhamento do grupo)
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

# 4. Configurar a chave da LLM, se for usar Groq
cp .env.example .env
# edite .env e preencha GROQ_API_KEY (gratuita em https://console.groq.com/keys)
```

### Fases 3 a 5

Execute os comandos abaixo na raiz do repositório, com o ambiente Python ativado:

```bash
# Gráfico de convergência e mapa interativo
python -m src.visualization

# Instruções, relatório ou pergunta sobre as rotas
python -m src.llm instructions
python -m src.llm report
python -m src.llm ask --question "Quais entregas são críticas?"

# Três configurações do GA, cada uma com três sementes, e baseline guloso
python -m src.experiments

# Testes
python -m pytest -q

# Coletar respostas reais da LLM para avaliação manual
python -m src.llm.evaluate
```

Para a LLM, o modo `auto` usa Groq quando `GROQ_API_KEY` está definida e tenta Ollama se
a chamada falhar. Sem chave, usa Ollama local. Se necessário, escolha explicitamente
`--provider groq` ou `--provider ollama`. Para Ollama, inicie o servidor local e baixe o modelo
indicado em `OLLAMA_MODEL`. A avaliação manual e seus critérios estão em
[docs/fase4-avaliacao-llm.md](docs/fase4-avaliacao-llm.md).

As visualizações são gravadas em `results/figures/` e os experimentos em
`results/experiments.json` e `results/experiments.csv`. As distâncias representam diferenças
euclidianas entre coordenadas de latitude/longitude; **não são quilômetros nem distâncias reais
de rua**. Veja a análise dos experimentos em [docs/fase5-experimentos.md](docs/fase5-experimentos.md).

Notas de arquitetura de cada fase (artefatos de acompanhamento do grupo, não fazem parte da entrega
final): ver [docs/](docs/).

## 5. Status

Projeto em desenvolvimento — ver [PLANO.md](PLANO.md) para o cronograma e [PROGRESS.md](PROGRESS.md)
para o progresso atualizado por bloco de fases. A integração LLM e os prompts estão implementados;
a avaliação de respostas reais requer uma chave Groq ou um servidor Ollama configurado.
