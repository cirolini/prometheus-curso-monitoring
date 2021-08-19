# Instalando o Prometheus no Kubernetes

O Prometheus foi lançado antes do Kubernetes, mas a facilidades do autodiscovery do prometheus e a necessidade de monitoração crescente de serviços efêmeros que não se encaixavam bem nos sistemas de monitoração mais tradicionais, o prometheus acabou ganhando um bom espaço e hoje é o modo mais comum de monitoramos sistemas no Kubernetes.

## instalando o kind

Primeiro de tudo vc precisa de um cluster de Kubernetes para poder instalar a stack, não vamos fazer diretamente em produção, vamos fazer localmente no nosso computador, antigamente eu usava o minikube para isso, uma instalação all in one do Kubernetes que permitia você testar as coisas localmente. Atualmente eu tenho usado o kind, que cria um cluster de Kubernetes usando o docker local do teu computador, deixando assim as coisas um pouco mais leves.

Como eu uso o MAC a instalação do kind é bem simples:

```
brew install kind
```

Se você usa windows pode fazer o download do binário pronto tbm aqui: `https://kind.sigs.k8s.io/dl/v0.10.0/kind-windows-amd64`

Depois de tudo instalado temos que criar o nosso cluster de Kubernetes:

```
$ kind create cluster

Creating cluster "kind" ...
 ✓ Ensuring node image (kindest/node:v1.21.1) 🖼
 ✓ Preparing nodes 📦
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹️
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
Set kubectl context to "kind-kind"
You can now use your cluster with:

kubectl cluster-info --context kind-kind

Not sure what to do next? 😅  Check out https://kind.sigs.k8s.io/docs/user/quick-start/
```

Depois de alguns minutos o cluster é criado e vc ja pode acessar as informações básicas do cluster aqui: `kubectl cluster-info --context kind-kind`

## Instalando o helm

A forma de instalação mais simples de aplicações no kubernetes é utilizando o helm. O helm é um gerenciador de pacotes para o Kubernetes. Ele facilita a instalação de aplicações abstraindo as complexidades da criação de deployments, services, pods, configmap entre as outras abstrações do Kubernetes.

Para instalar o helm é bem simples, basta no terminar escrever:

```
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 | bash
```

Depois de alguns minutos ja vamos ter o helm instalado e podemos começar a instalar o prometheus e o restante do que precisamos.

## Instalando o Prometheus

Primeiro precisamos adicionar o repositório do prometheus ao nosso helm:

```
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

Agora ja estamos prontos para instalar o Prometheus no nosso Kubernetes. Para isso vamos escolher um release name e rodar o seguinte comando:

```
helm install [RELEASE_NAME] prometheus-community/prometheus
````

Podemos acompanhar os pods serem criados através do comando: `kubectl get pods --watch`, vai vir algo como abaixo:

```
rc@mac ~ % kubectl get pods
NAME                                               READY   STATUS              RESTARTS   AGE
my-prometheus-alertmanager-d59dcdb9f-8mnpg         0/2     ContainerCreating   0          15s
my-prometheus-kube-state-metrics-5bd9dfbf9-dz7sb   0/1     ContainerCreating   0          15s
my-prometheus-node-exporter-2xhqh                  0/1     ContainerCreating   0          15s
my-prometheus-pushgateway-56f75856f6-8w899         0/1     Running             0          15s
my-prometheus-server-74946dd7b-n9kxw               0/2     ContainerCreating   0          15s
```

Com isso ja funcionando podemos acessar o nosso prometheus por: `kubectl port-forward prometheus-server-7fdf57f659-zds7p 9090` e também o alertmanager por: `kubectl port-forward prometheus-alertmanager-8697d479dd-8lxk4 9090`.

Podemos ainda especionar as configurações:

```
kubectl get cm
kubectl describe cm prometheus-server
kubectl describe cm prometheus-alertmanager
```

Não é adequado editar as configurações da aplicação manualmente via kubectl, o helm possui uma série de opções e formas de editar as configurações e ainda sim manter a consistência do prometheus, mantendo assim a facilidade de atualização/reinstalação quando necessário.

```
helm show values prometheus-community/prometheus
helm show values prometheus-community/prometheus >> values.yml
```

Para ter uma versão sem os comentários dos valores: `grep -v '^\s*$\|^\s*\#' values.yml  >> values_simple.yml`

Agora para editarmos algum valor podemos editar o arquivo values.yml e realizar um upgrade:

```
helm upgrade -f values.yml prometheus prometheus-community/prometheus
```

O arquivo ainda pode ser quebrado em múltiplos arquivos para facilitar a manutenção. E todos eles podem ser adicionados com o `-f`.

Se estiver usando um prometheus em produção o que eu recomendo é que vc use um persistent volume externo, algo como um ELB na AWS, para que os dados fiquem acessíveis externamente ao Kubernetes e não ocupando o espaço em disco dos nodos. Se você tem um cluster de kubernetes privado, pode usar um volume como NFS ou algo semelhante.

### Expondo os serviços externamente

Claro que o acesso em produção não funciona usando port-forward, e precisamos ter acesso externo as mesmas URLS. Claro que cada cloud provider como a AWS ou GCP tem o seu próprio jeito de fazer isso, e se você ainda tem um cluster em baremetal tem outras formas.

A maneira mais comum é ativando um service do tipo loadbalancer, isso vai fazer com que o teu provedor de acesso libere um IP externo para que você possa acessar os serviços. Fazemos a configuração dos mesmos alterando as configurações do helm e aplicando novamente.

Para trocar o alertmanager e o prometheus para o tipo loadbancer você precisa alterar as seguintes configurações no value.yaml

```
alertmanager:
  service:
    type: LoadBalancer

server:
  service:
    type: LoadBalancer
```

Também é possível habilitar um ingress através do arquivo de valores. O ingress vai te dar uma url/ip único para acesso aos serviços do Kubernetes.

```
alertmanager:
  ingress:
    ## If true, alertmanager Ingress will be created
    ##
    enabled: false

    ## Alertmanager server Ingress annotations
    ##
    annotations: {}
    #   kubernetes.io/ingress.class: nginx
    #   kubernetes.io/tls-acme: 'true'

    hosts: []
    #   - alertmanager.domain.com
    #   - domain.com/alertmanager

server:
  ingress:
    ## If true, Prometheus server Ingress will be created
    ##
    enabled: false

    ## Prometheus server Ingress annotations
    ##
    annotations: {}
    #   kubernetes.io/ingress.class: nginx
    #   kubernetes.io/tls-acme: 'true'

    hosts: []
    #   - prometheus.domain.com
    #   - domain.com/prometheus
```

## Concluindo

Essa instalação do Prometheus ja vai vir com o Prometheus server, o alertmanager, node_exporter, pushgateway e o kube state metrics. Então ja tem tudo que precisa para monitorar o seu cluster do Kubernetes e as demais aplicações que vamos usar e instalar no Prometheus.
