# Jobs e Instances

Como ja vimos o prometheus vai até os endpoints buscar as métricas, esse método se chama em ingles "scrape", para o prometheus todos os endpoints são conhecidos como instances e uma coleção de instancias corresponde a um job.

Esse modelo pode ser visto na configuração:

```
scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets:
          - 'localhost:9090'
          - 'PMS2:9090'
          - 'PMS3:9090'
```

Aqui temos um job chamado `prometheus` com três instances. Repare que os três endereços vão numa lista só dentro do mesmo `targets` — se você repetir a chave `targets` três vezes, o YAML mantém só a última.

Os nomes dos jobs e das instancias são automaticamente adicionados automaticamente no metric name. Ao exemplo abaixo:

```
up{instance="localhost:9090", job="prometheus"}
```
