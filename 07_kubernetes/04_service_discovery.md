# PRometheus Service Discovery

Talvez o que mais tenha feito o Prometheus crescer junto com o Kubernetes foi a capacidade de auto discovery dele. Com esta funcionalidade não precisamos ficar reconfigurando o Prometheus a cada alteração da aplicação, ou criação de uma nova aplicação, basta colocarmos os annotations certos na aplicação.

Primeiro vamos monitorar o próprio Grafana. Vamos verificar se ele ja esta mostrando métricas no `/metrics`

```
kubectl port-forward grafana-7f67869c5c-k2xkd 3000
curl localhost:300/metrics
```

Com isso funcionando vamos configurar os annotations:

```
podAnnotations:
  prometheus.io/scrape: "true"
  prometheus.io/path: /metrics
  prometheus.io/port: "3000"
```

Agora basta atualizar pelo helm:

```
helm upgrade -f grafana/value_enable_monitoring.yml grafana grafana/grafana
```

Em alguns segundos podemos consultar que o Kubernetes tem um novo target, e inclusive ja podemos visualizar os dados.

Isso fizemos para o Grafana, mas o conceito é o mesmo para as tuas aplicações. Basicamente, quando voce for fazer o deployment ou a criação de um novo Pod bastaca colocar os mesmos annotations e a parta da qual a sua aplicação expõe as métricas, como no exemplo abaixo:

```
apiVersion: v1
kind: Pod
metadata:
  name: annotations-demo
  annotations:
    prometheus.io/scrape: "true"
    prometheus.io/path: /metrics
    prometheus.io/port: "80"
spec:
  containers:
  - name: my_app
    image: my_app:latest
    ports:
    - containerPort: 80
```
