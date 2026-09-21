# Grafana no Kubernetes

O Grafana hoje é uma das principais formas de montar graficos e tirar insights a partir das métricas do Prometheus. Através dele vamos poder explorar mais dados do nosso cluster e ter mais informações relevantes.

> **O que mudou nesta edição.** Antes este capítulo instalava o chart `grafana/grafana` separado e mandava você criar o datasource na mão. Com o kube-prometheus-stack **o Grafana já veio instalado no passo anterior**, com o datasource do Prometheus apontado e dezenas de dashboards de Kubernetes provisionados. Então este capítulo mudou de assunto: em vez de instalar, vamos ver o que já está lá e como acrescentar o que é seu.

## Acessando

```
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
```

Repare em duas coisas. A porta do lado do service é **80**, não 3000 — o `3000:80` mapeia a porta local 3000 para a porta 80 do service. E o alvo é o `svc/`, não o pod: assim você não precisa descobrir o nome do pod, que muda a cada deploy.

Abra http://localhost:3000. O usuário é `admin` e a senha padrão do chart é `prom-operator`. Para confirmar:

```
kubectl -n monitoring get secret monitoring-grafana \
  -o jsonpath="{.data.admin-password}" | base64 -d ; echo
```

Para trocar, mexa nos values:

```
grafana:
  adminPassword: algo-melhor-que-isso
```

## O que já vem pronto

Vá em `Dashboards`. Você vai encontrar uma pasta com um monte de dashboard que ninguém criou: uso de recursos por namespace, por pod, por workload, saúde do control plane, do kubelet, do próprio Prometheus. Eles vêm do projeto [kubernetes-mixin](https://github.com/kubernetes-monitoring/kubernetes-mixin) e são um bom lugar para estudar PromQL de verdade — abra um painel, clique em `Edit` e leia a consulta.

O datasource também já está lá, apontando para o Prometheus do stack. Você pode conferir em `Connections → Data sources`.

## Acrescentando os seus dashboards

Clicar na interface e salvar funciona, mas o dashboard morre junto com o pod. Existem dois jeitos de fazer isso direito.

O primeiro é pelos values, apontando para o catálogo do grafana.com:

```
grafana:
  dashboardProviders:
    dashboardproviders.yaml:
      apiVersion: 1
      providers:
        - name: curso
          folder: Curso
          type: file
          options:
            path: /var/lib/grafana/dashboards/curso
  dashboards:
    curso:
      node-exporter-full:
        gnetId: 1860        # o famoso Node Exporter Full
        revision: 41
        datasource: Prometheus
```

O segundo, e o mais usado no dia a dia, é o sidecar de dashboards, que já vem ligado. Ele fica olhando os ConfigMaps do cluster e carrega qualquer um que tenha um label específico:

```
kubectl -n monitoring create configmap meu-dashboard \
  --from-file=meu-dashboard.json

kubectl -n monitoring label configmap meu-dashboard grafana_dashboard=1
```

Em alguns segundos o dashboard aparece no Grafana. A graça disso é que o dashboard vira um manifesto como qualquer outro: entra no git, passa por review e sobe no deploy junto com a aplicação.

## Expondo em produção

Vale o mesmo do capítulo anterior: `port-forward` é para desenvolvimento. Em produção, LoadBalancer ou ingress:

```
grafana:
  grafana.ini:
    server:
      domain: monitoring.example.com
      root_url: "%(protocol)s://%(domain)s/grafana"
      serve_from_sub_path: true
  ingress:
    enabled: true
    ingressClassName: nginx
    hosts:
      - monitoring.example.com
    path: /grafana
```

E, já que vai ficar exposto: troque a senha do admin e considere plugar no login que a sua empresa já usa. O Grafana fala OAuth, SAML e LDAP.
