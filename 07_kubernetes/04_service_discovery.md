# Prometheus Service Discovery

Talvez o que mais tenha feito o Prometheus crescer junto com o Kubernetes foi a capacidade de auto discovery dele. Com esta funcionalidade não precisamos ficar reconfigurando o Prometheus a cada alteração da aplicação, ou criação de uma nova aplicação.

> **O que mudou nesta edição.** A versão antiga usava annotations `prometheus.io/scrape` nos pods. Isso não é um padrão do Prometheus — é uma convenção que vinha no `prometheus.yml` de exemplo do chart antigo, com um `relabel_config` que lia essas annotations. Com o Prometheus Operator o mecanismo é outro: **ServiceMonitor** e **PodMonitor**. Se você tem um cluster antigo com as annotations, elas continuam valendo lá; num cluster novo com o operator, elas não fazem nada sozinhas.

## ServiceMonitor

Um `ServiceMonitor` diz ao operator: "existe um Service com estes labels, e ele expõe métricas nesta porta". O operator traduz isso num `scrape_config` e recarrega o Prometheus.

Vamos monitorar o próprio Grafana como exemplo. Primeiro, confirme que ele expõe métricas:

```
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
curl -s localhost:3000/metrics | head
```

O Service do Grafana é assim:

```
$ kubectl -n monitoring get svc monitoring-grafana --show-labels
NAME                 PORT(S)   LABELS
monitoring-grafana   80/TCP    app.kubernetes.io/name=grafana,...
```

E o ServiceMonitor que casa com ele:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: grafana
  namespace: monitoring
  labels:
    release: monitoring
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: grafana     # tem que bater com os labels do Service
  namespaceSelector:
    matchNames:
      - monitoring
  endpoints:
    - port: http-web                      # o NOME da porta no Service, nao o numero
      path: /metrics
      interval: 30s
```

Aplicando:

```
kubectl apply -f grafana-servicemonitor.yaml
```

Em alguns segundos o target aparece no Prometheus, sem reload nenhum.

Dois detalhes que respondem pela maioria dos "meu ServiceMonitor não funciona":

**O `port` é o nome da porta, não o número.** Se o Service declara `- name: http-web, port: 80`, aqui vai `http-web`. Para descobrir:

```
kubectl -n monitoring get svc monitoring-grafana -o jsonpath='{.spec.ports[*].name}' ; echo
```

**O `selector` precisa bater com os labels do Service**, não do Deployment nem do Pod. É o Service que o operator procura.

## PodMonitor

Quando a aplicação não tem Service — um job, um DaemonSet que fala direto — use `PodMonitor`, que é igual mas aponta para os pods:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: PodMonitor
metadata:
  name: minha-app
  labels:
    release: monitoring
spec:
  selector:
    matchLabels:
      app: minha-app
  podMetricsEndpoints:
    - port: metrics
      path: /metrics
```

Na dúvida, prefira `ServiceMonitor`. Ele é o caminho mais comum e o Service te dá um alvo estável.

## Na sua aplicação

Na prática você entrega os dois manifestos juntos, a aplicação e o ServiceMonitor dela. Fica assim:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: minha-app
  labels:
    app: minha-app
spec:
  selector:
    app: minha-app
  ports:
    - name: metrics          # de um nome a porta - o ServiceMonitor precisa dele
      port: 8080
      targetPort: 8080
---
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: minha-app
  labels:
    release: monitoring
spec:
  selector:
    matchLabels:
      app: minha-app
  endpoints:
    - port: metrics
      path: /metrics
```

Essa é a grande vantagem do modelo: **quem sabe que a aplicação expõe métricas é o time da aplicação**, e ele declara isso junto com o deploy. Ninguém precisa abrir um chamado para o time de infra editar a configuração central do Prometheus.

## Quando não aparece

O roteiro de depuração, na ordem:

```
# 1. o operator enxergou o objeto?
kubectl -n monitoring get servicemonitor

# 2. o que o Prometheus esta' procurando?
kubectl -n monitoring get prometheus monitoring-prometheus \
  -o jsonpath='{.spec.serviceMonitorSelector}' ; echo

# 3. o selector casa com algum Service de verdade?
kubectl get svc -l app.kubernetes.io/name=grafana --all-namespaces

# 4. o operator reclamou de alguma coisa?
kubectl -n monitoring logs deploy/monitoring-operator | tail -30
```

Na maioria das vezes é o label `release` faltando, ou o nome da porta errado.

E vale lembrar: por baixo de tudo isso o Prometheus continua usando o mesmo service discovery de sempre, o `kubernetes_sd_config`. O operator só está escrevendo aquele YAML por você. Se quiser ver o resultado:

```
kubectl -n monitoring get secret prometheus-monitoring-prometheus \
  -o jsonpath='{.data.prometheus\.yaml\.gz}' | base64 -d | gunzip | head -60
```

É um bom exercício: você reconhece ali os mesmos `scrape_configs` e `relabel_configs` do módulo 02.
