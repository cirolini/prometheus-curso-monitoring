# Tipos de Métricas

Existem 4 tipos de métricas principais dentro do Prometheus.

## Counter

Um counter é uma métrica cumulativa que só incrementa o valor, ou seja, o valor só aumenta, e só é reiniciada, ou volta a zero quando é feito um restart da aplicação que gera a metrica. Exemplos de usos são numero de requisições atendidas, tarefas completadas ou erros. Vai ser util também para calcularmos o numero de requisições por segundo quando vermos a função rate.

Counter não devem ser usados em valores que podem diminuir, como numero de threads ou processos de um determinado sistema.

Exemplo da métrica:

```
# HELP prometheus_http_requests_total Counter of HTTP requests.
# TYPE prometheus_http_requests_total counter
prometheus_http_requests_total{code="200",handler="/api/v1/label/:name/values"} 5
prometheus_http_requests_total{code="200",handler="/api/v1/metadata"} 1
prometheus_http_requests_total{code="200",handler="/api/v1/query"} 10
prometheus_http_requests_total{code="200",handler="/api/v1/query_range"} 8
prometheus_http_requests_total{code="200",handler="/api/v1/targets"} 1
prometheus_http_requests_total{code="200",handler="/favicon.ico"} 1
prometheus_http_requests_total{code="200",handler="/graph"} 4
prometheus_http_requests_total{code="200",handler="/metrics"} 4959
prometheus_http_requests_total{code="200",handler="/static/*filepath"} 6
prometheus_http_requests_total{code="302",handler="/"} 3
```

Uma maneira de saber o numero de requisições por segundo:

```
rate(prometheus_http_requests_total[30m])
```

Um exemplo bem simples de um conter um python:

```
from prometheus_client import Counter
c = Counter('my_failures', 'Description of counter')
c.inc()     # Increment by 1
c.inc(1.6)  # Increment by given value
```


## Gauge

Um Gauge é uma métrica que representa um valor numérico que pode subir ou descer. Server para medir numero de processos ou threads, e também saturação como uso de disco ou memória, entre muitas outras métricas.

Um exemplo de métrica usando gauge:

```
# HELP go_goroutines Number of goroutines that currently exist.
# TYPE go_goroutines gauge
go_goroutines 32
```

Um exemplo simples em python.

```
from prometheus_client import Gauge
g = Gauge('my_number_of_threads', 'Description of gauge')
g.inc()      # Increment by 1
g.dec(10)    # Decrement by given value
g.set(4.2)   # Set to a given value
```


## Histogram

Um histogram armazena o tamanho e o numero de eventos dividido em grupos, em ingles, buckets. Isso permite calcular agregações com os quantil, ou também conhecido como percentils, como 95 percentil, etc. Pode parecer um pouco confuso no inicio, mas é uma forma engenhosa de conseguir calcular rapidamente os percentils de tempo ou tamanhos de grandes números de requisições.

Um histograma expõe múltiplas informações durante a coleta de dados.

- buckets, ou counter para cada bucket em separado: <basename>_bucket{le="<upper inclusive bound>"}
- soma, a soma total dos valores: <basename>_sum
- numero total de eventos: <basename>_count

Em um exemplo isso fica mais claro:

```
# HELP prometheus_http_request_duration_seconds Histogram of latencies for HTTP requests.
# TYPE prometheus_http_request_duration_seconds histogram
prometheus_http_request_duration_seconds_bucket{handler="/api/v1/query_range",le="0.1"} 795000
prometheus_http_request_duration_seconds_bucket{handler="/api/v1/query_range",le="0.2"} 859052
prometheus_http_request_duration_seconds_bucket{handler="/api/v1/query_range",le="0.4"} 898039
prometheus_http_request_duration_seconds_bucket{handler="/api/v1/query_range",le="1"} 916661
prometheus_http_request_duration_seconds_bucket{handler="/api/v1/query_range",le="3"} 925581
prometheus_http_request_duration_seconds_bucket{handler="/api/v1/query_range",le="8"} 928383
prometheus_http_request_duration_seconds_bucket{handler="/api/v1/query_range",le="20"} 929368
prometheus_http_request_duration_seconds_bucket{handler="/api/v1/query_range",le="60"} 930049
prometheus_http_request_duration_seconds_bucket{handler="/api/v1/query_range",le="120"} 930213
prometheus_http_request_duration_seconds_bucket{handler="/api/v1/query_range",le="+Inf"} 930451
prometheus_http_request_duration_seconds_sum{handler="/api/v1/query_range"} 179499.95925200367
prometheus_http_request_duration_seconds_count{handler="/api/v1/query_range"} 930451
```

Os valores dos buckets são sempre incrementados, ou seja o bucket mais baixo tem o menor valor, e os buckets com valores maiores vão sendo incrementados até que cheguem ao total/count.

E podemos calcular por exemplo o 90 percentil da duração das requisições usando a função histogram_quantile:

```
histogram_quantile(0.9,
  rate(prometheus_http_request_duration_seconds_bucket[5m])
)
```

## Sumary

Sumary são muito similares aos histogram, server para contabilizar tempos de respostas ou tamanhos das requisições e também servem para verificar os percentils de valores. A grande diferença é que os summary os quantiles não são cumulativos, e se são processados na aplicação/cliente. Então, se vc deseja saber o percentil de um determinado valor pode buscar a metrica diretamente usando o label do quantile.


```
# HELP prometheus_rule_evaluation_duration_seconds The duration for a rule to execute.
# TYPE prometheus_rule_evaluation_duration_seconds summary
prometheus_rule_evaluation_duration_seconds{quantile="0.5"} 6.4853e-05
prometheus_rule_evaluation_duration_seconds{quantile="0.9"} 0.00010102
prometheus_rule_evaluation_duration_seconds{quantile="0.99"} 0.000177367
prometheus_rule_evaluation_duration_seconds_sum 1.623860968846092e+06
prometheus_rule_evaluation_duration_seconds_count 1.112293682e+09
```

Os summarys tem grandes custos de processamento no lado do cliente e grandes dificuldades de criar corretamente as métricas. Hoje é muito recomendado utilizar histograms antes de summaries, que ainda acabam existindo mais por uma questão histórica do Prometheus.
