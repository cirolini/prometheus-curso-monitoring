# Instrumentando uma chamada de LLM

Vamos abrir a aplicação do lab e ver o que é preciso registrar numa chamada de modelo. O código está em [`labs/llm-app/`](../labs/llm-app/), dividido em quatro arquivos: `metrics.py` (as métricas), `provider.py` (quem fala com o modelo), `agent.py` (o agente do capítulo 5) e `app.py` (a aplicação FastAPI).

Nada aqui depende de fornecedor. O `provider.py` é um adapter fino com duas implementações — `mock`, que é o padrão e roda sem chave nenhuma, e `http`, que você aponta para o seu provider por variável de ambiente. **Trocar de fornecedor é implementar uma função.** As métricas não mudam.

## As métricas

### Duração

```python
operation_duration = Histogram(
    "gen_ai_client_operation_duration_seconds",
    "Duracao da chamada ao modelo",
    ["gen_ai_operation_name", "gen_ai_provider_name", "gen_ai_request_model", "outcome"],
    buckets=(0.1, 0.25, 0.5, 1, 2, 4, 8, 15, 30, 60),
)
```

Três decisões aqui, e todas importam.

**Os buckets vão até 60s.** Os default do `prometheus_client` param em 10. Como vimos no capítulo anterior, a cauda de uma chamada de LLM passa disso com folga, e tudo que cai no `+Inf` some do cálculo de percentil. Meça a sua distribuição real antes de fixar esses números — os do lab são um ponto de partida razoável, não uma verdade.

**Tem uma label `outcome`.** Chamada que falhou também tem duração, e geralmente uma duração diferente: timeout demora muito, rate limit responde na hora. Se você só medir o caminho feliz, a sua latência fica *mais bonita* justamente quando o sistema está pior — as chamadas lentas viram erro e desaparecem do gráfico. No `app.py` isso aparece como duas chamadas ao `observe()`, uma no sucesso e outra na falha.

**O modelo é label.** Você vai querer comparar modelos, e vai querer ver o efeito de trocar de modelo. Sem essa label, não dá.

### Tokens

```python
token_usage = Histogram(
    "gen_ai_client_token_usage_tokens",
    "Tokens consumidos por chamada",
    [..., "gen_ai_token_type"],     # input | output
    buckets=(10, 50, 100, 250, 500, 1000, 2500, 5000, 10000, 25000, 100000),
)

tokens_total = Counter(
    "gen_ai_client_tokens_total",
    "Total acumulado de tokens",
    ["gen_ai_provider_name", "gen_ai_request_model", "gen_ai_token_type"],
)
```

São duas métricas porque respondem a perguntas diferentes. O histograma responde *"como é a distribuição do tamanho das minhas chamadas?"* — é ele que mostra que apareceu uma cauda de prompts gigantes. O counter responde *"quantos tokens eu queimei no total?"* — é ele que alimenta o custo.

Repare que `input` e `output` são **label, não métricas separadas**. Isso segue a convenção do OpenTelemetry, que vamos ver no próximo capítulo, e é conveniente: você soma os dois quando quer o total e separa quando quer o custo, já que saída costuma custar bem mais que entrada.

### Custo

```python
cost_usd_total = Counter(
    "llm_cost_usd_total",
    "Custo acumulado estimado em dolares",
    ["gen_ai_provider_name", "gen_ai_request_model"],
)
```

Repare no prefixo diferente: `llm_`, não `gen_ai_`. É de propósito. **As convenções do OpenTelemetry não definem nenhuma métrica de custo** — conferi a especificação enquanto escrevia isto, e não existe. Então este nome é invenção nossa, e o prefixo diferente deixa claro o que é padrão e o que é caseiro.

O cálculo é uma multiplicação:

```python
cost = (input_tokens / 1_000_000 * PRICE_IN
        + output_tokens / 1_000_000 * PRICE_OUT)
cost_usd_total.labels(provider.name, provider.model).inc(cost)
```

Os preços vêm de variável de ambiente, e **você** os mantém. Não existe mágica: se o provider mudar a tabela e você não atualizar, o gráfico vai continuar bonito e errado. Por isso a métrica se chama *estimado*.

Um counter de dinheiro se comporta como qualquer counter: use `rate()` para ver gasto por segundo, multiplique para chegar em hora ou dia, e `predict_linear()` para projetar. Fica tudo igual ao que você já sabe do [módulo 04](../04_querying/03_functions.md).

### Erros, por tipo

```python
errors_total = Counter(
    "gen_ai_client_errors_total",
    "Erros por tipo",
    [..., "error_type"],
)
```

Aqui está o detalhe que mais rende no dia a dia: **separe os erros por tipo**, porque a ação é diferente para cada um.

| `error_type` | O que fazer |
|---|---|
| `rate_limit` | backoff, fila, ou pedir mais quota. Não é bug |
| `timeout` | às vezes é só esperar mais; às vezes o prompt ficou grande demais |
| `server_error` | é do provider. Retry ajuda |
| `client_error` | é seu. Retry **não** ajuda, só gasta |
| `connection_error` | rede |

Um contador único de "erros" junta tudo isso num número que não diz o que fazer. E cuidado com a tentação oposta: não use a mensagem de erro crua como label. Cardinalidade alta é o jeito mais fácil de derrubar um Prometheus — mantenha o conjunto de valores pequeno e fechado, como no `provider.py`.

### Retries

```python
retries_total = Counter("gen_ai_client_retries_total", ..., ["error_type"])
```

Retry é invisível para quem mede só a chamada final, e custa dinheiro de verdade: cada tentativa é uma chamada faturada. Uma aplicação que "está bem" com 15% de retry está queimando 15% a mais do que a fatura deveria — e a latência que o usuário sente é a soma das tentativas.

Só faz retry do que vale a pena:

```python
RETRIABLE = {"rate_limit", "timeout", "server_error", "connection_error"}
```

Um `client_error` fora dessa lista é intencional: tentar de novo vai receber o mesmo 400 e pagar por ele.

## Juntando tudo

O coração do `app.py` é este laço:

```python
def call_llm(prompt: str):
    attempt = 0
    started = time.perf_counter()
    m.inflight.labels(provider.name).inc()
    try:
        while True:
            try:
                completion = provider.complete(prompt)
            except ProviderError as e:
                m.errors_total.labels(provider.name, provider.model, e.error_type).inc()
                if e.error_type in RETRIABLE and attempt < MAX_RETRIES:
                    attempt += 1
                    m.retries_total.labels(provider.name, provider.model, e.error_type).inc()
                    time.sleep(0.2 * (2 ** attempt))      # backoff exponencial
                    continue
                m.operation_duration.labels(
                    "chat", provider.name, provider.model, "error"
                ).observe(time.perf_counter() - started)
                raise

            elapsed = time.perf_counter() - started
            labels = ("chat", provider.name, provider.model)
            m.operation_duration.labels(*labels, "ok").observe(elapsed)
            m.token_usage.labels(*labels, "input").observe(completion.input_tokens)
            m.token_usage.labels(*labels, "output").observe(completion.output_tokens)
            ...
            return completion, elapsed, cost, attempt
    finally:
        m.inflight.labels(provider.name).dec()
```

Três coisas para reparar:

O `try/finally` com o `inflight` garante que o gauge desce **mesmo quando a chamada explode**. Gauge que só sobe no caminho feliz vira mentira depois do primeiro incidente.

O `started` é marcado **antes do primeiro retry**, não a cada tentativa. A duração que interessa é a que o usuário esperou, que inclui todos os backoffs.

E a duração é registrada nos dois caminhos, com `outcome` diferente.

## Rodando

```
make up
curl -s -X POST localhost:8000/ask \
  -H 'content-type: application/json' \
  -d '{"prompt":"explique observabilidade"}' | jq
```

A resposta traz os números da chamada:

```json
{
  "text": "(resposta simulada para: explique observabilidade)",
  "model": "mock-model-1",
  "input_tokens": 132,
  "output_tokens": 604,
  "duration_seconds": 0.712,
  "estimated_cost_usd": 0.009456,
  "retries": 0
}
```

E as métricas estão onde sempre estiveram:

```
curl -s localhost:8000/metrics | grep gen_ai_client_token
```

O lab já sobe um gerador de tráfego contra essa aplicação, então os gráficos se mexem sozinhos enquanto você estuda. No Prometheus, comece por aqui:

```
histogram_quantile(0.95, sum by (le) (rate(gen_ai_client_operation_duration_seconds_bucket[5m])))
sum by (gen_ai_token_type) (rate(gen_ai_client_tokens_total[5m]) * 60)
sum(rate(llm_cost_usd_total[1h])) * 3600
sum by (error_type) (rate(gen_ai_client_errors_total[5m]))
```

São as mesmas funções do módulo 04. Nada de novo — só aplicadas a um domínio novo.
