# Values da edição antiga (chart `prometheus-community/prometheus`)

Estes arquivos são da versão 2021 do curso, quando o módulo de Kubernetes usava o chart `prometheus-community/prometheus` e o `grafana/grafana` separado. A edição 2026 passou a usar o **kube-prometheus-stack**, que é o que a comunidade usa hoje, e os values novos estão em [`labs/k8s/`](../../labs/k8s/).

Ficaram aqui por dois motivos: quem tem um cluster rodando com o chart antigo ainda precisa deles, e eles são um registro útil de como era.

**Não use como referência para uma instalação nova.** As versões estão congeladas em 2021:

| Arquivo | O que tem dentro |
|---|---|
| `prometheus/values.yml` | dump completo do chart, 1734 linhas — Prometheus `v2.26.0`, Alertmanager `v0.21.0` |
| `prometheus/values_simple.yml` | o mesmo sem comentários — Prometheus `v2.24.0` |
| `prometheus/alerting-kubernetes.yml` | alertas de Kubernetes no formato `serverFiles` do chart antigo |
| `prometheus/alerting-codex.yml` | alertas do Prometheus. **Este arquivo está quebrado**: usa as variáveis `{{ $prometheusJob }}` e `{{ $namespace }}`, que não existem em lugar nenhum do chart. O `helm upgrade` falha com "undefined variable". É sobra de um copy/paste do kube-prometheus |
| `grafana/values.yml` | dump do chart do Grafana — imagem `7.4.5` |

No kube-prometheus-stack os alertas não vivem mais em `serverFiles`: eles viram objetos `PrometheusRule` do Kubernetes. A lição [Alertas no Kubernetes](../03_alerting_k8s.md) mostra como fica.
