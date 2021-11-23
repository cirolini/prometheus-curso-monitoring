# Detecção de Anomalia com Z-Score

Um tópico bastante interessante em qualquer universo dos dados é os modelos de detecção de anomalias. O Z-Score, ou Escore padrão, ou standard score é um método simples para encontrar desvios padrão em series de dados, basicamente encontrar anomalias em dados do tipo timeseries.

O primeiro aviso, o z-score funciona muito bem com dados com uma distribuição normal. Dados que sofrem muita sazonalidade, diminuem muito a noite, ou que variam muito ele pode ter dificuldade e conter muitos falsos positivos.

Um valor que eu gosto bastante de usar o z-score é para detecção de anomalia em tempos de entrega, e também para dados de disponibilidade, como são dados que tem menos variações, o z-score costuma ser bem preciso.

A formula do z-score é assim:

![Z-Score](/08_advanced_topics/images/z-score-formula.png "Z-Score Formula")

## Como calcular o z-score

Para calcular o z-score você precisa subtrair a métrica pela média da métrica e dividir o resultado pelo desvio padrão. Como estamos lidando com um timeseries, vamos pegar a média sobre o tempo e o desvio padrão sobre o tempo da ultima semana, para ter um valor com uma média mais precisa porque vamos observar um tempo maior.

A formula no Prometheus fica assim, algo bem fácil de fazer no Prometheus.

```
(
  http_availability -
  avg_over_time(http_availability[1w])
) / stddev_over_time(http_availability[1w])
```

O resultado é um valor que vai dizer o quanto longe do normal que a métrica esta, sendo que um valor igual a 0 significa que esta exatamente no valor normal e um +3 ou -3 esta muito acima ou abaixo do normal.

Se colocarmos isso em um gráfico vai ficar assim, e cada vez que o valor do z-score baixou de -3 foi algo realmente muito baixo do normal.

![Z-Score](/08_advanced_topics/images/z-score.png "Z-Score")

Para criarmos um alerta pode ser algo nessa linha:

```
- name: AnomalyDetection
  rules:
  - alert: HHTTP Availability Anomaly Detection
    expr: (( http_availability - avg_over_time(http_availability[1w])) / stddev_over_time(http_availability[1w]) ) < 3
    for: 50m
    labels:
      severity: warning
    annotations:
      summary: "Anomaly detected in HTTP Availability "
      description: "Z-Score is above than -3"
```


Referencias:
- https://about.gitlab.com/blog/2019/07/23/anomaly-detection-using-prometheus/
- https://en.wikipedia.org/wiki/Standard_score
- https://towardsdatascience.com/practical-monitoring-with-prometheus-grafana-part-iii-81f019ecee19
