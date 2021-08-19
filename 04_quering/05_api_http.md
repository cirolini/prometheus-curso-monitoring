# API HTTP

Uma forma que vc pode fazer as consultas ao Prometheus, além da interface gráfica que ele ja prove, ou do Grafana, é utilizar diretamente a API HTTP. Caso você precise criar uma integração com o prometheus existem bibliotecas prontas para fazer a integração, mas para coisas mais simples é possível consultar o prometheus por uma API HTTP.

Para consultarmos a API, basta usarmos a url do nosso prometheus e acrescentar `/api/v1/query`. Essa consulta vai te dar o resultado de uma consulta em um determinado momento no tempo.

Os paramentros são:

- query=<string>: A string é a expressão do Prometheus para a consutla.
- time=<rfc3339 | unix_timestamp>: O momento em que vc quer consultar o valor da métrica. Opcional.
- timeout=<duration>: Tempo para gerar um timeout na requisição. Opcional.


```
$ curl 'http://localhost:9090/api/v1/query?query=up&time=2015-07-01T20:10:51.781Z'
{
   "status" : "success",
   "data" : {
      "resultType" : "vector",
      "result" : [
         {
            "metric" : {
               "__name__" : "up",
               "job" : "prometheus",
               "instance" : "localhost:9090"
            },
            "value": [ 1435781451.781, "1" ]
         },
         {
            "metric" : {
               "__name__" : "up",
               "job" : "node",
               "instance" : "localhost:9100"
            },
            "value" : [ 1435781451.781, "0" ]
         }
      ]
   }
}
```

# Alertas

Podem ainda criar softwares para ler alertas usando a API:

```
$ curl http://localhost:9090/api/v1/alerts

{
    "data": {
        "alerts": [
            {
                "activeAt": "2018-07-04T20:27:12.60602144+02:00",
                "annotations": {},
                "labels": {
                    "alertname": "my-alert"
                },
                "state": "firing",
                "value": "1e+00"
            }
        ]
    },
    "status": "success"
}
```

# Deletando dados

Uma das maneiras mais fáceis de apagar dados do Prometheus é usando a API para excluir metric names inteiros, ou em um período de tempo.

Basicamente basta fazer um POST na url `/api/v1/admin/tsdb/delete_series`.

Os parametros são:

URL query parameters:

- match[]= O metric_name mais os labels que quer deletar.
- start=<rfc3339 | unix_timestamp>: Data inicial para começar a deleção.
- end=<rfc3339 | unix_timestamp>: Data final para a deleção. Opcional.

```
$ curl -X POST \
  -g 'http://localhost:9090/api/v1/admin/tsdb/delete_series?match[]=up&match[]=process_start_time_seconds{job="prometheus"}'
```

Depois de deletar as metrics é necessário executar via API um clean tombstones, isso vai fazer com que ele limpe os arquivos em disco e libere espaço.

```
$ curl -XPOST http://localhost:9090/api/v1/admin/tsdb/clean_tombstones
```
