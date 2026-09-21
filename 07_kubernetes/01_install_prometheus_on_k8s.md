# Instalando o Prometheus no Kubernetes

O Prometheus foi lançado antes do Kubernetes, mas a facilidades do autodiscovery do prometheus e a necessidade de monitoração crescente de serviços efêmeros que não se encaixavam bem nos sistemas de monitoração mais tradicionais, o prometheus acabou ganhando um bom espaço e hoje é o modo mais comum de monitoramos sistemas no Kubernetes.

> **O que mudou nesta edição.** Até 2021 este módulo instalava o chart `prometheus-community/prometheus` e, ao lado dele, o `grafana/grafana`. Hoje o caminho padrão é o **kube-prometheus-stack**, que traz Prometheus, Alertmanager, Grafana, node_exporter e kube-state-metrics já integrados, e opera tudo através do **Prometheus Operator**. A diferença prática é grande e vale entender antes de seguir: com o operator você para de editar arquivo de configuração e passa a criar objetos do Kubernetes. Os values da edição antiga continuam no repositório, em [`legacy/`](legacy/).
>
> Se você só quer o ambiente de pé para acompanhar as aulas, tem atalho: `make k8s` na raiz do repositório faz tudo que está escrito abaixo.

## Instalando o kind

Primeiro de tudo vc precisa de um cluster de Kubernetes para poder instalar a stack, não vamos fazer diretamente em produção, vamos fazer localmente no nosso computador, antigamente eu usava o minikube para isso, uma instalação all in one do Kubernetes que permitia você testar as coisas localmente. Atualmente eu tenho usado o kind, que cria um cluster de Kubernetes usando o docker local do teu computador, deixando assim as coisas um pouco mais leves.

Como eu uso o MAC a instalação do kind é bem simples:

```
brew install kind kubectl helm
```

Em Linux e Windows, a [página de instalação do kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation) tem o binário para cada sistema.

Depois de tudo instalado temos que criar o nosso cluster de Kubernetes:

```
$ kind create cluster --name curso-prometheus

Creating cluster "curso-prometheus" ...
 ✓ Ensuring node image (kindest/node:v1.37.0) 🖼
 ✓ Preparing nodes 📦
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹️
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
Set kubectl context to "kind-curso-prometheus"
```

Um detalhe que economiza dor de cabeça: **cada versão do kind só publica imagens de node para um punhado de versões do Kubernetes.** Se você fixar uma imagem (`kindest/node:v1.37.0`, por exemplo) e depois atualizar o kind, confira nas release notes dele se aquela imagem ainda existe. Tentar subir uma combinação que não existe é o erro mais comum aqui.

Depois de alguns minutos o cluster é criado e vc ja pode acessar as informações básicas do cluster: `kubectl cluster-info --context kind-curso-prometheus`

## Instalando o helm

A forma de instalação mais simples de aplicações no kubernetes é utilizando o helm. O helm é um gerenciador de pacotes para o Kubernetes. Ele facilita a instalação de aplicações abstraindo as complexidades da criação de deployments, services, pods, configmap entre as outras abstrações do Kubernetes.

Se você não instalou junto com o kind ali em cima:

```
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
```

## Instalando o kube-prometheus-stack

Primeiro adicionamos o repositório:

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

E instalamos. Repare que estamos passando um arquivo de values — já volto nele:

```
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --values labs/k8s/kube-prometheus-stack-values.yaml \
  --wait --timeout 15m
```

O `--wait` faz o helm segurar até tudo estar de pé, o que é mais honesto do que ele voltar na hora e você descobrir depois que metade não subiu.

Acompanhando os pods:

```
$ kubectl -n monitoring get pods
NAME                                                   READY   STATUS    RESTARTS   AGE
alertmanager-monitoring-alertmanager-0                 2/2     Running   0          2m
monitoring-grafana-684b9b87fd-mw2s7                    3/3     Running   0          2m
monitoring-kube-state-metrics-78fd56fc4b-q458r         1/1     Running   0          2m
monitoring-operator-7b47656db8-lwq8b                   1/1     Running   0          2m
monitoring-prometheus-node-exporter-hjwgt              1/1     Running   0          2m
prometheus-monitoring-prometheus-0                     2/2     Running   0          2m
```

Seis pods e você já tem a stack inteira. Compare com a edição antiga, onde Prometheus e Grafana eram duas instalações separadas que você tinha que conectar na mão.

## O que o operator mudou

Aqui está a parte conceitual que importa mais do que os comandos.

No Prometheus que instalamos no Linux, tudo vivia no `prometheus.yml`: os jobs, os alertas, o endereço do Alertmanager. Com o Prometheus Operator, esse arquivo deixa de ser escrito por você — ele é **gerado** a partir de objetos do Kubernetes:

| O que você quer | No Linux | Com o operator |
|---|---|---|
| Coletar de uma aplicação | um `scrape_config` no `prometheus.yml` | um objeto `ServiceMonitor` ou `PodMonitor` |
| Criar um alerta | um arquivo em `rule_files` | um objeto `PrometheusRule` |
| Configurar o Prometheus | flags e `prometheus.yml` | um objeto `Prometheus` |
| Configurar o Alertmanager | `alertmanager.yml` | um objeto `Alertmanager` / `AlertmanagerConfig` |

Dá para ver todos eles:

```
kubectl -n monitoring get prometheus,alertmanager,servicemonitor,prometheusrule
```

A vantagem é que a monitoração passa a ser versionada e aplicada como qualquer outro manifesto do cluster. A aplicação declara que quer ser monitorada, e ninguém precisa editar a configuração central.

## Os values

O `values.yaml` completo do kube-prometheus-stack passa de cinco mil linhas. Você não precisa lidar com isso — para ver tudo que existe:

```
helm show values prometheus-community/kube-prometheus-stack > values-completo.yaml
```

Na prática você mexe em poucas chaves. O [values do lab](../labs/k8s/kube-prometheus-stack-values.yaml) tem cerca de cem linhas e já cobre o curso. Duas coisas nele merecem explicação.

A primeira:

```
prometheus:
  prometheusSpec:
    serviceMonitorSelectorNilUsesHelmValues: false
    podMonitorSelectorNilUsesHelmValues: false
    ruleSelectorNilUsesHelmValues: false
```

Por padrão o operator **só enxerga** `ServiceMonitor` e `PrometheusRule` que tenham o label do próprio release do helm. Isso evita que um objeto perdido em outro namespace comece a ser coletado sem ninguém saber. Essas linhas desligam essa proteção e mandam ele enxergar tudo no cluster — o que é bom num lab e é uma decisão que merece pensamento em produção.

A segunda:

```
kubeControllerManager:
  enabled: false
kubeScheduler:
  enabled: false
kubeProxy:
  enabled: false
kubeEtcd:
  enabled: false
```

Num cluster kind esses componentes não expõem métricas de forma acessível. Deixar ligado só rende target vermelho no Prometheus sem nada de errado acontecendo, o que ensina a péssima lição de ignorar target vermelho. Num cluster de verdade, ligue.

Para alterar qualquer coisa, edite o arquivo e:

```
helm upgrade monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values labs/k8s/kube-prometheus-stack-values.yaml
```

## Acessando

Em desenvolvimento, `port-forward` resolve. Repare na porta de cada serviço, que é a pegadinha clássica:

```
kubectl -n monitoring port-forward svc/monitoring-prometheus 9090:9090
kubectl -n monitoring port-forward svc/monitoring-alertmanager 9093:9093
kubectl -n monitoring port-forward svc/monitoring-grafana 3000:80
```

O Alertmanager é 9093, não 9090. O Grafana é 3000 no seu lado e **80** no service.

### Em produção

Claro que o acesso em produção não funciona usando port-forward, e precisamos ter acesso externo as mesmas URLS. Cada cloud provider tem o seu jeito, e se você tem um cluster em baremetal tem outras formas.

A maneira mais comum é um service do tipo LoadBalancer, que faz o provedor liberar um IP externo:

```
grafana:
  service:
    type: LoadBalancer
```

Ou um ingress, que te dá uma URL única:

```
grafana:
  ingress:
    enabled: true
    ingressClassName: nginx
    hosts:
      - monitoring.example.com
```

Sobre armazenamento: em produção use um volume persistente de verdade. Por padrão o Prometheus do lab guarda em `emptyDir`, que evapora quando o pod morre.

```
prometheus:
  prometheusSpec:
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: gp3          # na AWS, um volume EBS
          accessModes: ["ReadWriteOnce"]
          resources:
            requests:
              storage: 50Gi
```

Na AWS o volume é **EBS** (Elastic Block Store). Não confunda com ELB, que é o load balancer — são coisas diferentes e o nome é parecido o suficiente para confundir.

## Concluindo

Com uma instalação você já tem Prometheus, Alertmanager, Grafana, node_exporter e kube-state-metrics conversando entre si, e o cluster inteiro sendo monitorado desde o primeiro minuto. No próximo passo vamos olhar o Grafana que veio junto.
