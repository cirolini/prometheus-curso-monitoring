# Alertando no k8s

Precisamos também criar as monitorações no prometheus, mas como todo o sistema gerenciado pelo helm, as alterações são feitas por eles. Recomendo que se vc tem um time trabalhando nos alertas que esse processo fique em algum tipo de sistema de controle de versão como o github ou gitlab, e melhor ainda seria integrar um sistema automatizado para atualizar a partir de alterações.

Vamos aplicar as configurações através do do helm, e os arquivos de configuração. Vamos alterar os valores padrões para reconhecer mais um arquivo de regras, o alerting-kubernetes alem de alterar o arquivo padrão de monitoração para mais alguns alertas do próprio prometheus.

Nesse projeto ja temos alguns arquivos de exemplos de alertas que podem ser usados para esse tutorial.

```
helm upgrade prometheus prometheus-community/prometheus -f prometheus/values.yml -f prometheus/alerting-kubernetes.yml -f prometheus/alerting-codex.yml
```

Caso o reload automático não identifique todos os tópicos podemos forçar:

```
curl http://localhost:9090/-/reload
```

Depois disso navegar pelo prometheus e ver os alertas na pagina de alertas.

![PrometheusAlerting](/07_kubernetes/images/prometheus_alerting.png "PrometheusAlerting")
