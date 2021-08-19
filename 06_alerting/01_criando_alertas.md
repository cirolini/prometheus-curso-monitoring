# Criando alertas

Uma das coisas que eu gosto no prometheus é que ele não foi pensado para gerar alertas, não me entenda errado, ele foi gerado para coletar, armazenar e manipular dados ou métricas e gerar estatística e insights. E com isso podemos gerar alertas. Então na verdade os alertas são uma consequência do nosso conhecimento e da nossa capacidade de ter métricas interessantes dos nossos sistemas e ai sim geramos alertas sobre elas. Vamos falar mais sobre modelos de alertas mais adiante.

Ja criamos um primeiro alerta logo que instalamos o Alertmanager para testar toda a integração. Agora vamos entender um pouco melhor o que estávamos fazendo e criar novos alertas.

O primeiro alerta que fizemos foi:

```
groups:
- name: prometheus.rules
  rules:
  - alert: Watchdog
    annotations:
      message: |
        This is an alert meant to ensure that the entire alerting pipeline is functional.
        This alert is always firing, therefore it should always be firing in Alertmanager
        and always fire against a receiver. There are integrations with various notification
        mechanisms that send a notification when this alert is not firing. For example the
        "DeadMansSnitch" integration in PagerDuty.
    expr: vector(1)
    labels:
      severity: none
```

Aqui ja temos muita coisa para entender como criar novos alertas. Primeiro os alertas são divididos por grupos, geralmente associamos por aplicação, ou por grupo de servidores. Depois vamos criar as novas regras, damos um nome para o alerta, uma descrição.

O ponto importante é a expr, que é onde vamos colocar a expressão que vai determinar se o alerta vai acontecer ou não. No proximo exemplo isso fica mais claro:

```
# Alert for any instance that is unreachable for >5 minutes.
  - alert: InstanceDown
    expr: up == 0
    for: 5m
    labels:
      severity: page
    annotations:
      summary: "Instance {{ $labels.instance }} down"
      description: "{{ $labels.instance }} of job {{ $labels.job }} has been down for more than 5 minutes."
```

Aqui criamos um alerta de instance down. Caso a métrica `up`, com qualquer conjunto de labels, vá para o valor zero por 5 minutos teremos esse alerta. Vai colocar um label de severity: page para podermos integrar com algum tipo de chamada de telefone ou email.

As annotations servem para podermos agregar mais informações no alerta, como a instance que esta acontecendo entre outros. Eu recomendo colocar também informações como runbooks, dashboards, etc.

Os labels servem para categorizar os alertas. Podemos colocar a severity, mas também poderíamos colocar o tipo de aplicação, ambiente, squad, etc. Além disso vão nos permitir agrupar alertas no Alertmanager.

Algumas expressão interessantes para podermos gerar alertas:

- expr: 100 - (avg by (instance) (rate(node_cpu_seconds_total{job="node",mode="idle"}[1m])) * 100) > 90
  Servidor com CPU disponível abaixo de 10%.
- expr: 100 - ((sum(node_filesystem_avail_bytes{app!~"ltc|pms"} * 100) by (instance, device)) / sum(node_filesystem_size_bytes{app!~"ltc|pms"}) by (instance, device)) > 90
  Uso de disco acima de 90%
- max_over_time(prometheus_config_last_reload_successful[5m]) == 0
  O prometheus não conseguiu fazer o reload com sucesso.

Enfim, as expressões aqui podem ser as mesmas que usamos para gerar gráficos e estatísticas, somente precisam de alguma forma um indicador booleano para quando atingido o prometheus possa saber que tem que gerar o alerta.
