# Recoding Rules

Muitas vezes as querys que precisamos fazer podem ser muito pesadas e podem exigir que o prometheus faça muito processamento dependendo do numero de funções ou operações que utilizamos e também da quantidade de dados que vamos processar.

Para aliviar esse trabalho no Prometheus podemos usar as recording rules, que ja fazem o processamento que é necessário em tempo de coleta, ou seja, podemos gravar dados ja pré processados em uma outra metric name para poder consultar mais rapidamente.


Criamos um arquivo com as regras:

```
sudo vim /etc/prometheus/recording_rules.yml

groups:
  - name: general
    rules:
      - record: prometheus_http_requests:sum:rate1m
        expr: sum(rate(prometheus_http_requests_total{handler="/metrics"}[1m])) by (code)
```

Depois arrumamos a conf do prometheus para ter esse arquivo e fazemos o reload dele:

```
sudo vim /etc/prometheus/prometheus.yml

rule_files:
  - "recording_rules.yml"
```

Agora basta pesquisar pelo nome da metrica que criamos e ja temos a métrica funcionando.
