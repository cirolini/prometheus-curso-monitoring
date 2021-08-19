# Jobs e Instances

Como ja vimos o prometheus vai até os endpoints buscar as métricas, esse método se chama em ingles "scrap", para o prometheus todos os endpoints são conhecidos como instances e uma coleção de instancias corresponde a um job.

Esse modelo pode ser visto na configuração:

```
- job_name: 'prometheus'

    static_configs:
    - targets: ['localhost:9090']
    - targets: ['PMS2:9090']
    - targets: ['PMS3:9090']
```

Os nomes dos jobs e das instancias são automaticamente adicionados automaticamente no metric name. Ao exemplo abaixo:

```
up{instance="localhost:9090", job="prometheus"}
```
