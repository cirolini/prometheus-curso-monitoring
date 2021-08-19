# A API de gerenciamento

O Prometheus desenvolveu uma API de gerenciamento que podemos executar alguns comandos e pegar alguns status sobre o sistema. Essa API é util para automatizar deployments de alertas ou alterações de configuração, ou até mesmo testar a saúde do Prometheus.

Query para testar a saúde do Prometheus. Caso tudo esteja correto ele vai devolver uma resposta com o status 200 OK, com a msg `Prometheus is Healthy.`

```
$ curl localhost:9090/-/healthy
Prometheus is Healthy.
```

Query para testar se o Prometheus ja esta pronto para receber consultas, ja esta avaliando os alertas e coletando métricas. Útil para quando reiniciamos o sistema.

```
$ curl localhost:9090/-/ready
Prometheus is Ready.
```

Fazer o reload do Prometheus, especialmente útil quando você atualiza alertas, cria novos jobs ou alterar confs.

```
$ curl -d POST localhost:9090/-/reload
```

Podemos fazer com que o Prometheus seja encerrado corretamente através da API de gerenciamento, para isto basta.

```
curl -d POST localhost:9090/-/quit
```
