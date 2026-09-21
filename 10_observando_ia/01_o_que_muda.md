# O que muda quando a aplicação chama um LLM

Agente é software. Roda em servidor, atende requisição, tem latência, tem erro, tem custo. Tudo que vimos até aqui continua valendo — e é por isso que este módulo vem no fim, e não no começo: sem os oito módulos anteriores, nada aqui faria sentido.

Mas quatro coisas mudam o suficiente para merecerem um módulo próprio.

## 1. A latência não tem "normal"

Num webserver, o tempo de resposta gira em torno de um valor. Você olha o p95, define um SLO e pronto.

Numa chamada de LLM a distribuição é outra: a maioria responde rápido e uma minoria demora muito, porque o tempo depende de quantos tokens o modelo resolveu gerar. A mesma pergunta, feita duas vezes, pode levar 800ms e 12 segundos.

Isso tem uma consequência prática imediata: **média aqui é inútil.** Se o p50 é 1s e o p99 é 30s, a média fica em algum lugar no meio, descrevendo uma requisição que não existe. Você precisa de percentil, e portanto de histograma.

E tem uma consequência menos óbvia nos **buckets**. Os buckets default do `prometheus_client` vão até 10 segundos. Se a sua cauda mora em 30s, todo mundo acima de 10s cai no bucket `+Inf` e o seu p99 vira chute. Por isso o app do lab define buckets até 60s na mão:

```python
buckets=(0.1, 0.25, 0.5, 1, 2, 4, 8, 15, 30, 60)
```

Se você só lembrar de uma coisa deste capítulo, lembre dessa.

## 2. Cada requisição custa dinheiro, e o valor varia

Um endpoint HTTP comum custa aproximadamente o mesmo toda vez. Uma chamada de LLM custa proporcionalmente aos tokens — e o número de tokens varia por requisição.

Isso muda o que é um incidente. Um bug que faz o sistema mandar o dobro de contexto em cada chamada não derruba nada: a latência continua aceitável, a taxa de erro continua zero, os dashboards continuam verdes. Você descobre no fim do mês, na fatura.

Custo, aqui, é sinal de produção. Não é assunto do financeiro — é métrica, com alerta, como saturação de disco. E olha que conveniente: nós já temos a ferramenta certa para "isso vai virar problema em algumas horas". É o `predict_linear` do [módulo 06](../06_alerting/02_predict_linear.md), aplicado a dinheiro em vez de disco.

## 3. Falhas que retornam 200

Esta é a diferença mais desconfortável.

No resto do curso, erro tem código. 500, 503, `up == 0`. Você conta, divide pelo total, tem a taxa de erro.

Um modelo pode devolver **200 com a resposta errada**. Inventar um número, ignorar metade da pergunta, responder em outro idioma, alucinar uma citação. Para o Prometheus isso é uma requisição bem-sucedida de 1,2 segundo. Todos os gráficos ficam verdes enquanto o produto entrega lixo.

Vale ser honesto sobre o limite: **métrica não resolve isso.** Prometheus mede o que é numérico e agregável; "a resposta está certa?" não é. O que dá para fazer é medir os *proxies* que costumam andar junto:

- resposta vazia ou absurdamente curta
- resposta que não passou na validação de schema, quando você pede saída estruturada
- o usuário reformulou a pergunta logo depois (sinal de que a primeira resposta não serviu)
- o usuário abandonou a conversa
- taxa de retry no seu lado da aplicação

Nenhum desses mede qualidade. Todos eles mexem quando a qualidade cai. É o mesmo raciocínio do [alertando nos sintomas](../09_conclusion/02_alerting_on_symptoms.md): você não mede a causa, mede o que o usuário sente.

Para medir qualidade de verdade existe avaliação offline — conjunto de testes, LLM como juiz, revisão humana por amostragem. Isso é outro assunto, roda fora do caminho da requisição, e não é Prometheus.

## 4. Tokens são a unidade de trabalho

No módulo 09 falamos dos quatro sinais de ouro: latência, tráfego, erros e saturação. Eles continuam valendo, mas **tráfego** ganha uma segunda dimensão.

Requisições por segundo já não descrevem a carga. Dez requisições com 200 tokens e dez com 50 mil tokens são o mesmo tráfego no gráfico e coisas completamente diferentes para o seu custo, para a sua latência e para o seu limite de quota.

Então: conte requisições **e** conte tokens. Separando entrada de saída, porque têm preços diferentes — saída costuma custar várias vezes mais que entrada.

## Traduzindo para os quatro sinais

| Sinal | Num serviço comum | Numa aplicação com LLM |
|---|---|---|
| Latência | p95 do tempo de resposta | p95 **e** p99 — a cauda é o que dói. Se você faz streaming, também o tempo até o primeiro token |
| Tráfego | requisições/s | requisições/s **e** tokens/min, entrada e saída separados |
| Erros | taxa de 5xx | erros por tipo (rate limit ≠ timeout ≠ erro de conteúdo) **e** proxies de qualidade |
| Saturação | CPU, memória, disco | quota e rate limit do provider, chamadas em andamento, tamanho da fila |
| *(novo)* Custo | — | dólares por hora, e a projeção para o fim do dia |

## O lab

O módulo tem uma aplicação FastAPI instrumentada, que sobe junto com o resto:

```
make up
```

Ela está em [`labs/llm-app/`](../labs/llm-app/) e, por padrão, usa um provider **simulado** — não precisa de chave de API nenhuma. O simulador gera latência de cauda longa, contagem de tokens e falhas plausíveis, que é exatamente o que precisamos para ver os gráficos se mexerem.

```
curl -s -X POST localhost:8000/ask \
  -H 'content-type: application/json' \
  -d '{"prompt":"explique observabilidade em uma frase"}' | jq
```

No próximo capítulo vamos abrir essa aplicação e ver como cada métrica é registrada.
