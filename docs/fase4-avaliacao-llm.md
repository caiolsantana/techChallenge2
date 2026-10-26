# Avaliação da camada LLM — Fase 4

## Casos de uso e execução

O comando `python -m src.llm.evaluate` gera a solução com o cenário padrão e semente 42,
envia três pedidos ao provedor escolhido e salva `results/llm-evaluation.json`:

1. Instruções por veículo, com ordem das paradas e prioridade.
2. Relatório operacional com rotas, cargas, distâncias e pontos sem rota.
3. Pergunta: “Quais são as entregas críticas e em que ordem serão atendidas?”

O arquivo deixa as notas de avaliação como `null`, para preenchimento por uma pessoa após
comparar cada resposta com `GAResult.best_solution`. Uma chamada real ao provedor é necessária;
teste com um provedor falso verifica o fluxo do código, mas não mede a qualidade da LLM.

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

## Estado da avaliação

O código, os prompts e a rubrica estão prontos. Nesta execução não havia `GROQ_API_KEY` nem
servidor Ollama local; por isso ainda não há respostas reais nem notas de qualidade. Complete
a avaliação após configurar um dos provedores e inclua as três notas e observações no relatório
técnico final.

Referências das interfaces usadas: [Groq Chat Completions](https://console.groq.com/docs/api-reference)
e [Ollama Chat API](https://docs.ollama.com/api/chat).
