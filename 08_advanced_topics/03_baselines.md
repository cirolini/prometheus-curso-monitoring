# Criando uma baseline Simples

A muito tempo atrás quando eu comecei a trabalhar com datacenters usávamos um sistema de monitoração baseado em RRDtool parte desenvolvido na empresa, e uma das funcionalidade mais legais que tínhamos era a baseline. Magicamente ao clicarmos em um botão depois de algumas semanas gerava uma linha, junto a métrica que estávamos analisando.

A baseline é uma métrica que se baseia em pontos no passado para gerar um linha de comparação com o cenário atual. Pensando em um exemplo pratico, serve para ver se o teu numero de requisições aumentou ou diminuiu comparado com um período de "x" tempo.

Sim, eu sei que existem os `avg_over_time` e o `quantile_over_time` entre outros, o problema é que para graficos sazonais, ou seja aqueles que fazem uma curva, as métricas `over_time` geram uma linha reta de difícil comparação com o momento atual. Ex:

![Baseline_avg](/08_advanced_topics/images/baseline_avg.png "Baseline with avg_over_time")

Isso é uma baseline, mas para dados sazonais não tem muita eficiência.

## Método de criar uma baseline

O prometheus tem uma feature que é o `offset`, a capacidade de olhar uma métrica em um periodo de tempo atras. Por exemplo, `prometheus_http_requests_total offset 1d` vai me dizer a mesma métrica só que com o valor de 1 dia atras. O valor que vamos usar no offset para variar tbm, pode ser minutos `15m`, ou anos, `2y`.

Assumindo que eu ja tenho uma recording rule que grava o somatório de requisições http do prometheus assim:

```
- record: prom:requests_total:rate1m
  expr: sum(rate(prometheus_http_requests_total[1m]))
```

Pensando nisso eu queria criar uma baseline que fosse a média dos valores das ultimas 8 semanas de uma determinada métrica, acabei fazendo dessa forma:

```
((
  avg_over_time(prom:requests_total:rate1m[30m] offset 1w) +
  avg_over_time(prom:requests_total:rate1m[30m] offset 2w) +
  avg_over_time(prom:requests_total:rate1m[30m] offset 3w) +
  avg_over_time(prom:requests_total:rate1m[30m] offset 4w) +
  avg_over_time(prom:requests_total:rate1m[30m] offset 5w) +
  avg_over_time(prom:requests_total:rate1m[30m] offset 6w) +
  avg_over_time(prom:requests_total:rate1m[30m] offset 7w) +
  avg_over_time(prom:requests_total:rate1m[30m] offset 8w))
/ 8)
```

Com isso temos a média de numero de requestes das ultimas 8 semanas desse exato ponto do tempo, colocando isso em um gráfico no Grafana e juntando com a métrica atual, vamos ter algo semelhante a isso:


![Baseline_](/08_advanced_topics/images/baseline.png "Baseline")

Esse gráfico mostra que baseado em uma média das ultimas 8 semanas, o meu acesso a essa API esta crescendo.
