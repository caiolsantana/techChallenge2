# Avaliação da camada LLM — Fase 4

## Casos de uso e execução

O comando `python -m src.llm.evaluate` gera a solução com o cenário padrão e semente 42,
envia três pedidos ao provedor escolhido e salva `results/llm-evaluation.json`:

1. Instruções por veículo, com ordem das paradas e prioridade.
2. Relatório operacional com rotas, cargas, distâncias e pontos sem rota.
3. Pergunta: “Quais são as entregas críticas e em que ordem serão atendidas?”

O comando cria notas `null` para revisão posterior. Cada arquivo de avaliação inclui uma
referência estruturada extraída de `GAResult.best_solution` (IDs na ordem, pontos críticos,
totais e pontos sem rota). Testes com provedor falso verificam o fluxo; as notas abaixo foram
atribuídas às respostas reais do Ollama após comparação com essa referência.

## Rubrica (0 a 2 por dimensão, por resposta)

| Dimensão | 0 | 1 | 2 |
|---|---|---|---|
| Correção factual | Inventa ou contradiz rotas, prioridades ou números | Pequenas omissões ou imprecisões | Todos os fatos citados conferem com a solução |
| Clareza | Instruções confusas ou ambíguas | Compreensível com ajustes | Clara, ordenada e fácil de seguir |
| Utilidade | Não ajuda o operador | Ajuda parcialmente | Atende ao caso de uso com detalhes necessários |

Registre em `review_notes` cada erro ou omissão, em especial: parada fora da ordem, prioridade
incorreta, ponto não roteado omitido, distância chamada de quilômetros, horário ou economia
inventados. Uma resposta boa deve declarar quando os dados não permitem calcular tempo de
viagem, distância rodoviária ou economia operacional.

## Resultado com Llama 3.1 local

Modelo: `llama3.1:latest` (8B, quantização Q4_K_M). Cenário: `sp_default.json`, 30 pontos,
quatro veículos; semente 42 e configuração padrão do GA. A solução usou três veículos com
10, 13 e 7 paradas, 82,34 unidades de carga, distância total 3,605366 unidades de coordenada,
nove pontos críticos e nenhum ponto sem rota.

| Caso | Primeira rodada | Após revisão dos prompts | Evidência principal |
|---|---:|---:|---|
| Instruções | 5/6 | 6/6 | 30 IDs e ordem por veículo conferidos; primeira resposta afirmou destaque em negrito sem aplicá-lo |
| Relatório | 3/6 | 6/6 | Primeira resposta disse “10 por veículo”; segunda informou 10/13/7 e os totais corretos |
| Perguntas | 1/6 | 6/6 | Primeira resposta omitiu dois críticos e incluiu quatro regulares; segunda listou os nove críticos com veículo e ordem |
| **Total** | **9/18** | **18/18** | Conferência técnica com a solução estruturada do GA |

A revisão dos prompts passou a enviar contagens e totais já calculados ao pedido de relatório
e uma lista exclusiva de pontos críticos ao pedido correspondente. As respostas e notas por
dimensão estão em `results/llm-evaluation-initial.json` e `results/llm-evaluation.json`.

Este é um teste de um cenário com uma execução por versão do prompt. O resultado demonstra que
o modelo pode seguir os dados nesse caso, mas a primeira rodada mostrou que também pode
confundir fatos. As coordenadas são sintéticas; as instruções não equivalem a navegação real.

Referências das interfaces usadas: [Ollama Chat API](https://docs.ollama.com/api/chat).
