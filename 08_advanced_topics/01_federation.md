# Federation

O Federation é uma forma de permitir múltiplos servidores de Prometheus coletarem dados selecionados uns dos outros. Existem muitos casos de uso para isso, pode ser que você tenha múltiplos datacenters e quer poder ter um Prometheus em cada datacenter mas quer fazer as consultas de forma agregada com todos os dados. Pode ser uma forma também de ter múltiplas instancias com perfil de maquinas diferentes, coletando informações de serviços diferentes com tempo de armazenamento diferentes, e em algum ponto querer agregar certas informações por mais tempo.

Dito isso a configuração do federation é muito simples, basta criarmos um novo job para scrape e colocar o endereço de outro prometheus com o path `/federate`.

Se você não pretende ter problemas de espaço em disco em breve, recomendo filtrar bem a parte do match, somente para buscar as métricas realmente necessárias no federation. Segue um exemplo abaixo de como configurar o federation, e também como configurar os filtros de coleta através do parâmetro `match[]`.

```
scrape_configs:
  - job_name: 'federate'
    scrape_interval: 15s

    honor_labels: true
    metrics_path: '/federate'

    params:
      'match[]':
        - '{job="prometheus"}'
        - '{__name__=~"job:.*"}'

    static_configs:
      - targets:
        - 'source-prometheus-1:9090'
        - 'source-prometheus-2:9090'
        - 'source-prometheus-3:9090'
```

Cuidado também com o crescimento do cluster, o federation pode começar a ser bem custoso em termos de performance para o cluster. Eu realmente recomendo o uso dele com cuidado e somente para o necessário.

Vale saber que hoje o federation não é mais a única resposta para "quero ver tudo num lugar só". Quando o objetivo é visão global de verdade, com retenção longa, o caminho mais comum passou a ser `remote_write` mandando os dados para algo feito para isso — Thanos, Mimir ou Cortex. O federation continua ótimo para o que ele sempre foi bom: puxar um punhado de métricas agregadas de um Prometheus para outro. Ele vira problema quando alguém tenta usar como replicação.
