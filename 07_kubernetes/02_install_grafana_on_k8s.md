# Instalando o Grafana no Kubernetes

O Grafana hoje é uma das principais formas de montar graficos e tirar insights a partir das métricas do Prometheus. Através dele vamos poder explorar mais dados do nosso cluster e ter mais informações relevantes.

## Instalando o Grafana

Para instalar o Grafana vamos seguir um processo bastante similar ao do prometheus.

```
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

helm install [RELEASE_NAME] grafana/grafana
```

Para acessar o grafana no nosso navegador podemos usar o mesmo comando de port-forward somente mudando para o container do grafana: `kubectl port-forward grafana-76849b87b5-szrm9 9090`

Dentro do Grafana podemos adicionar o source do prometheus, colocando o endereço interno do cluster: `prometheus-server.default.svc.cluster.local` e depois disso ja podemos adicionar alguns dashboards direto do diretório da grafana sobre dashboards:

- https://grafana.com/grafana/dashboards/8588
- https://grafana.com/grafana/dashboards/7249


# Expondo os serviços externamente

Claro que o acesso em produção não funciona usando port-forward, e precisamos ter acesso externo as mesmas URLS. Claro que cada cloud provider como a AWS ou GCP tem o seu próprio jeito de fazer isso, e se você ainda tem um cluster em baremetal tem outras formas.

A maneira mais comum é ativando um service do tipo loadbalancer, isso vai fazer com que o teu provedor de acesso libere um IP externo para que você possa acessar os serviços. Fazemos a configuração dos mesmos alterando as configurações do helm e aplicando novamente.

## GRAFANA

Para o grafana é extremamente parecido com o Prometheus:

```
service:
  type: LoadBalancer
```

Ou para habilitar o ingress:

```
grafana.ini:
  server:
    domain: monitoring.example.com
    root_url: "%(protocol)s://%(domain)s/grafana"
    serve_from_sub_path: true
ingress:
  enabled: true
  hosts:
    - "monitoring.example.com"
  path: "/grafana"
```

Depois disso vamos ter Dashboards como esse:

![Grafana-k8s](/07_kubernetes/images/grafana_k8s.png "Grafana-k8s")
