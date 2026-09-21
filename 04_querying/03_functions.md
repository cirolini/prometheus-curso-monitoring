# Functions

O prometheus tem diversas funções que ajudam a modificar/agregar/extrair informações a partir dos dados que coletamos. A ideia é cobrir as funções que eu mais uso do Prometheus.

## Delta

Calcula a diferença entre o primeiro e o ultimo valor em um range de tempo. O `delta` é para **gauge** — aquilo que sobe e desce, como temperatura ou uso de memória.

```
delta(node_memory_MemAvailable_bytes[5m])
```

Para counter não use `delta`: use `increase`, que é o equivalente e sabe lidar com o reset do contador quando a aplicação reinicia.

```
increase(prometheus_http_requests_total[5m])
```

## Rate

O rate calcula a média por segundo de um **counter** — aquele valor que só sobe. É muito util quando queremos ver o numero de requisições por segundo, usando uma média baseada no intervalo que passamos na consulta.

Vale gravar essa regra, porque é o erro mais comum de quem está começando: **`rate` é sempre sobre counter, nunca sobre gauge.** Aplicar `rate` num gauge devolve número, mas número sem significado. O `rate` também trata sozinho o reset do contador: se a aplicação reinicia e a métrica volta a zero, ele entende que houve reset e não devolve um valor negativo.


```
rate(prometheus_http_requests_total{handler="/metrics"}[1m])
```

## iRate

O irate é exatamente igual ao rate, a diferença é que ele usa somente os últimos dois pontos de dados. Ele deve ser usado quando queremos ver melhor os "spikes", ou comportamentos sem a normalização de uma média maior de tempo.

```
irate(prometheus_http_requests_total{handler="/metrics"}[1m])
```

## predict_linear

Essa função usa regressão linear para prever o valor de uma métrica em um determinado período no futuro. Regressão linear é uma das formas mais simples de tentar fazer previsões, mas quando os dados são normalizados é possível fazer previsões bem assertivas.

```
predict_linear(node_filesystem_avail_bytes[30m], 1 * 3600)
```

O ultimo parâmetro é o o numero de segundos que se quer prever no futuro, aquele calculo é para facilitar o entendimento em horas.

## histogram_quantile

Já conversamos na parte de conceitos como funciona o tipo de dado [Histogram](../03_conceitos/02_tipos_de_metricas.md), agora somente revisamos a função exibindo alguns percentils de dados.

```
histogram_quantile(0.9,
  sum by (le) (rate(prometheus_http_request_duration_seconds_bucket[5m]))
)
```

Essa expressão pega os 90 percentil do tempo de duração por segundo das requisições. Podemos brincar com os percentils simplesmente mudando o primeiro parâmetro.

Repare no `sum by (le)`. Ele não é enfeite: o `histogram_quantile` precisa receber os buckets agregados pela label `le`, que é quem diz o limite de cada bucket. Se você agregar sem o `by (le)`, ou esquecer de agregar quando tem várias instâncias, o resultado sai errado — e o pior é que sai errado silenciosamente, sem erro nenhum.

Se a métrica for um [native histogram](../03_conceitos/02_tipos_de_metricas.md), a consulta fica mais curta, porque não existe `_bucket` nem `le` para agregar:

```
histogram_quantile(0.9, rate(prometheus_http_request_duration_seconds[5m]))
```
