# O Basico

O prometheus tem uma query language própria chamada de PromQL que vai permitir selecionar e agregar os dados das metricas que vamos coletar. Vamos começar a entender como fazer querys no Prometheus usando a própria interface web dele.

Se colocarmos a metric name: `prometheus_http_requests_total` vamos ver todas as metricas referentes a esse metric name, pq estão divididas pelos labels. Se especificarmos um label, isso vai fazer com que ele filtre os resultados e mostre somente o que estamos pesquisando: `prometheus_http_requests_total{handler="/metrics"}` é possivel usar multiplos labels: `prometheus_http_requests_total{code="200", handler="/metrics"}`. Também é possivel usar operadores para selecionar os labels, são eles:

- =: Seleciona labels exatamente com o que esta na string.
- !=: Seleciona labels diferentes do que esta na string.
- =~: Seleciona labels que batem com a regex.
- !~: Seleciona labels que não batem com a regex.

A parte das expressões regulares são muito uteis, por exemplo selecionar todas as métricas do api: `prometheus_http_requests_total{handler=~"/api.*"}`.

# Seletor de range de tempo

Também é possivel usar um seletor de range de tempo para buscar mais valores ao mesmo tempo, por exemplo: `prometheus_http_requests_total[1m]` podem ser usados em conjunto com as labels ou funções.

## Unidades de tempo

As unidades de tempos que podemos usar são:

ms - milliseconds
s - seconds
m - minutes
h - hours
d - days - assuming a day has always 24h
w - weeks - assuming a week has always 7d
y - years - assuming a year has always 365d

Isso também vai servir para as funções que vamos ver mais adiante.

# Vendo registros do passado

Uma outra coisa interessante no prometheus é que podemos deslocar as nossas querys para buscarem dados no passado, ou seja que o ponto inicial delas aconteça no tempo que determinarmos, assim: `prometheus_http_requests_total offset 5m`, essa query vai buscar esse metric name de 5 minutos atras. 
