# Lab do curso

Aqui mora o ambiente pronto do curso. A ideia é simples: você não deveria gastar a primeira hora do curso instalando coisa. Sobe tudo com um comando, e as lições de instalação manual continuam ali para quando você quiser entender o que está acontecendo por baixo.

## Subindo

Na raiz do repositório:

```
make up
```

Isso levanta o ambiente inteiro. Quando terminar:

| Serviço | URL | Observação |
|---|---|---|
| Prometheus | http://localhost:9090 | |
| Alertmanager | http://localhost:9093 | |
| Grafana | http://localhost:3000 | `admin` / `admin`, datasource e dashboard já provisionados |
| App de exemplo | http://localhost:5000 | o exporter do módulo 05; tem `/metrics` e `/erro` |
| Pushgateway | http://localhost:9091 | |
| cAdvisor | http://localhost:8080 | |
| node_exporter | http://localhost:9100/metrics | |
| blackbox_exporter | http://localhost:9115 | |

Para derrubar e limpar os volumes:

```
make down
```

Outros atalhos: `make ps`, `make logs`, `make reload` (recarrega a config do Prometheus sem reiniciar) e `make validate` (roda `promtool check config` e `amtool check-config`).

## O que está rodando

As versões estão pinadas no arquivo [`.env`](.env). Nada de `:latest` — um curso que quebra sozinho porque uma imagem mudou não serve para ninguém.

| Componente | Versão | Verificada em |
|---|---|---|
| Prometheus | `v3.14.0` | 19/09/2026 |
| Alertmanager | `v0.34.1` | 19/09/2026 |
| Grafana | `13.2.2` | 19/09/2026 |
| node_exporter | `v1.12.1` | 19/09/2026 |
| blackbox_exporter | `v0.28.0` | 19/09/2026 |
| pushgateway | `v1.11.3` | 19/09/2026 |
| cAdvisor | `v0.55.1` | 19/09/2026 |

> Sobre o cAdvisor: o release dele no GitHub já está na `v0.60.6`, mas a imagem publicada em `gcr.io` para na `v0.55.1`. Usamos a mais nova que existe de verdade no registry. Se você tentar `v0.60.6`, o pull falha.

## Detalhes que valem a pena olhar

Três coisas no lab existem para resolver pegadinhas que aparecem nas lições:

**As flags do Prometheus.** O `docker-compose.yml` sobe o Prometheus com `--web.enable-lifecycle` e `--web.enable-admin-api`. Sem a primeira, o `POST /-/reload` do módulo 08 responde `Lifecycle API is not enabled.`. Sem a segunda, o `delete_series` do módulo 04 responde `admin APIs disabled`. Em produção, pense bem antes de habilitar a segunda.

**A retenção.** Em [`prometheus/prometheus.yml`](prometheus/prometheus.yml) ela está em `storage.tsdb.retention.time`, dentro do arquivo de configuração — e não na flag `--storage.tsdb.retention.time`, que ficou *deprecated* no Prometheus 3. A vantagem de estar na config é que dá para mudar com um reload, sem reiniciar o serviço.

**Os `matchers` do Alertmanager.** Em [`alertmanager/alertmanager.yml`](alertmanager/alertmanager.yml) as rotas usam `matchers:`. O `match:` que aparece em tutoriais antigos está *deprecated* desde o Alertmanager 0.22.

## Kubernetes

```
make k8s
```

Cria um cluster [kind](https://kind.sigs.k8s.io/) chamado `curso-prometheus` e instala o **kube-prometheus-stack** nele. Depois:

```
make k8s-forward     # Grafana em http://localhost:3000 (admin / prom-operator)
make k8s-down        # apaga o cluster
```

| Componente | Versão | Verificada em |
|---|---|---|
| kind | `0.33.0` | 19/09/2026 |
| imagem do node | `kindest/node:v1.37.0` | 19/09/2026 |
| chart kube-prometheus-stack | `91.4.1` (app `v0.94.0`) | 19/09/2026 |
| kubectl | `1.37.0` | 19/09/2026 |
| helm | `4.3.0` | 19/09/2026 |

O [values](k8s/kube-prometheus-stack-values.yaml) é de propósito curto. O `values.yaml` completo do chart passa de cinco mil linhas; ali ficam só as chaves que o curso mexe. Para ver tudo:

```
helm show values prometheus-community/kube-prometheus-stack
```

Duas coisas nele merecem atenção. A primeira é o bloco de `...SelectorNilUsesHelmValues: false`: por padrão o operator só enxerga `ServiceMonitor` e `PrometheusRule` que carreguem o label do próprio release, e essas linhas mandam ele enxergar tudo no cluster. É o que você quer num lab, e provavelmente não é o que você quer em produção. A segunda é que `kubeControllerManager`, `kubeScheduler`, `kubeProxy` e `kubeEtcd` estão desligados — num cluster kind eles não são acessíveis, e deixá-los ligados só rende target vermelho sem motivo.

## Se der problema

A porta já está em uso? `make down` e tente de novo — provavelmente sobrou container de uma execução anterior.

O cAdvisor não sobe no macOS? Ele precisa ler `/var/lib/docker`, que no Docker Desktop mora dentro da VM e não no seu disco. Com [colima](https://github.com/abiosoft/colima) funciona, porque o bind é resolvido dentro da própria VM Linux.

O `make k8s` falha por falta de memória? O kube-prometheus-stack não cabe confortavelmente em menos de 4 GB. Se você usa colima, suba a VM com mais folga: `colima start --cpu 4 --memory 8`.
