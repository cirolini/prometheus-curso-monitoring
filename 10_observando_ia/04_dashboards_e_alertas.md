# Dashboards e alertas para IA

Com as métricas no Prometheus, agora é aplicar tudo que já vimos no curso. Este capítulo não traz função nova de PromQL — traz decisões sobre **o que** olhar e **quando** acordar alguém.

O lab já sobe um dashboard pronto, em `Dashboards → Curso Prometheus → observando aplicações com IA`, e as regras estão em [`labs/prometheus/rules/ia.yml`](../labs/prometheus/rules/ia.yml).

## O dashboard

Quatro números no topo, para a pergunta "está tudo bem agora?":

| Painel | Consulta |
|---|---|
| Custo projetado / dia | `predict_linear(llm_cost_usd_total[1h], 24*3600)` |
| Custo acumulado | `sum(llm_cost_usd_total)` |
| p95 de latência | `max(llm:latency_p95:5m)` |
| Taxa de erro | `sum(rate(gen_ai_client_errors_total[5m])) / sum(rate(gen_ai_client_operation_duration_seconds_count[5m]))` |

Repare que a taxa de erro divide pelo `_count` do histograma de duração. É de graça: todo histograma do Prometheus já expõe `_count`, que é o número de observações. Como instrumentamos a duração **também no caminho de erro**, esse `_count` é o total real de chamadas. Não precisa de um contador separado só para o denominador.

### Latência: p50, p95 e p99 juntos

```
histogram_quantile(0.50, sum by (le) (rate(gen_ai_client_operation_duration_seconds_bucket[5m])))
histogram_quantile(0.95, sum by (le) (rate(gen_ai_client_operation_duration_seconds_bucket[5m])))
histogram_quantile(0.99, sum by (le) (rate(gen_ai_client_operation_duration_seconds_bucket[5m])))
```

Os três no mesmo painel, de propósito: **a distância entre eles é a informação**. Num serviço comum, p50 e p99 andam próximos. Numa chamada de LLM eles se afastam muito, e acompanhar essa distância diz mais do que qualquer um dos números sozinho. Quando o p99 dispara e o p50 não mexe, o problema é de cauda — prompt grande, retry, uma região degradada — e não do serviço inteiro.

E, de novo, o `sum by (le)` não é opcional.

### Tokens por minuto

```
sum by (gen_ai_token_type) (rate(gen_ai_client_tokens_total[5m]) * 60)
```

Entrada e saída separadas, porque têm preços diferentes. Se a linha de entrada sobe sozinha, alguém aumentou o contexto — histórico de conversa que não é podado, RAG trazendo documento demais. Se a de saída sobe, o modelo está falando mais.

### Erros por tipo

```
sum by (error_type) (rate(gen_ai_client_errors_total[5m]))
```

O painel mais útil do dashboard num incidente, porque já aponta o caminho: `rate_limit` é quota, `timeout` é paciência ou prompt grande, `client_error` é bug seu.

## Os alertas

Quatro regras, e cada uma segue a filosofia do [módulo 09](../09_conclusion/02_alerting_on_symptoms.md): um alerta precisa representar um problema com ação associada.

### SLO de latência

```yaml
- alert: LLMLatenciaAlta
  expr: |
    histogram_quantile(0.95,
      sum by (le, gen_ai_request_model) (
        rate(gen_ai_client_operation_duration_seconds_bucket[5m])
      )
    ) > 10
  for: 10m
```

O `for: 10m` é generoso de propósito. Latência de LLM oscila muito; um pico de dois minutos não é incidente, é terça-feira. Sem um `for` folgado, esse alerta vira ruído e as pessoas param de olhar.

O agrupamento `by (gen_ai_request_model)` serve para você saber **qual** modelo degradou, e é o que permite alertar de forma diferente por modelo — um modelo grande naturalmente tem um SLO mais frouxo.

### Custo: o `predict_linear`, aplicado a dinheiro

Esta é a regra que amarra o módulo inteiro de volta ao [módulo 06](../06_alerting/02_predict_linear.md):

```yaml
- alert: LLMEstouroDeOrcamentoPrevisto
  expr: predict_linear(llm_cost_usd_total[1h], 24 * 3600) > 50
  for: 30m
```

É exatamente a mesma ideia do disco enchendo. Olha a última hora de gasto, projeta 24 horas à frente por regressão linear, e avisa **agora** se a projeção passar do orçamento diário — não no fim do mês, quando a fatura chega.

Vale lembrar o que dissemos lá atrás: regressão linear assume que o comportamento continua. Se o seu tráfego tem forte sazonalidade — cai de madrugada, sobe de manhã —, uma projeção feita às 10h vai exagerar. Duas saídas: janela maior (`[6h]`), ou uma baseline como a do [módulo 08](../08_advanced_topics/03_baselines.md), comparando com o mesmo horário de dias anteriores.

E a queima súbita, que pega o que a projeção não pega:

```yaml
- alert: LLMQueimaDeCustoAnormal
  expr: |
    sum(rate(llm_cost_usd_total[10m]))
      >
    5 * sum(rate(llm_cost_usd_total[7d]))
  for: 15m
```

Gastando cinco vezes a média da última semana. Pega o loop infinito, o retry descontrolado, o prompt que cresceu de repente. É o tipo de alerta que se paga sozinho na primeira vez que dispara.

### Rate limit em separado

```yaml
- alert: LLMRateLimitPersistente
  expr: sum(rate(gen_ai_client_errors_total{error_type="rate_limit"}[10m])) > 0.2
  for: 15m
```

Já existe um alerta de taxa de erro geral. Este existe porque **a ação é diferente**: não adianta investigar código, é quota. O runbook aqui é "backoff mais agressivo, fila, ou falar com o fornecedor", e isso não tem nada a ver com o runbook de um 5xx.

## As recording rules

Três, pelo motivo de sempre do [módulo 04](../04_querying/04_recording_rules.md) — consulta pesada, calculada uma vez:

```yaml
- record: llm:cost_usd:rate1h
  expr: sum by (gen_ai_request_model) (rate(llm_cost_usd_total[1h]))

- record: llm:tokens:rate5m
  expr: sum by (gen_ai_request_model, gen_ai_token_type) (rate(gen_ai_client_tokens_total[5m]))

- record: llm:latency_p95:5m
  expr: |
    histogram_quantile(0.95,
      sum by (le, gen_ai_request_model) (
        rate(gen_ai_client_operation_duration_seconds_bucket[5m])
      )
    )
```

Tem um segundo motivo, específico deste módulo: como as convenções de GenAI ainda são instáveis, **a recording rule funciona como camada de indireção**. Se a spec renomear `gen_ai.client.token.usage` amanhã, você conserta em um lugar e os dashboards e alertas que consomem `llm:tokens:rate5m` continuam funcionando.

## O que não alertar

Tão importante quanto o que alertar:

**Não alerte em tokens por si só.** Tokens subindo pode ser sucesso do produto. O que dói é custo, e custo já tem alerta.

**Não alerte em cada erro isolado.** Chamada de LLM falha; é por isso que existe retry. Alerte na taxa, depois do retry.

**Não tente alertar em qualidade de resposta com métrica.** Como vimos no [capítulo 1](01_o_que_muda.md), métrica não enxerga isso. Colocar no dashboard os proxies — resposta vazia, falha de validação de schema, retry do usuário — é útil. Transformar isso em página às 3 da manhã é um jeito de perder a confiança do time no alerta.

No último capítulo, o que muda quando a aplicação não faz uma chamada, mas várias em sequência.
